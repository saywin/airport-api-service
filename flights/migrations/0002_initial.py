# Generated by Django 5.0.6 on 2024-06-23 15:20

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("flights", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="route",
            name="destination",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="destination_routes",
                to="flights.airport",
            ),
        ),
        migrations.AddField(
            model_name="route",
            name="source",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="source_routes",
                to="flights.airport",
            ),
        ),
        migrations.AddField(
            model_name="flight",
            name="route",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="flights",
                to="flights.route",
            ),
        ),
        migrations.AddField(
            model_name="ticket",
            name="flight",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="flights.flight"
            ),
        ),
        migrations.AddField(
            model_name="ticket",
            name="order",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="flights.order"
            ),
        ),
    ]
