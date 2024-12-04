from django.utils.translation import gettext_lazy as _

TRANSACTION_STATUS = (
    ('processing', _('В обработке')),
    ('completed', _('Успешно завершено')),
    ('canceled', _('Отменен')),
    ('timeout', _('Истек срок оплаты')),
)

TRANSACTION_TYPE = (
    ('tour', _('Тур')),
    ('hotel', _('Отель')),
    ('ticket', _('Авиабилет')),
)
