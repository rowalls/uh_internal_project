"""
.. module:: resnet_internal.apps.core.models
   :synopsis: University Housing Internal Core Models.

.. moduleauthor:: Alex Kavanaugh <alex@kavdev.io>

"""

import logging
import re

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, UserManager, PermissionsMixin
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db.models.base import Model
from django.db.models.deletion import CASCADE
from django.db.models.fields import (CharField, TextField, DateTimeField, EmailField, BooleanField,
                                     URLField, SmallIntegerField, PositiveSmallIntegerField)
from django.db.models.fields.related import ForeignKey, ManyToManyField
from django.urls import reverse, NoReverseMatch
from django.utils import timezone
from django.utils.functional import cached_property
from ldap_groups.exceptions import InvalidGroupDN
from ldap_groups.groups import ADGroup as LDAPADGroup


logger = logging.getLogger(__name__)


class Community(Model):

    name = CharField(max_length=30, verbose_name="Community Name")

    def __str__(self):
        return self.name

    @cached_property
    def address(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Communities'


class Building(Model):

    name = CharField(max_length=30, verbose_name="Building Name")
    community = ForeignKey(Community, verbose_name="Community",
                           related_name="buildings", on_delete=CASCADE)

    def __str__(self):
        return self.name

    @cached_property
    def address(self):
        return self.community.address + ' ' + self.name


class Room(Model):

    name = CharField(max_length=10, verbose_name="Room Number")
    building = ForeignKey(Building, verbose_name="Building",
                          related_name="rooms", on_delete=CASCADE)

    def __str__(self):
        return self.name

    @cached_property
    def community(self):
        return self.building.community

    @cached_property
    def address(self):
        return self.building.address + ' ' + self.name

    def save(self, *args, **kwargs):
        # Upper name letters
        for field_name in ['name']:
            value = getattr(self, field_name, None)
            if value:
                setattr(self, field_name, value.upper())

        super(Room, self).save(*args, **kwargs)


class Department(Model):

    name = CharField(max_length=50, verbose_name='Department Name')

    def __str__(self):
        return self.name


class SubDepartment(Model):

    name = CharField(max_length=50, verbose_name='Sub Department Name')
    department = ForeignKey(Department,
                            verbose_name="Department",
                            null=True,
                            related_name="sub_departments",
                            on_delete=CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Sub Department'


class ADGroup(Model):
    distinguished_name = CharField(max_length=250, unique=True, verbose_name='Distinguished Name')
    display_name = CharField(max_length=50, verbose_name='Display Name')

    def clean(self):
        try:
            LDAPADGroup(self.distinguished_name).get_tree_members()
        except InvalidGroupDN:
            raise ValidationError('Invalid Group Distinguished Name. Please verify.')

    def __str__(self):
        return self.display_name

    class Meta:
        verbose_name = 'AD Group'


class PermissionClass(Model):
    name = CharField(max_length=50, verbose_name='Class Name', unique=True)
    groups = ManyToManyField(ADGroup, related_name='permissionclasses', verbose_name='AD Groups')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'permission classes'


class StaffMapping(Model):
    """A mapping of various department staff to their respective positions."""

    title = CharField(max_length=50, unique=True, verbose_name='Title')
    name = CharField(max_length=50, verbose_name='Full Name')
    email = CharField(max_length=20, verbose_name='Email Address')
    extension = PositiveSmallIntegerField(verbose_name='Telephone Extension')

    class Meta:
        verbose_name = 'Campus Staff Mapping'


class CSDMapping(Model):
    """A mapping of a csd to their controlled buildings."""

    name = CharField(max_length=50, verbose_name='Full Name')
    email = CharField(max_length=20, verbose_name='Email')
    domain = CharField(max_length=35, unique=True, verbose_name='Domain')
    buildings = ManyToManyField(Building, related_name="csdmappings",
                                verbose_name="Domain Buildings")
    ad_group = ForeignKey(ADGroup, verbose_name='Domain AD Group',
                          on_delete=CASCADE)

    def __str__(self):
        return self.domain

    class Meta:
        verbose_name = 'CSD Domain Mapping'


class InternalUserManager(UserManager):

    def _create_user(self, username, email, password, is_staff, is_superuser, **extra_fields):
        now = timezone.now()

        if not username:
            raise ValueError('The given username must be set.')

        email = self.normalize_email(email)
        username = self.normalize_email(username)

        user = self.model(username=username, email=email, is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser, last_login=now, **extra_fields)
        user.set_password("!")
        user.save(using=self._db)

        return user


class UHInternalUser(AbstractBaseUser, PermissionsMixin):
    """University Housing Internal User Model"""

    username = CharField(max_length=30, unique=True, verbose_name='Username')
    first_name = CharField(max_length=30, blank=True, verbose_name='First Name')
    last_name = CharField(max_length=30, blank=True, verbose_name='Last Name')
    email = EmailField(blank=True, verbose_name='Email Address')
    ad_groups = ManyToManyField(ADGroup, verbose_name='AD Groups', related_name='users')

    is_active = BooleanField(default=True)
    is_staff = BooleanField(default=False)

    USERNAME_FIELD = 'username'
    objects = InternalUserManager()

    #
    # A set of flags that keeps a record of each user's orientation progress.
    #
    onity_complete = BooleanField(default=False)  # Onity Door access
    srs_complete = BooleanField(default=False)  # SRS Manager access
    payroll_complete = BooleanField(default=False)  # Payroll access
    orientation_complete = BooleanField(default=False)  # Promotes user to Technician status

    class Meta:
        verbose_name = 'University Housing Internal User'

    def get_full_name(self):
        """Returns the first_name combined with the last_name
           separated with a space with the possible '- ADMIN' removed."""

        full_name = '%s %s' % (self.first_name, re.sub(r' - ADMIN', '', self.last_name))
        return full_name.strip()

    def get_alias(self):
        """Returns the username with the possible '-admin' and '@calpoly.edu' removed."""

        return self.username.replace('-admin', '').replace('@calpoly.edu', '')

    def get_short_name(self):
        "Returns the short name for the user."

        return self.get_alias()

    def email_user(self, subject, message, from_email=None):
        """Sends an email to this user."""

        send_mail(subject, message, from_email, [self.email])

    def has_access(self, class_name):
        cache_key = 'has_access:' + self.username + ':' + class_name
        result = cache.get(cache_key, None)

        if result is None:
            result = self.ad_groups.all().filter(permissionclasses__name=class_name).exists()
            cache.set(cache_key, result, 4 * 60 * 60)

        return result


class TechFlair(Model):
    """A mapping of users to custom flair."""

    tech = ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Technician', on_delete=CASCADE)
    flair = CharField(max_length=30, unique=True, verbose_name='Flair')

    class Meta:
        verbose_name = 'Tech Flair'
        verbose_name_plural = 'Tech Flair'


class NavbarLink(Model):
    display_name = CharField(max_length=50, verbose_name='Display Name')
    permission_classes = ManyToManyField(PermissionClass,
                                         verbose_name='Permission Classes', blank=True)
    show_to_all = BooleanField(verbose_name='Show To All Users', default=False)
    icon = CharField(max_length=100, verbose_name='Icon Static File Location',
                     blank=True, null=True)
    sequence_index = SmallIntegerField(verbose_name='Sequence Index')
    parent_group = ForeignKey('NavbarLink', related_name='links', blank=True, null=True,
                              verbose_name='Parent Link Group', on_delete=CASCADE)

    external_url = URLField(verbose_name='URL', blank=True, null=True)
    url_name = CharField(max_length=100, blank=True, null=True)
    onclick = CharField(max_length=200, blank=True, null=True, verbose_name='Onclick Handler')

    def __str__(self):
        return self.display_name

    def clean(self):
        if self.url_name and self.external_url:
            raise ValidationError('Navbar Links should have either a url name or an external url, not both.')

        if self.url_name:
            try:
                reverse(self.url_name)
            except NoReverseMatch:
                raise ValidationError('URL Name could not be resolved. Please enter a valid URL Name.')

    @cached_property
    def url(self):
        url = ''

        if self.url_name:
            try:
                url = reverse(self.url_name)
            except NoReverseMatch:
                logger.warning('Could not resolve ``' + self.url_name +
                               '`` for navbar link ' + self.display_name,
                               exc_info=True)
                pass
        else:
            url = self.external_url

        return url

    @cached_property
    def is_link_group(self):
        return NavbarLink.objects.filter(parent_group__id=self.id).exists()

    @cached_property
    def html_id(self):
        return self.display_name.lower().replace(' ', '_')

    @cached_property
    def target(self):
        return '_blank' if self.external_url else '_self'
