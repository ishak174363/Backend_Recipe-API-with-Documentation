# Generated by Django 5.1.1 on 2024-09-18 16:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_recipe"),
    ]

    operations = [
        migrations.RenameField(
            model_name="recipe",
            old_name="descriptions",
            new_name="description",
        ),
    ]
