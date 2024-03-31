from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect

from NewsApp.models import Category
from .models import Subscriber


@login_required
@csrf_protect
def my_subscriptions(request):
    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        category = Category.objects.get(id=category_id)
        action = request.POST.get('action')

        if action == 'subscribe':
            Subscriber.objects.create(user=request.user, category=category)
        elif action == 'unsubscribe':
            Subscriber.objects.filter(user=request.user, category=category).delete()

    categories_with_subscriptions = Category.objects.annotate(
        user_subscribed=Exists(Subscriber.objects.filter(user=request.user, category=OuterRef('pk')))).order_by('name')
    return render(request, 'subscriptions/subscriptions.html', {'categories': categories_with_subscriptions})


# функция для отправки списка постов подписчикам.
# def send_articles_to_subscribers():
#     # Получите все статьи за последнюю неделю
#     last_week = timezone.now() - timedelta(days=7)
#     articles = Post.objects.filter(creationDate__gte=last_week)
#
#     # Формируйте сообщение со ссылками на статьи
#     message = '\n'.join([f'{article.title}: http://127.0.0.1:8000/news/{article.id}' for article in articles])
#
#     # Получите всех подписчиков
#     subscribers = Subscriber.objects.all()
#
#     # Отправьте каждому подписчику сообщение
#     for subscriber in subscribers:
#         send_mail(
#             'Новые статьи за неделю',
#             message,
#             'AndreyTestSF@yandex.ru',
#             [subscriber.user.email],
#         )