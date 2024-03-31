import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util
from news.models import Post
from subscriptions.models import Subscriber
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


def send_weekly_emails():
    one_week_ago = timezone.now() - timedelta(days=7)
    new_posts = Post.objects.filter(creationDate__gte=one_week_ago)

    for post in new_posts:
        categories = post.postCategory.all()
        for category in categories:
            subscribers = Subscriber.objects.filter(category=category)
            for subscriber in subscribers:
                # if проверяет у подписчика адрес электронной почты.
                # Если есть, он перейдет к отправке электронного письма с помощью функции "send_mail".
                if subscriber.user.email:
                    send_mail(
                        'Список постов за последнюю неделю',
                        f'Появилась новый пост, проверьте ее: http://127.0.0.1:8000/news/{post.id}',
                        'AndreyTestSF@yandex.ru',
                        [subscriber.user.email],
                    )
                else:
                    send_mail(
                        'Нет новых постов',
                        "За прошедшую неделю не было новых статей",
                        'AndreyTestSF@yandex.ru',
                        [subscriber.user.email],
                    )


# Декоратор `close_old_connections` гарантирует, что соединения с базой данных,
# которые стали непригодными для использования или устарели, будут закрыты до и после вашего
# задание выполнено. Вы должны использовать его для переноса любых заданий, для которых вы запланировали этот доступ
# база данных Django любым способом.
@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    """
    Это задание удаляет записи о выполнении задания APScheduler старше `max_age`
    из базы данных.
    Это помогает предотвратить заполнение базы данных старыми историческими данными
    записи, которые больше не являются полезными.

    :параметр max_age: Максимальный промежуток времени для сохранения исторических данных
    записи о выполнении заданий. Значение по умолчанию - 7 дней.
    """
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            send_weekly_emails,
            trigger=CronTrigger(day_of_week='fri', hour=18, minute=00),
            id="send_weekly_emails",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Добавлена работа send_weekly_emails..")
        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )

        try:
            logger.info("Запуск планировщика...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Остановка планировщика...")
            scheduler.shutdown()
            logger.info("Планировщик успешно закрылся!")