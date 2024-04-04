from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView)

from blog.models import Category, Post, Comment
from .forms import PostCreateForm, CommentForm
from .mixins import CommentMixin, OnlyOwnerMixin, PostMixin
from .utils import get_post_list


MAX_POSTS: int = 10

User = get_user_model()


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostCreateForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})


class PostUpdateView(PostMixin, UpdateView):
    def get_success_url(self) -> str:
        return reverse_lazy('blog:post_detail', kwargs={'pk': self.object.pk})


class PostDeleteView(PostMixin, DeleteView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostCreateForm(instance=self.object)
        return context


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = MAX_POSTS
    queryset = get_post_list()


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if (obj.author != self.request.user
            and (not obj.is_published or not obj.category.is_published
                 or obj.pub_date > timezone.now())):
            raise Http404
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.select_related('author')
        context['form'] = CommentForm()
        return context


class CommentCreateView(CommentMixin, CreateView):
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)


class CommentUpdateView(CommentMixin, OnlyOwnerMixin, UpdateView):
    template_name = 'blog/comment.html'

    def get_object(self, queryset=None):
        post_id = self.kwargs['post_id']
        comment_id = self.kwargs['comment_id']
        return get_object_or_404(Comment, pk=comment_id, post_id=post_id)


class CommentDeleteView(CommentMixin, OnlyOwnerMixin, DeleteView):
    template_name = 'blog/comment.html'

    def get_object(self, queryset=None):
        post_id = self.kwargs['post_id']
        comment_id = self.kwargs['comment_id']
        return get_object_or_404(Comment, pk=comment_id, post_id=post_id)


class CategoryPostsListView(ListView):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = MAX_POSTS

    def get_queryset(self):
        return get_post_list().filter(category__slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category.objects.values('title', 'description').filter(
                is_published=True
            ), slug=self.kwargs['slug'])
        return context


class UserDetailView(DetailView):
    model = User
    template_name = 'blog/profile.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        users_posts = Post.objects.filter(author=self.object)

        if self.request.user == self.object:
            users_posts = Post.objects.filter(author=self.object)
        else:
            users_posts = get_post_list().filter(author=self.object)

        paginator = Paginator(users_posts, MAX_POSTS)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        return context


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    fields = ['username', 'first_name', 'last_name', 'email']

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.object.username})
