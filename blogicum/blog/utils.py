from django.db.models import Count
from django.utils import timezone

from blog.models import Post


def get_post_list(manager=Post.objects, filter=False, annotation=False):
    data = manager.select_related('category', 'location', 'author')
    if filter:
        data = data.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True
        )
    if annotation:
        data = data.annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')
    return data
