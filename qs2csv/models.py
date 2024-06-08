from datetime import timedelta
from decimal import Decimal
from json import dumps
from random import randint
from uuid import uuid4

from django.db import models
from django.utils.crypto import get_random_string


def random_string():
    return get_random_string(length=10)


def random_int():
    return randint(-2147483648, 2147483647)


def random_json():
    return dumps({random_string(): random_int()})


def random_decimal():
    return Decimal(random_int() / 117)


def random_float():
    return float(random_int() / 117)


class ForeignKeyModel(models.Model):
    chars = models.CharField(max_length=255, default="test")

    def __str__(self) -> str:
        return f"FK Model #{self.pk}"


class TestModel(models.Model):
    """This is a test model that uses all supported fields.
    ManyToManyField is not supported and GeneratedField is not
    available for all the project's Django dependency.

    """

    pk_field = models.BigAutoField(primary_key=True, verbose_name="Big Auto")
    char_field = models.CharField(
        max_length=255, default=get_random_string, verbose_name="Chars"
    )
    big_int_field = models.BigIntegerField(
        default=random_int, verbose_name="Big Integer"
    )
    boolean_field = models.BooleanField(default=True, verbose_name="Boolean")
    date_field = models.DateField(auto_now_add=True, verbose_name="Date")
    datetime_field = models.DateTimeField(auto_now_add=True, verbose_name="DateTime")
    decimal_field = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=random_decimal,
        verbose_name="Decimal",
    )
    duration_field = models.DurationField(
        default=timedelta(hours=24), verbose_name="Duration"
    )
    float_field = models.FloatField(default=random_float, verbose_name="Float")
    foreign_key = models.ForeignKey(
        ForeignKeyModel,
        related_name="all_fields_fk_models",
        db_index=False,
        on_delete=models.CASCADE,
        verbose_name="Foreign Key",
    )
    generic_ip_field = models.GenericIPAddressField(
        default="2a02:42fe::4", verbose_name="Generic IP Address"
    )
    json_field = models.JSONField(default=random_json, verbose_name="JSON")
    one_to_one_field = models.OneToOneField(
        ForeignKeyModel,
        related_name="all_fields_oto_models",
        db_index=False,
        on_delete=models.CASCADE,
        verbose_name="OneToOne",
    )
    many_to_many_field = models.ManyToManyField(ForeignKeyModel)
    text_field = models.TextField(default=random_string, verbose_name="Text")
    time_field = models.TimeField(auto_now_add=True, verbose_name="Time")
    uuid_field = models.UUIDField(default=uuid4, verbose_name="UUID")

    def __str__(self) -> str:
        return f"AF Model #{self.pk}"
