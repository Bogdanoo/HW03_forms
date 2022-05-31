from django.core.paginator import Paginator
from django.conf import settings
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from .models import Group, Post, User, PostForm


def index(request):
    post_list = Post.objects.all().order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = (
        Post
        .objects
        .filter(group=group).all()
    )[:settings.MAX_PAGE_AMOUNT]
    context = {
        'group': group,
        'posts': posts,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts_count = author.posts.count()
    post_list = author.posts.select_related('author')
    paginator = Paginator(post_list, settings.MAX_PAGE_AMOUNT)
    page_number = request.GET.get('page')
    page_object = paginator.get_page(page_number)
    context = {
        'author': author,
        'page_obj': page_object,
        'posts_amount': posts_count,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    context = {
        'post': post,
    }
    return render(request, 'posts/post_detail.html', context)


def post_create(request):
    form = PostForm(request.POST or None)
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', username=post.author)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    form = PostForm(instance=post)
    is_edit = True
    if request.user == post.author:
        if request.method == 'POST':
            form = PostForm(request.POST or None, instance=post)
            if form.is_valid():
                form.save()
            return redirect('posts:post_detail', post.pk)
        context = {
            'form': form,
            'post': post,
            'is_edit': is_edit,
        }
        return render(request, 'posts/update_post.html', context)
