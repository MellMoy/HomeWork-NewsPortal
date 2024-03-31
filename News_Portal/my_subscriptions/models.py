from django.db import models
from django.contrib.auth.models import User


# Создавайте свои модели здесь.
class Subscriber(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey('NewsApp.Category', on_delete=models.CASCADE)
