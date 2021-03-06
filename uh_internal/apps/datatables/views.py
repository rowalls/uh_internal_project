"""
.. module:: resnet_internal.apps.datatables.views
   :synopsis: University Housing Internal Datatable Views.

.. moduleauthor:: Alex Kavanaugh <alex@kavdev.io>
.. moduleauthor:: RJ Almada <almada.dev@gmail.com>


"""

from django.core.exceptions import ImproperlyConfigured
from django.views.generic.edit import CreateView

from ..datatables.ajax import RNINDatatablesPopulateView


class DatatablesView(CreateView):
    populate_class = None

    def __init__(self, **kwargs):
        super(DatatablesView, self).__init__(**kwargs)

        if not issubclass(self.populate_class, RNINDatatablesPopulateView):
            raise ImproperlyConfigured("The populate_class instance variable is either not set or is not a subclass of RNINDatatablesPopulateView.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["datatables_class"] = self.populate_class
        context.update(self.populate_class(request=self.request).get_context_data())
        return context
