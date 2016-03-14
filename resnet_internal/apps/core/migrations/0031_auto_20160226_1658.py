# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-26 16:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0030_DATA_create_permission_classes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resnetinternaluser',
            name='ad_groups',
            field=models.ManyToManyField(related_name='users', to='core.ADGroup', verbose_name='AD Groups'),
        ),
    ]
