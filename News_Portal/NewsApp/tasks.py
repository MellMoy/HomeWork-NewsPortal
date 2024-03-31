from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone

from .models import Post
from my_subscriptions.models import Subscriber


@shared_task
def send_NewsApp_notification(news_id):
    news = Post.objects.get(id=news_id)
    subscribers = Subscriber.objects.all()
    for subscriber in subscribers:
        send_mail(
            'Новый пост',
            f'Создан новый пост: {news.title}',
            'Ironpress@yandex.ru',
            [subscriber.user.email],
        )


@shared_task
def send_weekly_news():
    one_week_ago = timezone.now() - timezone.timedelta(weeks=1)
    news = Post.objects.filter(creationDate__gte=one_week_ago)
    subscribers = Subscriber.objects.all()
    for subscriber in subscribers:
        send_mail(
            'Еженедельные новости',
            f'Вот новости за прошедшую неделю: {", ".join(news.values_list("title", flat=True))}',
            'swaggadanil@mail.ru',
            [subscriber.user.email],
        )
