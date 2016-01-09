# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-26 11:49
from __future__ import unicode_literals

from django.db import migrations
from django.db.migrations.operations.special import RunPython


def update_navbar(apps, schema_editor):
    NavbarLink = apps.get_model('core', 'NavbarLink')
    ADGroup = apps.get_model('core', 'ADGroup')

    csd_group = ADGroup.objects.create(
        display_name="CSD",
        distinguished_name="CN=UH-CSD,OU=Residential Life,OU=UH,OU=Manual,OU=Groups,DC=ad,DC=calpoly,DC=edu"
    )

    ral_group = ADGroup.objects.create(
        display_name="Residential Life Staff",
        distinguished_name="CN=UH-RAL,OU=Residential Life,OU=UH,OU=Manual,OU=Groups,DC=ad,DC=calpoly,DC=edu"
    )

    ral_managers_group = ADGroup.objects.create(
        display_name="Residential Life Managers",
        distinguished_name="CN=UH-RAL-Managers,OU=User Groups,OU=Websites,OU=UH,OU=Manual,OU=Groups,DC=ad,DC=calpoly,DC=edu"
    )

    ra_group = ADGroup.objects.create(
        display_name="RA",
        distinguished_name="CN=UH-RA,OU=Residential Life,OU=UH,OU=Manual,OU=Groups,DC=ad,DC=calpoly,DC=edu"
    )

    fd_staff_group = ADGroup.objects.create(
        display_name="Front Desk Staff",
        distinguished_name="CN=UH-FD-Staff,OU=Front Desk,OU=Residential Life,OU=UH,OU=Manual,OU=Groups,DC=ad,DC=calpoly,DC=edu"
    )

    databases = NavbarLink.objects.filter(display_name="Databases")
    if databases.exists():
        databases = databases.first()
        databases.sequence_index = 3
        databases.save()

    network_administration = NavbarLink.objects.filter(display_name="Network Administration")
    if network_administration.exists():
        network_administration = network_administration.first()
        network_administration.sequence_index = 4
        network_administration.save()

    staff_resources = NavbarLink.objects.filter(display_name="Staff Resources")
    if staff_resources.exists():
        staff_resources = staff_resources.first()
        staff_resources.sequence_index = 5
        staff_resources.save()

    developer_resources = NavbarLink.objects.filter(display_name="Developer Resources")
    if developer_resources.exists():
        developer_resources = developer_resources.first()
        developer_resources.sequence_index = 6
        developer_resources.save()

    reslife_resources = NavbarLink.objects.create(
        display_name="Reslife Resources",
        sequence_index=2
    )
    reslife_resources.groups.add(csd_group, ral_group, ral_managers_group, ra_group, fd_staff_group, 1, 2, 5, 6, 7)  # UH-TAG, UH-TAG-Readonly, UH-RN-Staff, UH-RN-DevTeam, UH-RN-Techs

    roster_generator = NavbarLink.objects.create(
        display_name="Roster Generator",
        sequence_index=0,
        url_name="rosters",
        icon="images/icons/roster.png",
        parent_group=reslife_resources
    )
    roster_generator.groups.add(csd_group, ral_group, ral_managers_group, ra_group, fd_staff_group, 5, 6, 7)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_added_csd_mapping'),
    ]

    operations = [
        #  RunPython(update_navbar),
    ]
