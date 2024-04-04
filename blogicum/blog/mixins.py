from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy

from .forms import PostCreateForm, CommentForm
from .models import Post, Comment


class OnlyOwnerMixin(UserPassesTestMixin):
    def test_func(self):
        return self.get_object().author == self.request.user


class PostMixin(OnlyOwnerMixin, LoginRequiredMixin):
    model = Post
    form_class = PostCreateForm
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'

    def handle_no_permission(self):
        return redirect(reverse('blog:post_detail',
                                kwargs={'pk': self.get_object().pk}))

    def get_success_url(self) -> str:
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostCreateForm(instance=self.object)
        return context


class CommentMixin(LoginRequiredMixin):
    model = Comment
    form_class = CommentForm

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'pk': self.object.post.pk})
