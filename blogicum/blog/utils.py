from django.utils import timezone

from blog.models import Post


def get_post_list():
    """Вспомогательная функция для получения постов по условию задания."""
    return Post.objects.select_related(
        'category',
        'location',
        'author'
    ).filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True
    )
