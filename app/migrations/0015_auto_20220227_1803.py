# Generated by Django 3.1 on 2022-02-27 18:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0014_remove_bill_bill_cnote_range'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bill',
            name='bill_no',
            field=models.IntegerField(),
        ),
    ]
