from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User
from .utils import paginator


def index(request):
    post_list = Post.objects.select_related('author', 'group')
    page_obj = paginator(request, post_list)
    context = {'page_obj': page_obj, 'post_list': post_list}
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author')
    page_obj = paginator(request, posts)
    context = {'group': group, 'posts': posts, 'page_obj': page_obj}
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=author)
    page_obj = paginator(request, post_list)
    context = {'author': author, 'page_obj': page_obj, 'post_list': post_list}
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    one_post = get_object_or_404(Post, pk=post_id)
    author = Post.objects.select_related('author', 'group')
    context = {'one_post': one_post, 'author': author}
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST or None)

        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.text = form.cleaned_data['text']
            new_post.group = form.cleaned_data['group']
            new_post.author = request.user
            new_post.save()

            return redirect('posts:profile', username=request.user)
        return render(request, 'posts/create_post.html', {'form': form})

    form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    groups = Group.objects.all()

    if request.user == post.author:
        form = PostForm(request.POST or None, instance=post)

        if form.is_valid():
            post = form.save()
            post.save()

            return redirect('posts:post_detail', post_id=post_id)
        context = {'form': form, 'is_edit': True, 'post': post,
                   'groups': groups}
        return render(request, 'posts/create_post.html',
                      context)
    return redirect('posts:post_detail', post_id=post_id)
