"""
.. module:: resnet_internal.apps.portmap.forms
   :synopsis: ResNet Internal Portmap Forms.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from django.forms import ModelForm

from .models import ResHallWired


class ResHallWiredPortCreateForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(ResHallWiredPortCreateForm, self).__init__(*args, **kwargs)

        for field_name in self.fields:
            self.fields[field_name].error_messages = {'required': 'A ' + field_name + ' is required.'}

    class Meta:
        model = ResHallWired
        fields = ['id', 'room', 'switch_ip', 'switch_name', 'jack', 'blade', 'port', 'vlan']


class ResHallWiredPortUpdateForm(ResHallWiredPortCreateForm):

    class Meta:
        fields = ['id', 'switch_ip', 'switch_name', 'blade', 'port', 'vlan']
