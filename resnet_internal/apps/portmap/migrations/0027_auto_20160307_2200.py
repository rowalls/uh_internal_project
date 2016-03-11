# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-03-07 22:00
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import resnet_internal.apps.computers.fields


class Migration(migrations.Migration):

    dependencies = [
        ('portmap', '0026_auto_20160224_1044'),
    ]

    operations = [
        migrations.AlterField(
            model_name='networkdevice',
            name='dns_name',
            field=models.CharField(blank=True, max_length=75, null=True, verbose_name='DNS Name'),
        ),
        migrations.AlterField(
            model_name='networkdevice',
            name='ip_address',
            field=models.GenericIPAddressField(blank=True, null=True, protocol='IPv4', verbose_name='IP Address'),
        ),
        migrations.AlterField(
            model_name='networkdevice',
            name='mac_address',
            field=resnet_internal.apps.computers.fields.MACAddressField(blank=True, max_length=17, null=True, verbose_name='MAC Address'),
        ),
        migrations.AlterField(
            model_name='networkdevice',
            name='room',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Room', verbose_name='Room'),
        ),
        migrations.AlterField(
            model_name='networkdevice',
            name='upstream_device',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='downstream_devices', to='portmap.NetworkDevice'),
        ),
    ]
