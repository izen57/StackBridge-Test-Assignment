import uuid

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class Segment(models.Model):
    id = models.UUIDField('идентификатор', primary_key=True, default=uuid.uuid4, editable=False)
    videoUrl = models.URLField('URL видео, которому принадлежит сегмент')

    class Categories(models.IntegerChoices):
        __empty__ = _('Выберите категорию сегмента')
        SPONSOR = 1, _('Реклама или спонсор видео')
        SELF = 2, _('Самореклама (услуг или своих интернет-ресурсов)')
        ACTION = 3, _('Напоминание о взаимодействии (лайк, подписка, комментарий)')
        RECAP = 4, _('Пересказ предыдущих видео или рассказ о том, что будет в следующих')
    category = models.IntegerField('категория сегмента', choices=Categories)

    class Actions(models.TextChoices):
        SKIP = 'Пропустить'
        MUTE = 'Заглушить'
    action = models.CharField('действия с сегментом', choices=Actions, default=Actions.SKIP)

    start = models.TimeField('начало сегмента')
    end = models.TimeField('конец сегмента')
    submiter_id = models.ForeignKey(User, models.DO_NOTHING, verbose_name='идентификатор загрузившего пользователя')
    votes_amount = models.IntegerField('Кол-во голосов за и против', default=0)

    def __str__(self):
        return f'{self.id} {self.category} {self.action}'
