# Generated by Django 2.1.7 on 2019-03-29 05:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduleUs', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='description',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]
