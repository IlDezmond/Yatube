from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User

POSTS_SHOWN_AMOUNT = 10


def paginate(request, model_object, instances_amount: int):
    paginator = Paginator(model_object, instances_amount)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):
    template = 'posts/index.html'
    posts = Post.objects.select_related('author', 'group')
    page_obj = paginate(request, posts, POSTS_SHOWN_AMOUNT)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author', 'group')
    page_obj = paginate(request, posts, POSTS_SHOWN_AMOUNT)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    profile_user = get_object_or_404(User, username=username)
    posts = profile_user.posts.select_related('author', 'group')
    page_obj = paginate(request, posts, POSTS_SHOWN_AMOUNT)
    following = (
        profile_user.following.filter(user_id=request.user.id).exists()
    )
    context = {
        'profile_user': profile_user,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(
        Post.objects.select_related('author', 'group'),
        id=post_id
    )
    context = {
        'post': post,
        'form': CommentForm(),
        'comments': post.comments.all(),
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        author = request.user
        post.author = author
        post.save()
        return redirect('posts:profile', author.username)
    context = {
        'form': form,
        'is_edit': False,
    }
    return render(request, template, context=context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related('author').
        filter(id=post_id)
    )
    if post.author != request.user:
        return render(request, 'posts/post_edit_denied.html')

    template = 'posts/create_post.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'is_edit': True,
    }
    return render(request, template, context=context)


@login_required
def add_comment(request, post_id):
    form = CommentForm(request.POST or None)
    post = get_object_or_404(Post, id=post_id)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    posts = (Post.objects.filter(author__following__user=request.user)
             .select_related('author', 'group'))
    page_obj = paginate(request, posts, POSTS_SHOWN_AMOUNT)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user == author:
        return render(request, 'posts/self_follow_unavailable.html')
    Follow.objects.get_or_create(
        user=request.user,
        author=author
    )
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    Follow.objects.filter(
        user=request.user,
        author=get_object_or_404(User, username=username)
    ).delete()
    return redirect('posts:profile', username)
