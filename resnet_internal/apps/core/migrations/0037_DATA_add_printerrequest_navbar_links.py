# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-13 16:17
from __future__ import unicode_literals

from django.db import migrations
from django.db.migrations.operations.special import RunPython

from ....settings.base import PRINTER_REQUEST_CREATE_ACCESS


def add_navbar_item(apps, schema_editor):
    PermissionClass = apps.get_model('core', 'PermissionClass')
    NavbarLink = apps.get_model('core', 'NavbarLink')

    reslife_resources = NavbarLink.objects.filter(display_name="Reslife Resources")
    if reslife_resources.exists():
        reslife_resources = reslife_resources.first()

        # Add the printer requests view link
        my_printer_requests = NavbarLink.objects.create(
            display_name="My Printer Requests",
            sequence_index=3,
            url_name="printerrequests:home",
            icon="images/icons/printer.png",
            parent_group=reslife_resources
        )

        # Add the toner request sublink
        request_toner = NavbarLink.objects.create(
            display_name="Request Toner",
            sequence_index=0,
            url_name="printerrequests:toner_request",
            parent_group=my_printer_requests
        )

        # Add the parts request sublink
        request_parts = NavbarLink.objects.create(
            display_name="Request Parts",
            sequence_index=1,
            url_name="printerrequests:parts_request",
            parent_group=my_printer_requests
        )

        try:
            permission_class = PermissionClass.objects.get(name=PRINTER_REQUEST_CREATE_ACCESS)
        except PermissionClass.DoesNotExist:
            pass
        else:
            my_printer_requests.permission_classes.add(permission_class)
            request_toner.permission_classes.add(permission_class)
            request_parts.permission_classes.add(permission_class)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0036_DATA_fix_printers_modify_permission'),
    ]

    operations = [
        RunPython(add_navbar_item),
    ]
