import uuid

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, Group, PermissionsMixin
from django.utils.translation import gettext_lazy as _

from Web_site import settings

class MyUserManager(BaseUserManager):
    def create_user(self, email: str, name: str, surname: str, patronymic: str | None=None, password:str| None=None):
        if not email:
            raise ValueError("Пользователь должен иметь электронную почту.")

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            surname=surname,
            patronymic=patronymic
        )
        user.set_password(password)
        user.groups.set([Group.objects.get_or_create(name='Обычные пользователи')])
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, name: str, surname: str, patronymic: str | None=None, password:str| None=None):
        if not email:
            raise ValueError("Пользователь должен иметь электронную почту.")

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            surname=surname,
            patronymic=patronymic
        )
        user.set_password(password)
        user.groups.set([Group.objects.get_or_create(name='Администраторы')])
        user.save(using=self._db)
        return user

class MyUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField('почта', unique=True)
    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    is_active = models.BooleanField(default=True)

    name = models.CharField('имя')
    surname = models.CharField('фамилия')
    patronymic = models.CharField('отчество', null=True)
    REQUIRED_FIELDS = ['name', 'surname']

    objects = MyUserManager()

    @property
    def is_staff(self):
        return self.is_superuser

    # class Meta:
    #     permissions = (
    #         ('create_user', 'Создание новых пользователей. Доступно только администраторам.'),
    #         ('delete_user', '«Удаление» пользователя. Фактически ставится отметка о том, что учётная запись стала не активна, и зайти в неё не получится. Администраторы могут помечать неактивными любые учётные записи.')
    #     )

    def __str__(self):
        return f'{self.name} {self.patronymic} {self.surname} <{self.email}>'


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
    submiter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.DO_NOTHING,
        verbose_name='идентификатор загрузившего пользователя'
    )
    rating = models.IntegerField('вес сегмента', default=0)
    is_protected = models.BooleanField('сегмент защищён модератором или администратором', default=False)

    class Meta:
        permissions = (
            # ('change_segment', 'Изменение отдельно начала и конца сегмента. Доступно только администраторам.'),
            # ('delete_segment', 'Удаление сегмента. Доступно только администраторам или модераторам.'),
            ('protect_segment', 'Защита сегмента от последующих изменений со стороны рядовых пользователей. Доступно только администраторам или модераторам.'),
            ('change_category', 'Изменение категории сегмента.'),
            ('change_action', 'Изменение действия над категорией (заглушение или пропуск).'),
            ('vote', 'Проголосовать за или против сегмента, таким образом поддержав его от скрытия или наоборот.')
        )

    def __str__(self):
        return f'{self.videoUrl} {self.category} {self.action}'
