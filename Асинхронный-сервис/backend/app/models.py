from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, User
from django.db import models


class Substance(models.Model):
    STATUS_CHOICES = (
        (1, 'Действует'),
        (2, 'Удалена'),
    )

    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(max_length=500, verbose_name="Описание",)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    image = models.ImageField(verbose_name="Фото", blank=True, null=True)

    number = models.IntegerField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Вещество"
        verbose_name_plural = "Вещества"
        db_table = "substances"
        ordering = ("pk",)


class Medicine(models.Model):
    STATUS_CHOICES = (
        (1, 'Введён'),
        (2, 'В работе'),
        (3, 'Завершен'),
        (4, 'Отклонен'),
        (5, 'Удален')
    )

    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    date_created = models.DateTimeField(verbose_name="Дата создания", blank=True, null=True)
    date_formation = models.DateTimeField(verbose_name="Дата формирования", blank=True, null=True)
    date_complete = models.DateTimeField(verbose_name="Дата завершения", blank=True, null=True)

    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Создатель", related_name='owner', null=True)
    moderator = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Сотрудник", related_name='moderator', blank=True,  null=True)

    name = models.CharField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    dose = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return "Лекарство №" + str(self.pk)

    class Meta:
        verbose_name = "Лекарство"
        verbose_name_plural = "Лекарства"
        db_table = "medicines"
        ordering = ('-date_formation', )


class SubstanceMedicine(models.Model):
    substance = models.ForeignKey(Substance, on_delete=models.DO_NOTHING, blank=True, null=True)
    medicine = models.ForeignKey(Medicine, on_delete=models.DO_NOTHING, blank=True, null=True)
    weight = models.IntegerField(verbose_name="Поле м-м", default=100)

    def __str__(self):
        return "м-м №" + str(self.pk)

    class Meta:
        verbose_name = "м-м"
        verbose_name_plural = "м-м"
        db_table = "substance_medicine"
        ordering = ('pk', )
        constraints = [
            models.UniqueConstraint(fields=['substance', 'medicine'], name="substance_medicine_constraint")
        ]
