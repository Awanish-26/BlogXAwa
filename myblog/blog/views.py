# Standard library imports
import uuid
import markdown

# Django imports
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings

# Local imports
from .models import Post
from .forms import PostForm, EmailPostForm
from myblog.settings import supabase

# ------------------------------
# Views
# ------------------------------


# Home page view
def post_list(request):
    posts = Post.objects.all()
    for post in posts:
        post.content = markdown.markdown(post.content, extensions=[
                                         'markdown.extensions.fenced_code'])
    return render(request, 'blog/post_list.html', {'posts': posts})


# Post detail view
def post_detail(request, pk,  slug):
    post = get_object_or_404(Post, pk=pk, slug=slug)
    post.content = markdown.markdown(post.content, extensions=[
                                     'markdown.extensions.fenced_code'])
    return render(request, 'blog/post_detail.html', {'post': post})


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
            post.save()
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
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
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


# Post share view
def post_share(request, pk):
    post = Post.objects.get(pk=pk)
    if request.method == "POST":
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            send_mail(
                subject=f"{cd['name']} recommends you to read a post",
                message=f"{post.title}\n\n{cd['message']}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[cd['email']],
                auth_user=settings.EMAIL_HOST_USER,
                auth_password=settings.EMAIL_HOST_PASSWORD
            )
            messages.success(request, "Email sent successfully")
            return redirect('/')
        else:
            messages.error(request, "Error sending email")
    else:
        form = EmailPostForm()
    return render(request, 'blog/share.html', {'post': post, 'form': form})


# Post like view
@login_required
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return redirect('post_detail', pk=pk, slug=post.slug)
