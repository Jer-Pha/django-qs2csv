# Generated by Django 3.2.18 on 2024-06-08 07:17

import datetime
from django.db import migrations, models
import django.db.models.deletion
import django.utils.crypto
import qs2csv.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ForeignKeyModel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("chars", models.CharField(default="test", max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="TestModel",
            fields=[
                (
                    "pk_field",
                    models.BigAutoField(
                        primary_key=True, serialize=False, verbose_name="Big Auto"
                    ),
                ),
                (
                    "char_field",
                    models.CharField(
                        default=django.utils.crypto.get_random_string,
                        max_length=255,
                        verbose_name="Chars",
                    ),
                ),
                (
                    "big_int_field",
                    models.BigIntegerField(
                        default=qs2csv.models.random_int, verbose_name="Big Integer"
                    ),
                ),
                (
                    "boolean_field",
                    models.BooleanField(default=True, verbose_name="Boolean"),
                ),
                (
                    "date_field",
                    models.DateField(auto_now_add=True, verbose_name="Date"),
                ),
                (
                    "datetime_field",
                    models.DateTimeField(auto_now_add=True, verbose_name="DateTime"),
                ),
                (
                    "decimal_field",
                    models.DecimalField(
                        decimal_places=2,
                        default=qs2csv.models.random_decimal,
                        max_digits=10,
                        verbose_name="Decimal",
                    ),
                ),
                (
                    "duration_field",
                    models.DurationField(
                        default=datetime.timedelta(days=1), verbose_name="Duration"
                    ),
                ),
                (
                    "float_field",
                    models.FloatField(
                        default=qs2csv.models.random_float, verbose_name="Float"
                    ),
                ),
                (
                    "generic_ip_field",
                    models.GenericIPAddressField(
                        default="2a02:42fe::4", verbose_name="Generic IP Address"
                    ),
                ),
                (
                    "json_field",
                    models.JSONField(
                        default=qs2csv.models.random_json, verbose_name="JSON"
                    ),
                ),
                (
                    "text_field",
                    models.TextField(
                        default=qs2csv.models.random_string, verbose_name="Text"
                    ),
                ),
                (
                    "time_field",
                    models.TimeField(auto_now_add=True, verbose_name="Time"),
                ),
                (
                    "uuid_field",
                    models.UUIDField(default=uuid.uuid4, verbose_name="UUID"),
                ),
                (
                    "foreign_key",
                    models.ForeignKey(
                        db_index=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="all_fields_fk_models",
                        to="qs2csv.foreignkeymodel",
                        verbose_name="Foreign Key",
                    ),
                ),
                (
                    "many_to_many_field",
                    models.ManyToManyField(to="qs2csv.ForeignKeyModel"),
                ),
                (
                    "one_to_one_field",
                    models.OneToOneField(
                        db_index=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="all_fields_oto_models",
                        to="qs2csv.foreignkeymodel",
                        verbose_name="OneToOne",
                    ),
                ),
            ],
        ),
    ]
