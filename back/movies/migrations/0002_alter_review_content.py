# Generated by Django 4.2.16 on 2024-11-25 02:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='content',
            field=models.TextField(blank=True, max_length=250, null=True),
        ),
    ]
