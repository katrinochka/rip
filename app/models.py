from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, User
from django.db import models
from django.utils import timezone


class Programm(models.Model):
    STATUS_CHOICES = (
        (1, 'Действует'),
        (2, 'Удалена'),
    )

    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(max_length=500, verbose_name="Описание",)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    image = models.ImageField(verbose_name="Фото", blank=True, null=True)

    price = models.IntegerField()
    material = models.CharField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Программа"
        verbose_name_plural = "Программы"
        db_table = "programms"
        ordering = ("pk",)


class Manufacture(models.Model):
    STATUS_CHOICES = (
        (1, 'Введён'),
        (2, 'В работе'),
        (3, 'Завершен'),
        (4, 'Отклонен'),
        (5, 'Удален')
    )

    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    date_created = models.DateTimeField(verbose_name="Дата создания", blank=True, null=True, default=timezone.now())
    date_formation = models.DateTimeField(verbose_name="Дата формирования", blank=True, null=True)
    date_complete = models.DateTimeField(verbose_name="Дата завершения", blank=True, null=True)

    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Создатель", related_name='owner', null=True)
    moderator = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Работник", related_name='moderator', blank=True,  null=True)

    name = models.CharField(blank=True, null=True)
    marriage = models.BooleanField(blank=True, null=True, default=False)

    def __str__(self):
        return "Деталь №" + str(self.pk)

    class Meta:
        verbose_name = "Деталь"
        verbose_name_plural = "Детали"
        db_table = "manufactures"
        ordering = ('-date_formation', )


class ProgrammManufacture(models.Model):
    programm = models.ForeignKey(Programm, on_delete=models.DO_NOTHING, blank=True, null=True)
    manufacture = models.ForeignKey(Manufacture, on_delete=models.DO_NOTHING, blank=True, null=True)
    duration = models.IntegerField(verbose_name="Поле м-м", default=0)

    def __str__(self):
        return "м-м №" + str(self.pk)

    class Meta:
        verbose_name = "м-м"
        verbose_name_plural = "м-м"
        db_table = "programm_manufacture"
        ordering = ('pk', )
        constraints = [
            models.UniqueConstraint(fields=['programm', 'manufacture'], name="programm_manufacture_constraint")
        ]
