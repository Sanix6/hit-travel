from django.utils.translation import gettext_lazy as _

BOOK_STATUS = (
    ("booked", "Бронирование"),
    ("ticketed", "Оплачено"),
    ("canceled", "Отменено"),
    ("timeout", "Истек срок оплаты")
)

BOOK_CLASS_CHOICE = (
    ('e', 'Эконом класс'),
    ('b', 'Бизнес класс'),
    ('f', 'Первый класс'),
    ('w', 'Комфорт')
)

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


PASSENGER_TYPE = (
    ("adt", "Взрослый"),
    ("chd", "Ребенок"),
    ("inf", "Младенец без места"),
    ("src", "Пенсионер"),
    ("yth", "Подросток"),
    ("ins", "Младенец с местом")
)

DOCUMENT_TYPE = (
    ('C', 'Паспорт РФ'),
    ('B', 'Свидетельство о рождении РФ'),
    ('P', 'Заграничный паспорт РФ'),
    ('A', 'Иностранный документ'),
    ('M', 'Военный билет'),
    ('S', 'Паспорт моряка'),
    ('DP', 'Дипломатический паспорт'),
    ('WP', 'Служебный паспорт'),
    ('O', 'Удостоверение личности офицера'),
    ('L', 'Справка об утере паспорта'),
    ('R', 'Свидетельство на возвращение в РФ'),
    ('I', 'Не указан'),
)

PASSENGER_GENDER = (
    ("M", "Мужчина"),
    ("F", "Женщина"),
    ("MI", "Младенец мужского пола"),
    ("FI", "Младенец женского пола"),
)
