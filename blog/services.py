"""
Blog services for Inspora platform.
"""
import requests
import json
from datetime import datetime
from django.conf import settings
from .models import BlogPost, Category, Tag


class MediumService:
    """Service for integrating with Medium API and fetching articles."""
    
    def __init__(self):
        self.base_url = "https://api.rss2json.com/v1/api.json"
        self.medium_profile = "https://medium.com/@mathurasa98"
    
    def fetch_medium_articles(self):
        """Fetch articles from Medium profile using RSS to JSON service."""
        try:
            # Use RSS to JSON service to fetch Medium articles
            params = {
                'rss_url': f'{self.medium_profile}/feed',
                'api_key': getattr(settings, 'RSS_API_KEY', None),  # Optional API key
                'count': 20  # Number of articles to fetch
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 'ok':
                return self._parse_medium_articles(data.get('items', []))
            else:
                return []
                
        except Exception as e:
            print(f"Error fetching Medium articles: {e}")
            return []
    
    def _parse_medium_articles(self, articles):
        """Parse Medium RSS articles into structured data."""
        parsed_articles = []
        
        for article in articles:
            try:
                # Extract author from Medium URL
                author_name = article.get('author', 'Unknown Author')
                
                # Extract tags from categories
                tags = []
                if 'categories' in article:
                    tags = [cat.strip() for cat in article['categories'] if cat.strip()]
                
                # Parse publication date
                pub_date = None
                if article.get('pubDate'):
                    try:
                        pub_date = datetime.strptime(article['pubDate'], '%a, %d %b %Y %H:%M:%S %z')
                    except:
                        pub_date = datetime.now()
                
                parsed_articles.append({
                    'title': article.get('title', 'Untitled'),
                    'content': article.get('content', ''),
                    'excerpt': article.get('description', ''),
                    'author_name': author_name,
                    'url': article.get('link', ''),
                    'published_date': pub_date,
                    'tags': tags,
                    'image_url': article.get('thumbnail', ''),
                    'read_time': self._estimate_read_time(article.get('content', '')),
                    'source': 'Medium'
                })
                
            except Exception as e:
                print(f"Error parsing article {article.get('title', 'Unknown')}: {e}")
                continue
        
        return parsed_articles
    
    def _estimate_read_time(self, content):
        """Estimate reading time based on content length."""
        if not content:
            return 1
        
        # Average reading speed: 200 words per minute
        word_count = len(content.split())
        minutes = max(1, round(word_count / 200))
        return minutes
    
    def sync_medium_articles(self, user):
        """Sync Medium articles to local blog posts."""
        articles = self.fetch_medium_articles()
        synced_count = 0
        
        for article_data in articles:
            try:
                # Check if article already exists
                if BlogPost.objects.filter(title=article_data['title']).exists():
                    continue
                
                # Create or get category
                category, _ = Category.objects.get_or_create(
                    name='Medium Articles',
                    defaults={'description': 'Articles imported from Medium'}
                )
                
                # Create blog post
                blog_post = BlogPost.objects.create(
                    title=article_data['title'],
                    content=article_data['content'],
                    excerpt=article_data['excerpt'],
                    author=user,
                    category=category,
                    status='published',
                    is_featured=False,
                    meta_description=article_data['excerpt'][:160] if article_data['excerpt'] else '',
                    external_url=article_data['url']
                )
                
                # Add tags
                for tag_name in article_data['tags'][:5]:  # Limit to 5 tags
                    tag, _ = Tag.objects.get_or_create(name=tag_name)
                    blog_post.tags.add(tag)
                
                synced_count += 1
                
            except Exception as e:
                print(f"Error syncing article {article_data.get('title', 'Unknown')}: {e}")
                continue
        
        return synced_count


class BlogAnalyticsService:
    """Service for blog analytics and insights."""
    
    @staticmethod
    def get_popular_posts(limit=10):
        """Get most popular blog posts based on views and likes."""
        return BlogPost.objects.filter(
            status='published'
        ).order_by('-views', '-likes')[:limit]
    
    @staticmethod
    def get_recent_posts(limit=10):
        """Get most recent blog posts."""
        return BlogPost.objects.filter(
            status='published'
        ).order_by('-created_at')[:limit]
    
    @staticmethod
    def get_posts_by_category(category_name, limit=10):
        """Get posts by category."""
        try:
            category = Category.objects.get(name=category_name)
            return BlogPost.objects.filter(
                category=category,
                status='published'
            ).order_by('-created_at')[:limit]
        except Category.DoesNotExist:
            return []
    
    @staticmethod
    def get_related_posts(post, limit=5):
        """Get related posts based on tags and category."""
        related_posts = BlogPost.objects.filter(
            status='published'
        ).exclude(id=post.id)
        
        # First try to find posts with same tags
        if post.tags.exists():
            tag_ids = post.tags.values_list('id', flat=True)
            tag_related = related_posts.filter(tags__id__in=tag_ids).distinct()
            if tag_related.count() >= limit:
                return tag_related[:limit]
        
        # Then try same category
        if post.category:
            category_related = related_posts.filter(category=post.category)
            if category_related.count() >= limit:
                return category_related[:limit]
        
        # Fallback to recent posts
        return related_posts.order_by('-created_at')[:limit]
    
    @staticmethod
    def get_blog_stats():
        """Get overall blog statistics."""
        total_posts = BlogPost.objects.filter(status='published').count()
        total_views = BlogPost.objects.aggregate(
            total_views=models.Sum('views')
        )['total_views'] or 0
        total_likes = BlogPost.objects.aggregate(
            total_likes=models.Sum('likes')
        )['total_likes'] or 0
        
        # Get category distribution
        category_stats = Category.objects.annotate(
            post_count=models.Count('blogpost')
        ).values('name', 'post_count').order_by('-post_count')
        
        # Get monthly post count
        from django.db import models
        monthly_stats = BlogPost.objects.filter(
            status='published'
        ).extra(
            select={'month': "EXTRACT(month FROM created_at)"}
        ).values('month').annotate(
            count=models.Count('id')
        ).order_by('month')
        
        return {
            'total_posts': total_posts,
            'total_views': total_views,
            'total_likes': total_likes,
            'category_stats': list(category_stats),
            'monthly_stats': list(monthly_stats)
        }


class BlogSearchService:
    """Service for advanced blog search functionality."""
    
    @staticmethod
    def search_posts(query, filters=None):
        """Search blog posts with advanced filtering."""
        from django.db.models import Q
        
        posts = BlogPost.objects.filter(status='published')
        
        if query:
            # Search in title, content, excerpt, and tags
            search_query = Q(title__icontains=query) | \
                          Q(content__icontains=query) | \
                          Q(excerpt__icontains=query) | \
                          Q(tags__name__icontains=query)
            posts = posts.filter(search_query).distinct()
        
        # Apply filters
        if filters:
            if filters.get('category'):
                posts = posts.filter(category__name=filters['category'])
            
            if filters.get('author'):
                posts = posts.filter(author__username__icontains=filters['author'])
            
            if filters.get('date_from'):
                posts = posts.filter(created_at__gte=filters['date_from'])
            
            if filters.get('date_to'):
                posts = posts.filter(created_at__lte=filters['date_to'])
            
            if filters.get('tags'):
                tag_list = [tag.strip() for tag in filters['tags'].split(',')]
                posts = posts.filter(tags__name__in=tag_list).distinct()
        
        return posts.order_by('-created_at')
    
    @staticmethod
    def get_search_suggestions(query, limit=5):
        """Get search suggestions based on query."""
        if len(query) < 2:
            return []
        
        # Get suggestions from titles
        title_suggestions = BlogPost.objects.filter(
            title__icontains=query,
            status='published'
        ).values_list('title', flat=True)[:limit]
        
        # Get suggestions from tags
        tag_suggestions = Tag.objects.filter(
            name__icontains=query
        ).values_list('name', flat=True)[:limit]
        
        # Get suggestions from categories
        category_suggestions = Category.objects.filter(
            name__icontains=query
        ).values_list('name', flat=True)[:limit]
        
        suggestions = list(title_suggestions) + list(tag_suggestions) + list(category_suggestions)
        return list(set(suggestions))[:limit]
