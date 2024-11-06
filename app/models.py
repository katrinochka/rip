from django.db import models
from django.utils import timezone

from django.contrib.auth.models import User


class Programm(models.Model):
    STATUS_CHOICES = (
        (1, 'Действует'),
        (2, 'Удалена'),
    )

    name = models.CharField(max_length=100, verbose_name="Название", blank=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    image = models.ImageField(blank=True, null=True)
    description = models.TextField(verbose_name="Описание", blank=True)

    price = models.IntegerField(blank=True)
    material = models.CharField(blank=True)

    def get_image(self):
        if self.image:
            return self.image.url.replace("minio", "localhost", 1)

        return "http://localhost:9000/images/default.png"

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Программа"
        verbose_name_plural = "Программы"
        db_table = "programms"


class Manufacture(models.Model):
    STATUS_CHOICES = (
        (1, 'Введён'),
        (2, 'В работе'),
        (3, 'Завершен'),
        (4, 'Отклонен'),
        (5, 'Удален')
    )

    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    date_created = models.DateTimeField(default=timezone.now(), verbose_name="Дата создания")
    date_formation = models.DateTimeField(verbose_name="Дата формирования", blank=True, null=True)
    date_complete = models.DateTimeField(verbose_name="Дата завершения", blank=True, null=True)

    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Пользователь", null=True, related_name='owner')
    moderator = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Работник", null=True, related_name='moderator')

    name = models.CharField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)

    def __str__(self):
        return "Деталь №" + str(self.pk)

    def get_programms(self):
        return [
            setattr(item.programm, "value", item.value) or item.programm
            for item in ProgrammManufacture.objects.filter(manufacture=self)
        ]

    class Meta:
        verbose_name = "Деталь"
        verbose_name_plural = "Детали"
        ordering = ('-date_formation',)
        db_table = "manufactures"


class ProgrammManufacture(models.Model):
    programm = models.ForeignKey(Programm, models.DO_NOTHING, blank=True, null=True)
    manufacture = models.ForeignKey(Manufacture, models.DO_NOTHING, blank=True, null=True)
    value = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return "м-м №" + str(self.pk)

    class Meta:
        verbose_name = "м-м"
        verbose_name_plural = "м-м"
        db_table = "programm_manufacture"
        unique_together = ('programm', 'manufacture')
