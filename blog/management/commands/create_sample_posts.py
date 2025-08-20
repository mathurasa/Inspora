"""
Management command to create sample blog posts for Inspora.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from blog.models import BlogPost, Category, Tag
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample blog posts for Inspora blog'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username of the user to assign posts to',
            default='admin'
        )
        parser.add_argument(
            '--count',
            type=int,
            help='Number of sample posts to create',
            default=15
        )
    
    def handle(self, *args, **options):
        username = options['username']
        count = options['count']
        
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
            
            # Create categories
            categories = self._create_categories()
            
            # Create tags
            tags = self._create_tags()
            
            # Create sample posts
            posts_created = self._create_sample_posts(user, categories, tags, count)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created {posts_created} sample blog posts'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating sample posts: {e}')
            )
    
    def _create_categories(self):
        """Create blog categories."""
        categories_data = [
            {
                'name': 'Technology',
                'description': 'Latest technology trends and insights',
                'slug': 'technology'
            },
            {
                'name': 'Project Management',
                'description': 'Best practices in project management',
                'slug': 'project-management'
            },
            {
                'name': 'Productivity',
                'description': 'Tips and tricks for better productivity',
                'slug': 'productivity'
            },
            {
                'name': 'Leadership',
                'description': 'Leadership insights and strategies',
                'slug': 'leadership'
            },
            {
                'name': 'Innovation',
                'description': 'Innovation in business and technology',
                'slug': 'innovation'
            },
            {
                'name': 'Medium Articles',
                'description': 'Articles imported from Medium',
                'slug': 'medium-articles'
            }
        ]
        
        categories = {}
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            categories[cat_data['name']] = category
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        return categories
    
    def _create_tags(self):
        """Create blog tags."""
        tags_data = [
            'Django', 'Python', 'Web Development', 'API', 'Database',
            'Agile', 'Scrum', 'Kanban', 'Team Management', 'Remote Work',
            'Productivity', 'Time Management', 'Leadership', 'Innovation',
            'Startup', 'Business', 'Technology', 'AI', 'Machine Learning',
            'Cloud Computing', 'DevOps', 'Cybersecurity', 'Data Science'
        ]
        
        tags = {}
        for tag_name in tags_data:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            tags[tag_name] = tag
            if created:
                self.stdout.write(f'Created tag: {tag.name}')
        
        return tags
    
    def _create_sample_posts(self, user, categories, tags, count):
        """Create sample blog posts."""
        sample_posts = [
            {
                'title': 'Getting Started with Django: A Complete Guide',
                'excerpt': 'Learn the fundamentals of Django web framework and build your first web application from scratch.',
                'content': self._get_django_post_content(),
                'category': categories['Technology'],
                'tags': ['Django', 'Python', 'Web Development'],
                'is_featured': True,
                'status': 'published'
            },
            {
                'title': '10 Project Management Best Practices for 2024',
                'excerpt': 'Discover the most effective project management strategies that will help your team succeed in the modern workplace.',
                'content': self._get_project_management_content(),
                'category': categories['Project Management'],
                'tags': ['Project Management', 'Agile', 'Team Management'],
                'is_featured': True,
                'status': 'published'
            },
            {
                'title': 'The Future of Remote Work: Trends and Predictions',
                'excerpt': 'Explore how remote work is evolving and what the future holds for distributed teams.',
                'content': self._get_remote_work_content(),
                'category': categories['Productivity'],
                'tags': ['Remote Work', 'Productivity', 'Team Management'],
                'is_featured': False,
                'status': 'published'
            },
            {
                'title': 'Building Scalable APIs with Django REST Framework',
                'excerpt': 'Learn how to create robust and scalable APIs using Django REST Framework for your web applications.',
                'content': self._get_api_content(),
                'category': categories['Technology'],
                'tags': ['Django', 'API', 'Web Development'],
                'is_featured': False,
                'status': 'published'
            },
            {
                'title': 'Leadership in the Digital Age: Key Skills for Success',
                'excerpt': 'Develop the essential leadership skills needed to thrive in today\'s rapidly changing digital landscape.',
                'content': self._get_leadership_content(),
                'category': categories['Leadership'],
                'tags': ['Leadership', 'Innovation', 'Business'],
                'is_featured': True,
                'status': 'published'
            },
            {
                'title': 'Agile vs Waterfall: Choosing the Right Methodology',
                'excerpt': 'Compare Agile and Waterfall methodologies to determine which approach works best for your projects.',
                'content': self._get_agile_content(),
                'category': categories['Project Management'],
                'tags': ['Agile', 'Project Management', 'Scrum'],
                'is_featured': False,
                'status': 'published'
            },
            {
                'title': 'Database Design Principles for Web Applications',
                'excerpt': 'Master the fundamentals of database design to create efficient and scalable web applications.',
                'content': self._get_database_content(),
                'category': categories['Technology'],
                'tags': ['Database', 'Web Development', 'API'],
                'is_featured': False,
                'status': 'published'
            },
            {
                'title': 'Time Management Strategies for Busy Professionals',
                'excerpt': 'Learn practical time management techniques that will help you become more productive and less stressed.',
                'content': self._get_time_management_content(),
                'category': categories['Productivity'],
                'tags': ['Time Management', 'Productivity', 'Leadership'],
                'is_featured': False,
                'status': 'published'
            },
            {
                'title': 'Innovation in Startups: From Idea to Market',
                'excerpt': 'Discover the key factors that drive innovation in successful startups and how to apply them to your business.',
                'content': self._get_innovation_content(),
                'category': categories['Innovation'],
                'tags': ['Innovation', 'Startup', 'Business'],
                'is_featured': False,
                'status': 'published'
            },
            {
                'title': 'Building High-Performing Teams: A Manager\'s Guide',
                'excerpt': 'Learn the essential strategies for building and leading high-performing teams in any organization.',
                'content': self._get_team_building_content(),
                'category': categories['Leadership'],
                'tags': ['Leadership', 'Team Management', 'Business'],
                'is_featured': False,
                'status': 'published'
            },
            {
                'title': 'DevOps Best Practices for Modern Applications',
                'excerpt': 'Implement DevOps practices to streamline your development and deployment processes.',
                'content': self._get_devops_content(),
                'category': categories['Technology'],
                'tags': ['DevOps', 'Technology', 'Cloud Computing'],
                'is_featured': False,
                'status': 'published'
            },
            {
                'title': 'The Art of Effective Communication in Business',
                'excerpt': 'Master the skills of effective communication to improve collaboration and drive better business results.',
                'content': self._get_communication_content(),
                'category': categories['Leadership'],
                'tags': ['Leadership', 'Business', 'Team Management'],
                'is_featured': False,
                'status': 'published'
            },
            {
                'title': 'Cybersecurity Essentials for Web Developers',
                'excerpt': 'Learn the fundamental security practices that every web developer should implement in their applications.',
                'content': self._get_security_content(),
                'category': categories['Technology'],
                'tags': ['Cybersecurity', 'Web Development', 'Technology'],
                'is_featured': False,
                'status': 'published'
            },
            {
                'title': 'Data-Driven Decision Making in Business',
                'excerpt': 'Learn how to use data analytics to make informed business decisions and drive growth.',
                'content': self._get_data_analytics_content(),
                'category': categories['Innovation'],
                'tags': ['Data Science', 'Business', 'Innovation'],
                'is_featured': False,
                'status': 'published'
            },
            {
                'title': 'Sustainable Business Practices for the Future',
                'excerpt': 'Discover how implementing sustainable practices can benefit your business and the environment.',
                'content': self._get_sustainability_content(),
                'category': categories['Innovation'],
                'tags': ['Innovation', 'Business', 'Sustainability'],
                'is_featured': False,
                'status': 'published'
            }
        ]
        
        posts_created = 0
        for i, post_data in enumerate(sample_posts[:count]):
            try:
                # Create post
                post = BlogPost.objects.create(
                    title=post_data['title'],
                    excerpt=post_data['excerpt'],
                    content=post_data['content'],
                    author=user,
                    category=post_data['category'],
                    status=post_data['status'],
                    is_featured=post_data['is_featured'],
                    meta_description=post_data['excerpt'][:160],
                    views=i * 10 + 50,  # Simulate some views
                    likes=i * 2 + 5      # Simulate some likes
                )
                
                # Add tags
                for tag_name in post_data['tags']:
                    if tag_name in tags:
                        post.tags.add(tags[tag_name])
                
                # Set creation date (spread over the last few months)
                days_ago = (count - i) * 3
                post.created_at = timezone.now() - timedelta(days=days_ago)
                post.save()
                
                posts_created += 1
                self.stdout.write(f'Created post: {post.title}')
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating post "{post_data["title"]}": {e}')
                )
        
        return posts_created
    
    def _get_django_post_content(self):
        return """
        <h2>Introduction to Django</h2>
        <p>Django is a high-level Python web framework that encourages rapid development and clean, pragmatic design. Built by experienced developers, it takes care of much of the hassle of web development, so you can focus on writing your app without needing to reinvent the wheel.</p>
        
        <h3>Why Choose Django?</h3>
        <ul>
            <li><strong>Rapid Development:</strong> Django's philosophy is to do things quickly and efficiently.</li>
            <li><strong>Clean Design:</strong> Django follows the DRY (Don't Repeat Yourself) principle.</li>
            <li><strong>Security:</strong> Django helps developers avoid many common security mistakes.</li>
            <li><strong>Scalability:</strong> Django can handle high-traffic websites and applications.</li>
        </ul>
        
        <h3>Getting Started</h3>
        <p>To get started with Django, you'll need to:</p>
        <ol>
            <li>Install Python (3.8 or higher)</li>
            <li>Install Django using pip</li>
            <li>Create your first project</li>
            <li>Run the development server</li>
        </ol>
        
        <h3>Basic Commands</h3>
        <pre><code>
# Create a new Django project
django-admin startproject myproject

# Navigate to the project directory
cd myproject

# Create a new app
python manage.py startapp myapp

# Run migrations
python manage.py migrate

# Start the development server
python manage.py runserver
        </code></pre>
        
        <h3>Project Structure</h3>
        <p>A typical Django project structure looks like this:</p>
        <pre><code>
myproject/
├── manage.py
├── myproject/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── myapp/
    ├── __init__.py
    ├── admin.py
    ├── models.py
    ├── views.py
    └── urls.py
        </code></pre>
        
        <h3>Next Steps</h3>
        <p>Once you have the basic structure in place, you can start building your models, views, and templates. Django provides a comprehensive admin interface out of the box, making it easy to manage your data.</p>
        """
    
    def _get_project_management_content(self):
        return """
        <h2>Project Management Best Practices</h2>
        <p>Effective project management is crucial for the success of any organization. In today's fast-paced business environment, teams need to be agile, collaborative, and results-driven.</p>
        
        <h3>1. Clear Project Goals</h3>
        <p>Every successful project starts with clearly defined goals. Use the SMART framework:</p>
        <ul>
            <li><strong>Specific:</strong> Define exactly what needs to be accomplished</li>
            <li><strong>Measurable:</strong> Establish criteria for measuring progress</li>
            <li><strong>Achievable:</strong> Ensure goals are realistic and attainable</li>
            <li><strong>Relevant:</strong> Align goals with business objectives</li>
            <li><strong>Time-bound:</strong> Set deadlines for achieving goals</li>
        </ul>
        
        <h3>2. Effective Communication</h3>
        <p>Communication is the backbone of successful project management. Establish clear communication channels and protocols:</p>
        <ul>
            <li>Regular team meetings and updates</li>
            <li>Clear documentation and reporting</li>
            <li>Open feedback channels</li>
            <li>Transparent decision-making processes</li>
        </ul>
        
        <h3>3. Risk Management</h3>
        <p>Identify potential risks early and develop mitigation strategies:</p>
        <ul>
            <li>Conduct regular risk assessments</li>
            <li>Develop contingency plans</li>
            <li>Monitor risk indicators</li>
            <li>Have backup resources ready</li>
        </ul>
        
        <h3>4. Agile Methodology</h3>
        <p>Embrace agile principles for better project outcomes:</p>
        <ul>
            <li>Iterative development cycles</li>
            <li>Regular stakeholder feedback</li>
            <li>Adaptive planning</li>
            <li>Continuous improvement</li>
        </ul>
        """
    
    def _get_remote_work_content(self):
        return """
        <h2>The Future of Remote Work</h2>
        <p>Remote work has transformed from a trend to a fundamental shift in how we work. As we look to the future, it's clear that remote and hybrid work models will continue to evolve and become more sophisticated.</p>
        
        <h3>Current Trends</h3>
        <p>The remote work landscape is constantly evolving with new technologies and methodologies:</p>
        <ul>
            <li>Advanced collaboration tools</li>
            <li>Virtual reality meeting spaces</li>
            <li>AI-powered productivity assistants</li>
            <li>Enhanced cybersecurity measures</li>
        </ul>
        
        <h3>Benefits of Remote Work</h3>
        <p>Remote work offers numerous advantages for both employees and employers:</p>
        <ul>
            <li>Increased productivity and focus</li>
            <li>Better work-life balance</li>
            <li>Reduced commuting time and costs</li>
            <li>Access to global talent pools</li>
            <li>Lower overhead costs for businesses</li>
        </ul>
        
        <h3>Challenges and Solutions</h3>
        <p>While remote work has many benefits, it also presents unique challenges:</p>
        <ul>
            <li><strong>Isolation:</strong> Regular virtual team building activities</li>
            <li><strong>Communication:</strong> Clear protocols and multiple channels</li>
            <li><strong>Work-life balance:</strong> Structured schedules and boundaries</li>
            <li><strong>Technology issues:</strong> Robust IT support and training</li>
        </ul>
        """
    
    def _get_api_content(self):
        return """
        <h2>Building Scalable APIs with Django REST Framework</h2>
        <p>Django REST Framework (DRF) is a powerful toolkit for building Web APIs. It provides a comprehensive set of tools for creating robust, scalable, and maintainable APIs.</p>
        
        <h3>Key Features</h3>
        <ul>
            <li>Serialization for complex data types</li>
            <li>Class-based views and viewsets</li>
            <li>Authentication and permissions</li>
            <li>Browsable API interface</li>
            <li>Comprehensive documentation</li>
        </ul>
        
        <h3>Best Practices</h3>
        <p>Follow these practices to build better APIs:</p>
        <ul>
            <li>Use proper HTTP status codes</li>
            <li>Implement comprehensive error handling</li>
            <li>Add authentication and authorization</li>
            <li>Include proper validation</li>
            <li>Document your API thoroughly</li>
        </ul>
        """
    
    def _get_leadership_content(self):
        return """
        <h2>Leadership in the Digital Age</h2>
        <p>Digital transformation has fundamentally changed what it means to be a leader. Today's leaders must navigate complex technological landscapes while inspiring and guiding their teams through unprecedented change.</p>
        
        <h3>Essential Leadership Skills</h3>
        <ul>
            <li><strong>Digital Literacy:</strong> Understanding technology trends</li>
            <li><strong>Adaptability:</strong> Embracing change and uncertainty</li>
            <li><strong>Emotional Intelligence:</strong> Managing relationships effectively</li>
            <li><strong>Strategic Thinking:</strong> Long-term vision and planning</li>
        </ul>
        """
    
    def _get_agile_content(self):
        return """
        <h2>Agile vs Waterfall: Choosing the Right Methodology</h2>
        <p>Selecting the right project management methodology is crucial for project success. Both Agile and Waterfall have their strengths and are suited for different types of projects.</p>
        
        <h3>Agile Methodology</h3>
        <p>Agile is iterative and flexible, perfect for projects with evolving requirements:</p>
        <ul>
            <li>Iterative development cycles</li>
            <li>Continuous stakeholder feedback</li>
            <li>Adaptive planning</li>
            <li>Rapid delivery of working software</li>
        </ul>
        """
    
    def _get_database_content(self):
        return """
        <h2>Database Design Principles for Web Applications</h2>
        <p>Good database design is fundamental to building scalable and maintainable web applications. Understanding the principles of database design will help you create efficient data structures.</p>
        
        <h3>Normalization</h3>
        <p>Database normalization helps eliminate redundancy and improve data integrity:</p>
        <ul>
            <li>First Normal Form (1NF)</li>
            <li>Second Normal Form (2NF)</li>
            <li>Third Normal Form (3NF)</li>
        </ul>
        """
    
    def _get_time_management_content(self):
        return """
        <h2>Time Management Strategies for Busy Professionals</h2>
        <p>Effective time management is essential for professional success. By implementing proven strategies, you can increase productivity and reduce stress.</p>
        
        <h3>Prioritization Techniques</h3>
        <ul>
            <li>Eisenhower Matrix</li>
            <li>Pomodoro Technique</li>
            <li>Time blocking</li>
            <li>Task batching</li>
        </ul>
        """
    
    def _get_innovation_content(self):
        return """
        <h2>Innovation in Startups: From Idea to Market</h2>
        <p>Innovation is the lifeblood of successful startups. Understanding how to foster innovation and bring ideas to market is crucial for entrepreneurial success.</p>
        
        <h3>Innovation Process</h3>
        <ul>
            <li>Idea generation and validation</li>
            <li>Market research and analysis</li>
            <li>Prototype development</li>
            <li>Customer feedback and iteration</li>
        </ul>
        """
    
    def _get_team_building_content(self):
        return """
        <h2>Building High-Performing Teams: A Manager's Guide</h2>
        <p>High-performing teams don't happen by accident. They require intentional leadership, clear communication, and a supportive culture.</p>
        
        <h3>Team Development Stages</h3>
        <ul>
            <li>Forming: Team members get to know each other</li>
            <li>Storming: Conflicts and challenges arise</li>
            <li>Norming: Team establishes working patterns</li>
            <li>Performing: Team achieves high performance</li>
        </ul>
        """
    
    def _get_devops_content(self):
        return """
        <h2>DevOps Best Practices for Modern Applications</h2>
        <p>DevOps practices help organizations deliver software faster and more reliably. Implementing DevOps requires cultural change and technical expertise.</p>
        
        <h3>Core DevOps Practices</h3>
        <ul>
            <li>Continuous Integration/Continuous Deployment</li>
            <li>Infrastructure as Code</li>
            <li>Automated testing</li>
            <li>Monitoring and logging</li>
        </ul>
        """
    
    def _get_communication_content(self):
        return """
        <h2>The Art of Effective Communication in Business</h2>
        <p>Effective communication is essential for business success. It improves collaboration, reduces misunderstandings, and drives better results.</p>
        
        <h3>Communication Skills</h3>
        <ul>
            <li>Active listening</li>
            <li>Clear and concise messaging</li>
            <li>Non-verbal communication</li>
            <li>Feedback and follow-up</li>
        </ul>
        """
    
    def _get_security_content(self):
        return """
        <h2>Cybersecurity Essentials for Web Developers</h2>
        <p>Security should be a top priority for every web developer. Understanding basic security principles helps protect users and applications.</p>
        
        <h3>Security Best Practices</h3>
        <ul>
            <li>Input validation and sanitization</li>
            <li>Authentication and authorization</li>
            <li>Data encryption</li>
            <li>Regular security updates</li>
        </ul>
        """
    
    def _get_data_analytics_content(self):
        return """
        <h2>Data-Driven Decision Making in Business</h2>
        <p>Data analytics provides valuable insights that can drive business growth and improve decision-making processes.</p>
        
        <h3>Analytics Process</h3>
        <ul>
            <li>Data collection and storage</li>
            <li>Data cleaning and preparation</li>
            <li>Analysis and modeling</li>
            <li>Insights and recommendations</li>
        </ul>
        """
    
    def _get_sustainability_content(self):
        return """
        <h2>Sustainable Business Practices for the Future</h2>
        <p>Sustainability is no longer optional for businesses. Implementing sustainable practices benefits both the environment and the bottom line.</p>
        
        <h3>Sustainability Strategies</h3>
        <ul>
            <li>Energy efficiency improvements</li>
            <li>Waste reduction programs</li>
            <li>Sustainable supply chain management</li>
            <li>Green product development</li>
        </ul>
        """
