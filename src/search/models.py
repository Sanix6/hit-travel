from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Favorites(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Пользователь"),
        on_delete=models.CASCADE,
        related_name="user",
    )
    date = models.DateTimeField(_("Дата"), auto_now_add=True)
    tourid = models.CharField(_("Код тура"), max_length=100, null=True, blank=True)

    def __str__(self):
        return self.user.email


class Countries(models.Model):
    name = models.CharField(_('Страна'), max_length=200, editable=True)
    code_name = models.CharField(_('Код страны'), max_length=3, help_text='KGZ', blank=True, null=True)
    img = models.ImageField(_('Флаг'), upload_to='flags', null=True, blank=True)

    class Meta:
        verbose_name = 'Страна'
        verbose_name_plural = 'Страны'

    def __str__(self):
        if self.code_name:
            return f"{self.name}-{self.code_name}"
        return f"{self.name}"

    def save(self, *args, **kwargs):
        self.code_name = self.code_name.upper()
        super().save(*args, **kwargs)


class Cities(models.Model):
    main = models.ForeignKey(Countries, related_name="cities", on_delete=models.CASCADE, verbose_name=_("Страна"))
    name = models.CharField(_('Город'), max_length=200)
    code_name = models.CharField(_('Код города'), max_length=3, help_text='FRU')

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'

    def save(self, *args, **kwargs):
        self.code_name = self.code_name.upper()
        super().save(*args, **kwargs)


class Airports(models.Model):
    main = models.ForeignKey(Cities, related_name="airports", on_delete=models.CASCADE)
    name = models.CharField(_('Аэропрт'), max_length=200)
    code_name = models.CharField(_('Код аэропорта'), max_length=5, help_text='FRU')

    class Meta:
        verbose_name = 'Аэропорт'
        verbose_name_plural = 'Аэропорты'

    def save(self, *args, **kwargs):
        self.code_name = self.code_name.upper()
        super().save(*args, **kwargs)

