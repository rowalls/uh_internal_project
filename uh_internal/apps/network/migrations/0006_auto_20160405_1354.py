# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-05 13:54
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0005_auto_20160405_1336'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clearpassloginattempt',
            name='enforcement_profiles',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), size=None),
        ),
        migrations.AlterField(
            model_name='clearpassloginattempt',
            name='service',
            field=models.CharField(max_length=100),
        ),
    ]
