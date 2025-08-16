"""
Management command to test profile picture functionality.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
import os

User = get_user_model()


class Command(BaseCommand):
    help = 'Test profile picture functionality by creating sample avatars'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username to test with'
        )
        parser.add_argument(
            '--create-sample',
            action='store_true',
            help='Create a sample avatar file for testing'
        )

    def handle(self, *args, **options):
        username = options['username']
        create_sample = options['create_sample']

        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'User "{username}" not found')
                )
                return
        else:
            # Get the first user if no username specified
            user = User.objects.first()
            if not user:
                self.stdout.write(
                    self.style.ERROR('No users found in the system')
                )
                return

        self.stdout.write(
            self.style.SUCCESS(f'Testing profile picture functionality for user "{user.username}"')
        )

        # Check current avatar status
        if user.avatar:
            self.stdout.write(f'  ✓ User has avatar: {user.avatar.name}')
            self.stdout.write(f'  ✓ Avatar URL: {user.avatar.url}')
            self.stdout.write(f'  ✓ Avatar size: {user.avatar.size} bytes')
        else:
            self.stdout.write('  ⚠ User has no avatar set')

        # Check avatar field configuration
        avatar_field = User._meta.get_field('avatar')
        self.stdout.write(f'  ✓ Avatar field upload_to: {avatar_field.upload_to}')
        self.stdout.write(f'  ✓ Avatar field null: {avatar_field.null}')
        self.stdout.write(f'  ✓ Avatar field blank: {avatar_field.blank}')

        # Check media settings
        self.stdout.write(f'  ✓ MEDIA_URL: {getattr(settings, "MEDIA_URL", "Not set")}')
        self.stdout.write(f'  ✓ MEDIA_ROOT: {getattr(settings, "MEDIA_ROOT", "Not set")}')

        # Check if media directory exists
        media_root = getattr(settings, 'MEDIA_ROOT', None)
        if media_root:
            if os.path.exists(media_root):
                self.stdout.write(f'  ✓ MEDIA_ROOT directory exists: {media_root}')
                
                # Check avatars subdirectory
                avatars_dir = os.path.join(media_root, 'avatars')
                if os.path.exists(avatars_dir):
                    self.stdout.write(f'  ✓ Avatars directory exists: {avatars_dir}')
                    
                    # List avatar files
                    avatar_files = [f for f in os.listdir(avatars_dir) if f.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))]
                    if avatar_files:
                        self.stdout.write(f'  ✓ Found {len(avatar_files)} avatar files:')
                        for file in avatar_files[:5]:  # Show first 5
                            file_path = os.path.join(avatars_dir, file)
                            file_size = os.path.getsize(file_path)
                            self.stdout.write(f'    - {file} ({file_size} bytes)')
                        if len(avatar_files) > 5:
                            self.stdout.write(f'    ... and {len(avatar_files) - 5} more')
                    else:
                        self.stdout.write('  ⚠ No avatar files found in avatars directory')
                else:
                    self.stdout.write(f'  ⚠ Avatars directory does not exist: {avatars_dir}')
            else:
                self.stdout.write(f'  ⚠ MEDIA_ROOT directory does not exist: {media_root}')

        # Test avatar URL generation
        if user.avatar:
            try:
                # Test if avatar URL is accessible
                avatar_path = user.avatar.path
                if os.path.exists(avatar_path):
                    self.stdout.write(f'  ✓ Avatar file exists on disk: {avatar_path}')
                else:
                    self.stdout.write(f'  ⚠ Avatar file missing on disk: {avatar_path}')
            except Exception as e:
                self.stdout.write(f'  ⚠ Error checking avatar file: {e}')

        # Test user methods
        try:
            full_name = user.get_full_name_or_username()
            self.stdout.write(f'  ✓ get_full_name_or_username(): {full_name}')
        except Exception as e:
            self.stdout.write(f'  ⚠ Error calling get_full_name_or_username(): {e}')

        # Test profile URLs
        try:
            from django.urls import reverse
            profile_url = reverse('accounts:profile')
            self.stdout.write(f'  ✓ Profile URL: {profile_url}')
            
            profile_edit_url = reverse('accounts:profile_edit')
            self.stdout.write(f'  ✓ Profile Edit URL: {profile_edit_url}')
            
            profile_picture_url = reverse('accounts:profile_picture_settings')
            self.stdout.write(f'  ✓ Profile Picture Settings URL: {profile_picture_url}')
            
        except Exception as e:
            self.stdout.write(f'  ⚠ Error generating profile URLs: {e}')

        # Create sample avatar if requested
        if create_sample:
            self.stdout.write('\nCreating sample avatar file...')
            try:
                # Create a simple test image (1x1 pixel PNG)
                sample_image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xf6\x178\xea\x00\x00\x00\x00IEND\xaeB`\x82'
                
                # Create sample avatar file
                sample_avatar = SimpleUploadedFile(
                    'sample_avatar.png',
                    sample_image_data,
                    content_type='image/png'
                )
                
                # Save to user
                user.avatar.save('sample_avatar.png', sample_avatar, save=True)
                
                self.stdout.write(
                    self.style.SUCCESS('  ✓ Sample avatar created successfully!')
                )
                self.stdout.write(f'  ✓ New avatar path: {user.avatar.path}')
                self.stdout.write(f'  ✓ New avatar URL: {user.avatar.url}')
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  ⚠ Error creating sample avatar: {e}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\nProfile picture test completed for user "{user.username}"')
        )

        # Recommendations
        self.stdout.write('\nRecommendations:')
        if not user.avatar:
            self.stdout.write('  • User should upload a profile picture')
        if not os.path.exists(getattr(settings, 'MEDIA_ROOT', '')):
            self.stdout.write('  • MEDIA_ROOT should be configured in settings')
        if not getattr(settings, 'MEDIA_URL', ''):
            self.stdout.write('  • MEDIA_URL should be configured in settings')
        
        self.stdout.write('  • Test the profile picture upload interface at /profile/picture/')
        self.stdout.write('  • Test the profile edit form at /profile/edit/')

