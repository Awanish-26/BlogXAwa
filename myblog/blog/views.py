# Standard library imports
import uuid
import markdown
from django.utils import timezone

# Django imports
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.conf import settings
from django.db.models import Q
from django.views.decorators.http import require_POST

# Local imports
from .models import Comment, Post, Category, Tag
from .forms import CommentForm, PostForm, EmailPostForm
from myblog.settings import supabase

# ------------------------------
# Views
# ------------------------------


# Home page view
def post_list(request):
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    tag = request.GET.get('tag', '').strip()

    posts = Post.objects.filter(is_published=True)

    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query)
        )

    if category:
        posts = posts.filter(category__slug=category)

    if tag:
        posts = posts.filter(tags__slug=tag)

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    for post in page_obj:
        post.content = markdown.markdown(
            post.content,
            extensions=['markdown.extensions.fenced_code']
        )

    return render(
        request,
        'blog/post_list.html',
        {
            'posts': page_obj,
            'query': query,
            'selected_category': category,
            'selected_tag': tag,
            'categories': Category.objects.all(),
            'tags': Tag.objects.all(),
        }
    )


# Post detail view
def post_detail(request, pk, slug):
    filters = Q(is_published=True)

    if request.user.is_authenticated:
        filters |= Q(author=request.user)

    post = get_object_or_404(
        Post.objects.filter(filters),
        pk=pk,
        slug=slug,
    )

    post.content = markdown.markdown(
        post.content,
        extensions=['markdown.extensions.fenced_code'],
    )

    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments': post.comments.select_related('author'),
        'comment_form': CommentForm() if request.user.is_authenticated else None,
    })


@login_required
@require_POST
def comment_create(request, pk):
    post = get_object_or_404(Post, pk=pk, is_published=True)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        messages.success(request, 'Comment added.')
    return redirect('post_detail', pk=post.pk, slug=post.slug)


@login_required
def comment_edit(request, pk):
    comment = get_object_or_404(Comment, pk=pk, author=request.user)
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Comment updated.')
            return redirect('post_detail', pk=comment.post.pk, slug=comment.post.slug)
    else:
        form = CommentForm(instance=comment)
    return render(request, 'blog/comment_edit.html', {
        'form': form,
        'comment': comment,
    })


@login_required
@require_POST
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk, author=request.user)
    post = comment.post
    comment.delete()
    messages.success(request, 'Comment deleted.')
    return redirect('post_detail', pk=post.pk, slug=post.slug)


# Post creation view
@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)

            if "banner" in request.FILES:
                file = request.FILES["banner"]
                file_data = file.read()

                # Generate a unique file name
                file_name = f"{uuid.uuid4()}.{file.name.split('.')[-1]}"

                # Validate file type
                content_type = file.content_type
                allowed_types = ['image/png',
                                 'image/jpeg', 'image/jpg', 'image/gif']
                if content_type not in allowed_types:
                    messages.error(request, "Unsupported file type.")
                    return redirect('post_create')

                # Upload file to the 'uploads' bucket with the new file_name
                supabase.storage.from_('uploads').upload(
                    path=file_name,
                    file=file_data,
                    file_options={'content-type': content_type}
                )

                # Get the permanent public URL
                public_url = supabase.storage.from_(
                    'uploads').get_public_url(file_name)

                # Assign banner and image name to post
                post.banner = public_url
                # Storing the original file name might be useful, but the key is the public_url
                post.image_name = file.name
            else:
                post.banner = None
                post.image_name = None

            post.author = request.user

            if request.POST.get('action') == 'publish':
                post.is_published = True
                post.published_at = timezone.now()
            else:
                post.is_published = False
                post.published_at = None

            post.save()
            form.save_m2m()
            messages.success(request, "Post created successfully")
            return redirect('post_list')
    else:
        form = PostForm()
    return render(request, 'blog/post_create.html', {'form': form})


# Post edit view
@login_required
def edit(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            if "banner" in request.FILES:
                file = request.FILES["banner"]
                file_data = file.read()
                file_name = f"{uuid.uuid4()}.{file.name.split('.')[-1]}"
                file_path = "uploads/" + file_name

                # Validate file type
                content_type = file.content_type
                allowed_types = ['image/png',
                                 'image/jpeg', 'image/jpg', 'image/gif']
                if content_type not in allowed_types:
                    messages.error(request, "Unsupported file type.")
                    return redirect('post_create')

                # Update file in storage
                supabase.storage.from_(
                    'uploads').update(file_path, file_data, {'content-type': content_type})

                # Generate signed URL
                signed_url_response = supabase.storage.from_(
                    'uploads').create_signed_url(file_path, 60 * 60 * 24)
                public_url = signed_url_response['signedURL']

                # Assign banner and image name to post
                post.banner = public_url
                post.image_name = file.name

            post.save()
            form.save_m2m()
            messages.success(request, "Updated successfully")
            return redirect('post_list')
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})


# Post delete view
@login_required
def delete(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    if post.image_name:
        supabase.storage.from_('uploads').remove(
            ["uploads/" + post.image_name, post.image_name])
    post.delete()
    messages.success(request, "Item deleted successfully")
    return redirect('/')


# Post like view
@login_required
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return redirect('post_detail', pk=pk, slug=post.slug)


@login_required
@require_POST
def publish_post(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    post.is_published = True
    post.published_at = timezone.now()
    post.save(update_fields=['is_published', 'published_at'])
    messages.success(request, 'Post published successfully.')
    return redirect('profile')


@login_required
@require_POST
def unpublish_post(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    post.is_published = False
    post.save(update_fields=['is_published'])
    messages.success(request, 'Post moved back to drafts.')
    return redirect('profile')
