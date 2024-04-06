from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView)

from blog.models import Category, Post
from blogicum.settings import MAX_POSTS
from .forms import PostCreateForm, CommentForm
from .mixins import (
    BaseCommentMixin, CommentUpdateAndDeleteMixin,
    OnlyOwnerMixin, PostUpdateAndDeleteMixin)
from .utils import get_post_list


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


class PostUpdateView(PostUpdateAndDeleteMixin, UpdateView):
    def get_success_url(self) -> str:
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.object.pk})


class PostDeleteView(PostUpdateAndDeleteMixin, DeleteView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostCreateForm(instance=self.object)
        return context


class PostListView(ListView):
    template_name = 'blog/index.html'
    paginate_by = MAX_POSTS
    queryset = get_post_list(filter=True, annotation=True)


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

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


class CommentCreateView(BaseCommentMixin, CreateView):
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)


class CommentUpdateView(BaseCommentMixin,
                        CommentUpdateAndDeleteMixin,
                        OnlyOwnerMixin,
                        UpdateView):
    pass


class CommentDeleteView(BaseCommentMixin,
                        CommentUpdateAndDeleteMixin,
                        OnlyOwnerMixin,
                        DeleteView):
    pass


class CategoryPostsListView(ListView):
    template_name = 'blog/category.html'
    paginate_by = MAX_POSTS

    def get_category(self):
        return get_object_or_404(
            Category.objects.filter(is_published=True),
            slug=self.kwargs['slug']
        )

    def get_queryset(self):
        return get_post_list(self.get_category().posts, True, True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_category()
        return context


class CreateUser(CreateView):
    template_name = 'registration/registration_form.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('blog:index')


class UserDetailView(ListView):
    template_name = 'blog/profile.html'
    paginate_by = MAX_POSTS

    def get_user(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_queryset(self):
        user = self.get_user()
        if self.request.user == user:
            return get_post_list(user.posts, annotation=True)
        return get_post_list(user.posts, True, True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_user()
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
