"""
Management command to sync Medium articles from @mathurasa98 profile.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from blog.services import MediumService

User = get_user_model()


class Command(BaseCommand):
    help = 'Sync Medium articles from @mathurasa98 profile to local blog'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username of the user to assign articles to',
            default='admin'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force sync even if articles already exist'
        )
    
    def handle(self, *args, **options):
        username = options['username']
        force = options['force']
        
        try:
            # Get or create user
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@inspora.com',
                    'first_name': username.title(),
                    'is_staff': True,
                    'is_superuser': True
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created user: {username}')
                )
            
            # Initialize Medium service
            medium_service = MediumService()
            
            self.stdout.write('Fetching Medium articles...')
            articles = medium_service.fetch_medium_articles()
            
            if not articles:
                self.stdout.write(
                    self.style.WARNING('No articles found or error occurred')
                )
                return
            
            self.stdout.write(f'Found {len(articles)} articles')
            
            # Sync articles
            synced_count = medium_service.sync_medium_articles(user)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully synced {synced_count} articles from Medium'
                )
            )
            
            # Display synced articles
            for article in articles[:5]:  # Show first 5
                self.stdout.write(
                    f'  - {article["title"]} ({article["source"]})'
                )
            
            if len(articles) > 5:
                self.stdout.write(f'  ... and {len(articles) - 5} more')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error syncing Medium articles: {e}')
            )
