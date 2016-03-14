# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-26 11:26
from __future__ import unicode_literals

from django.db import migrations


def create_network_devices_from_computers(apps, schema_editor):
    NetworkDevice = apps.get_model('portmap', 'NetworkDevice')
    Computer = apps.get_model('computers', 'Computer')

    for computer in Computer.objects.all():
        network_device = NetworkDevice()
        network_device.display_name = computer.computer_name
        network_device.dns_name = computer.computer_name.strip() + '.ad.calpoly.edu'
        network_device.ip_address = computer.ip_address
        network_device.mac_address = computer.mac_address
        network_device.save()


class Migration(migrations.Migration):

    dependencies = [
        ('computers', '0007_auto_20151220_1226'),
    ]

    operations = [
        migrations.RunPython(create_network_devices_from_computers)
    ]
