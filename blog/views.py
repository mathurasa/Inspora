from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import BlogPost, Category, Tag, Comment, Newsletter
from .forms import CommentForm, NewsletterForm
from .services import MediumService, BlogAnalyticsService

def blog_list(request):
    """Display list of blog posts with filtering and search"""
    posts = BlogPost.objects.filter(status='published').select_related('author', 'category')
    
    # Search functionality
    query = request.GET.get('q')
    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(excerpt__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()
    
    # Category filter
    category_slug = request.GET.get('category')
    if category_slug:
        posts = posts.filter(category__slug=category_slug)
    
    # Tag filter
    tag_slug = request.GET.get('tag')
    if tag_slug:
        posts = posts.filter(tags__slug=tag_slug)
    
    # Featured posts first
    posts = posts.order_by('-featured', '-published_at')
    
    # Pagination
    paginator = Paginator(posts, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get categories and tags for sidebar
    categories = Category.objects.annotate(post_count=Count('posts'))
    tags = Tag.objects.annotate(post_count=Count('posts'))
    
    # Popular posts
    popular_posts = BlogPost.objects.filter(status='published').order_by('-views')[:5]
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'tags': tags,
        'popular_posts': popular_posts,
        'query': query,
        'selected_category': category_slug,
        'selected_tag': tag_slug,
    }
    return render(request, 'blog/blog_list.html', context)

def post_detail(request, slug):
    """Display individual blog post with comments"""
    post = get_object_or_404(BlogPost, slug=slug, status='published')
    
    # Increment view count
    post.views += 1
    post.save()
    
    # Get comments
    comments = post.comments.filter(approved=True, parent=None).order_by('created_at')
    
    # Comment form
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Your comment has been submitted and is awaiting approval.')
            return redirect('blog:post_detail', slug=slug)
    else:
        comment_form = CommentForm()
    
    # Related posts
    related_posts = BlogPost.objects.filter(
        status='published',
        category=post.category
    ).exclude(id=post.id)[:3]
    
    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'related_posts': related_posts,
    }
    return render(request, 'blog/post_detail.html', context)

def category_posts(request, slug):
    """Display posts by category"""
    category = get_object_or_404(Category, slug=slug)
    posts = BlogPost.objects.filter(
        status='published',
        category=category
    ).select_related('author').order_by('-published_at')
    
    paginator = Paginator(posts, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, 'blog/category_posts.html', context)

def tag_posts(request, slug):
    """Display posts by tag"""
    tag = get_object_or_404(Tag, slug=slug)
    posts = BlogPost.objects.filter(
        status='published',
        tags=tag
    ).select_related('author').order_by('-published_at')
    
    paginator = Paginator(posts, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'tag': tag,
        'page_obj': page_obj,
    }
    return render(request, 'blog/tag_posts.html', context)

@login_required
@require_POST
def like_post(request, post_id):
    """Like/unlike a blog post"""
    post = get_object_or_404(BlogPost, id=post_id)
    
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    
    return JsonResponse({
        'liked': liked,
        'likes_count': post.likes.count()
    })

def newsletter_subscribe(request):
    """Subscribe to newsletter"""
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            newsletter, created = Newsletter.objects.get_or_create(
                email=email,
                defaults={'subscribed': True}
            )
            if not created and not newsletter.subscribed:
                newsletter.subscribed = True
                newsletter.unsubscribed_at = None
                newsletter.save()
            
            messages.success(request, 'Successfully subscribed to our newsletter!')
        else:
            messages.error(request, 'Invalid email address.')
    
    return redirect('blog:blog_list')

def newsletter_unsubscribe(request, email):
    """Unsubscribe from newsletter"""
    try:
        newsletter = Newsletter.objects.get(email=email)
        newsletter.subscribed = False
        newsletter.unsubscribed_at = timezone.now()
        newsletter.save()
        messages.success(request, 'Successfully unsubscribed from our newsletter.')
    except Newsletter.DoesNotExist:
        messages.error(request, 'Email not found in our newsletter list.')
    
    return redirect('blog:blog_list')

def sync_medium_articles(request):
    """Sync Medium articles from @mathurasa98 profile."""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('blog:blog_list')
    
    try:
        medium_service = MediumService()
        synced_count = medium_service.sync_medium_articles(request.user)
        
        if synced_count > 0:
            messages.success(request, f'Successfully synced {synced_count} articles from Medium!')
        else:
            messages.info(request, 'No new articles to sync from Medium.')
            
    except Exception as e:
        messages.error(request, f'Error syncing Medium articles: {str(e)}')
    
    return redirect('blog:blog_list')
