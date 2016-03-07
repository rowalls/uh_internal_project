"""
.. module:: resnet_internal.urls
   :synopsis: University Housing Internal URLs.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>
.. moduleauthor:: RJ Almada <almada.dev@gmail.com>

"""

import logging

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.staticfiles.templatetags.staticfiles import static as staticfiles
from django.core.exceptions import PermissionDenied
from django.views.decorators.cache import cache_page
from django.views.defaults import permission_denied, page_not_found
from django.views.generic import RedirectView
from django_cas_ng.views import login as auth_login, logout as auth_logout
from django_js_reverse.views import urls_js

from .apps.adgroups.ajax import remove_resnet_tech
from .apps.adgroups.views import ResTechListEditView
from .apps.computers.ajax import PopulateComputers, UpdateComputer, remove_pinhole, remove_domain_name, RemoveComputer, RetrieveComputerForm
from .apps.computers.views import ComputersView, ComputerRecordsView, RDPRequestView, PinholeRequestView, DomainNameRequestView
from .apps.core.ajax import update_network_status, get_tickets, BuildingChainedAjaxView, RoomChainedAjaxView, SubDepartmentChainedAjaxView, PopulateRooms, UpdateRoom, RemoveRoom, RetrieveRoomForm, update_csd_domain
from .apps.core.views import IndexView, handler500, TicketSummaryView, RoomsView, CSDDomainAssignmentEditView
from .apps.dailyduties.ajax import refresh_duties, update_duty, remove_voicemail, get_email_folders, get_mailbox_summary, email_mark_unread, email_mark_read, email_archive, send_email, attachment_upload, attachment_delete, ticket_from_email, get_csd_email
from .apps.dailyduties.views import VoicemailListView, VoicemailAttachmentRequestView, EmailMessageView, EmailListView, EmailAttachmentRequestView, EmailComposeView
from .apps.orientation.ajax import complete_task, complete_orientation
from .apps.orientation.views import ChecklistView, OnityDoorAccessView, SRSAccessView, PayrollView
from .apps.portmap.ajax import PopulatePorts, UpdatePort, change_port_status, PortChainedAjaxView, PopulateAccessPoints, UpdateAccessPoint, RemovePort, RemoveAccessPoint, RetrievePortForm, RetrieveAccessPointForm
from .apps.portmap.views import PortsView, AccessPointsView, PortFrameView, AccessPointFrameView
from .apps.printerrequests.ajax import change_request_status, update_part_inventory, update_toner_inventory
from .apps.printerrequests.views import RequestsListView, InventoryView, OnOrderView
from .apps.printers.ajax import PopulatePrinters, UpdatePrinter, RemovePrinter, RetrievePrinterForm
from .apps.printers.views import PrintersView
from .apps.residents.views import SearchView
from .apps.rosters.views import RosterGenerateView
from .settings.base import TICKET_ACCESS, ROOMS_ACCESS, ROOMS_MODIFY_ACCESS, DAILY_DUTIES_ACCESS, TECHNICIAN_LIST_ACCESS, NETWORK_ACCESS, NETWORK_MODIFY_ACCESS, COMPUTERS_RECORD_MODIFY_ACCESS, CSD_ASSIGNMENT_ACCESS, ORIENTATION_ACCESS, COMPUTERS_ACCESS, PRINTERS_ACCESS, COMPUTERS_MODIFY_ACCESS, PRINTERS_MODIFY_ACCESS, ROSTER_ACCESS


def permissions_check(class_name, raise_exception=True):
    """
    Decorator for views that checks whether a user has permission to view the
    requested page, redirecting to the log-in page if necessary.
    If the raise_exception parameter is given the PermissionDenied exception
    is raised.

    :param group_list: A list of group display names that should be allowed in.
    :type group_list: list
    :param raise_exception: Determines whether or not to throw an exception when permissions test fails.
    :type raise_exception: bool

    """

    def check_perms(user):
        # First check if the user has the permission (even anon users)
        if user.has_access(class_name):
            return True
        # In case the 403 handler should be called raise the exception
        if raise_exception:
            raise PermissionDenied
        # As the last resort, show the login form
        return False
    return user_passes_test(check_perms)

ticket_access = permissions_check(TICKET_ACCESS)
rooms_access = permissions_check(ROOMS_ACCESS)
rooms_modify_access = permissions_check(ROOMS_MODIFY_ACCESS)
daily_duties_access = permissions_check(DAILY_DUTIES_ACCESS)
orientation_access = permissions_check(ORIENTATION_ACCESS)
technician_list_access = permissions_check(TECHNICIAN_LIST_ACCESS)

network_access = permissions_check(NETWORK_ACCESS)
network_modify_access = permissions_check(NETWORK_MODIFY_ACCESS)

computers_access = permissions_check(COMPUTERS_ACCESS)
computers_modify_access = permissions_check(COMPUTERS_MODIFY_ACCESS)
computer_record_modify_access = permissions_check(COMPUTERS_RECORD_MODIFY_ACCESS)

printers_access = permissions_check(PRINTERS_ACCESS)
printers_modify_access = permissions_check(PRINTERS_MODIFY_ACCESS)

csd_assignment_access = permissions_check(CSD_ASSIGNMENT_ACCESS)
roster_access = permissions_check(ROSTER_ACCESS)


handler500 = handler500

logger = logging.getLogger(__name__)

# Core
urlpatterns = [
    url(r'^$', IndexView.as_view(), name='home'),
    url(r'^favicon\.ico$', RedirectView.as_view(url=staticfiles('images/icons/favicon.ico'), permanent=True), name='favicon'),
    url(r'^flugzeug/', include(admin.site.urls)),  # admin site urls, masked
    url(r'^login/$', auth_login, name='login'),
    url(r'^logout/$', auth_logout, name='logout', kwargs={'next_page': settings.CAS_LOGOUT_URL}),

    url(r'^jsreverse/$', cache_page(3600)(urls_js), name='js_reverse'),

    url(r'^ajax/chained_building/$', BuildingChainedAjaxView.as_view(), name='core_chained_building'),
    url(r'^ajax/chained_room/$', RoomChainedAjaxView.as_view(), name='core_chained_room'),
    url(r'^ajax/chained_sub_department/$', SubDepartmentChainedAjaxView.as_view(), name='core_chained_sub_department'),

    url(r'^core/network_status/update/$', update_network_status, name='core_update_network_status'),

    url(r'^core/tickets/list/$', login_required(ticket_access(get_tickets)), name='core_get_tickets'),
    url(r'^core/tickets/list/(?P<ticket_id>\b[0-9]*\b)/$', login_required(ticket_access(TicketSummaryView.as_view())), name='core_ticket_summary'),

    url(r'^rooms/$', login_required(rooms_access(RoomsView.as_view())), name='rooms'),
    url(r'^rooms/populate/$', login_required(rooms_access(PopulateRooms.as_view())), name='populate_rooms'),
    url(r'^rooms/update/$', login_required(rooms_modify_access(UpdateRoom.as_view())), name='update_room'),

    url(r'^rooms/remove/$', login_required(rooms_modify_access(RemoveRoom.as_view())), name='remove_room'),
    url(r'^rooms/form/$', login_required(rooms_modify_access(RetrieveRoomForm.as_view())), name='form_room'),

    url(r'^csd/assign_domain/$', login_required(csd_assignment_access(CSDDomainAssignmentEditView.as_view())), name='csd_assign_domain'),
    url(r'^csd/assign_domain/update/$', login_required(csd_assignment_access(update_csd_domain)), name='update_csd_domain'),

]

# Daily Duties
urlpatterns += [
    url(r'^daily_duties/email/list/$', login_required(daily_duties_access(EmailListView.as_view())), name='email_list'),
    url(r'^daily_duties/email/view/(?P<mailbox_name>.+)/(?P<uid>[0-9]+)/$', login_required(daily_duties_access(EmailMessageView.as_view())), name='email_view_message'),
    url(r'^daily_duties/email/compose/$', login_required(daily_duties_access(EmailComposeView.as_view())), name='email_compose'),
    url(r'^daily_duties/email/mark_unread/$', login_required(daily_duties_access(email_mark_unread)), name='email_mark_unread'),
    url(r'^daily_duties/email/mark_read/$', login_required(daily_duties_access(email_mark_read)), name='email_mark_read'),
    url(r'^daily_duties/email/archive$', login_required(daily_duties_access(email_archive)), name='email_archive'),
    url(r'^daily_duties/email/get_attachment/(?P<mailbox_name>.+)/(?P<uid>[0-9]+)/(?P<attachment_index>[0-9]+)/$', login_required(daily_duties_access(EmailAttachmentRequestView.as_view())), name='email_get_attachment'),
    url(r'^daily_duties/email/get_attachment/(?P<mailbox_name>.+)/(?P<uid>[0-9]+)/(?P<content_id>[^<>]+)/$', login_required(daily_duties_access(EmailAttachmentRequestView.as_view())), name='email_get_attachment'),
    url(r'^daily_duties/email/get_folders/$', login_required(daily_duties_access(get_email_folders)), name='email_get_folders'),
    url(r'^daily_duties/email/get_mailbox_summary/(?P<mailbox_name>.*)/(?P<search_string>.*)/(?P<message_group>[0-9]+)/$', login_required(daily_duties_access(get_mailbox_summary)), name='email_get_mailbox_summary_range'),
    url(r'^daily_duties/email/get_mailbox_summary/(?P<mailbox_name>.*)/(?P<search_string>.*)/$', login_required(daily_duties_access(get_mailbox_summary)), name='email_get_mailbox_summary'),
    url(r'^daily_duties/email/send_email/$', login_required(daily_duties_access(send_email)), name='send_email'),
    url(r'^daily_duties/email/upload_attachment/$', daily_duties_access(attachment_upload), name='jfu_upload'),
    url(r'^daily_duties/email/delete_attachment/(?P<pk>.+)$', daily_duties_access(attachment_delete), name='jfu_delete'),
    url(r'^daily_duties/email/cc_csd/$', daily_duties_access(get_csd_email), name='email_get_cc_csd'),

    url(r'^daily_duties/voicemail_list/$', login_required(daily_duties_access(VoicemailListView.as_view())), name='voicemail_list'),
    url(r'^daily_duties/refresh_duties/$', login_required(daily_duties_access(refresh_duties)), name='daily_duties_refresh_duties'),
    url(r'^daily_duties/update_duty/$', login_required(daily_duties_access(update_duty)), name='daily_duties_update_duty'),
    url(r"^daily_duties/voicemail/(?P<message_uid>\b[0-9]+\b)/$", login_required(daily_duties_access(VoicemailAttachmentRequestView.as_view())), name='voicemail_attachment_request'),
    url(r"^daily_duties/remove_voicemail/$", login_required(daily_duties_access(remove_voicemail)), name='remove_voicemail'),
    url(r"^daily_duties/create_ticket_from_email/$", login_required(daily_duties_access(ticket_from_email)), name='email_create_ticket'),
]

# ResNet Technician Orientation
urlpatterns += [
    url(r'^orientation/$', login_required(orientation_access(ChecklistView.as_view())), name='orientation_checklist'),
    url(r'^orientation/payroll/$', login_required(orientation_access(PayrollView.as_view())), name='orientation_payroll'),
    url(r'^orientation/onity/$', login_required(orientation_access(OnityDoorAccessView.as_view())), name='orientation_onity'),
    url(r'^orientation/srs/$', login_required(orientation_access(SRSAccessView.as_view())), name='orientation_srs'),
    url(r'^orientation/complete_task/$', login_required(orientation_access(complete_task)), name='orientation_complete_task'),
    url(r'^orientation/complete_orientation/$', login_required(orientation_access(complete_orientation)), name='orientation_complete'),
]

# AD Group management
urlpatterns += [
    url(r'^technicians/$', login_required(technician_list_access(ResTechListEditView.as_view())), name='restech_list_edit'),
    url(r'^technicians/remove/$', login_required(technician_list_access(remove_resnet_tech)), name='remove_resnet_tech'),
]

# Computers
urlpatterns += [
    url(r'^computers/$', login_required(computers_access(ComputersView.as_view())), name='computers'),
    url(r'^computers/populate/$', login_required(computers_access(PopulateComputers.as_view())), name='populate_computers'),
    url(r'^computers/update/$', login_required(computers_modify_access(UpdateComputer.as_view())), name='update_computer'),
    url(r'^computers/form/$', login_required(computers_modify_access(RetrieveComputerForm.as_view())), name='form_computer'),
    url(r'^computers/remove/$', login_required(computers_modify_access(RemoveComputer.as_view())), name='remove_computer'),
    url(r'^computers/remove_pinhole/$', login_required(computer_record_modify_access(remove_pinhole)), name='remove_computer_pinhole'),
    url(r'^computers/remove_domain_name/$', login_required(computer_record_modify_access(remove_domain_name)), name='remove_computer_domain_name'),
    url(r'^computers/(?P<ip_address>\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b)/$', login_required(computers_access(ComputerRecordsView.as_view())), name='view_computer_record'),
    url(r'^computers/(?P<ip_address>\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b)/rdp/$', login_required(computers_access(RDPRequestView.as_view())), name='rdp_request'),
    url(r'^computers/(?P<ip_address>\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b)/pinhole_request/$', login_required(computer_record_modify_access(PinholeRequestView.as_view())), name='pinhole_request'),
    url(r'^computers/(?P<ip_address>\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b)/domain_name_request/$', login_required(computer_record_modify_access(DomainNameRequestView.as_view())), name='domain_name_request'),
]

# Printer Requests
urlpatterns += [
    url(r'^printers/requests/list/', login_required(daily_duties_access(RequestsListView.as_view())), name='printer_request_list'),
    url(r'^printers/requests/view_inventory/', login_required(daily_duties_access(InventoryView.as_view())), name='printer_inventory'),
    url(r'^printers/requests/view_ordered/', login_required(daily_duties_access(OnOrderView.as_view())), name='printer_ordered_items'),
    url(r'^printers/requests/change_status/', login_required(daily_duties_access(change_request_status)), name='change_printer_request_status'),
    url(r'^printers/requests/toner/update_inventory/', login_required(daily_duties_access(update_toner_inventory)), name='update_printer_toner_inventory'),
    url(r'^printers/requests/parts/update_inventory/', login_required(daily_duties_access(update_part_inventory)), name='update_printer_part_inventory'),
]

# Printers
urlpatterns += [
    url(r'^printers/$', login_required(printers_access(PrintersView.as_view())), name='printers'),
    url(r'^printers/populate/$', login_required(printers_access(PopulatePrinters.as_view())), name='populate_printers'),
    url(r'^printers/update/$', login_required(printers_modify_access(UpdatePrinter.as_view())), name='update_printer'),
    url(r'^printers/form/$', login_required(printers_access(RetrievePrinterForm.as_view())), name='form_printer'),
    url(r'^printers/remove/$', login_required(printers_modify_access(RemovePrinter.as_view())), name='remove_printer'),
]

# Network
urlpatterns += [
    url(r'^ports/$', login_required(network_access(PortsView.as_view())), name='ports'),
    url(r'^ports/populate/$', login_required(network_access(PopulatePorts.as_view())), name='populate_ports'),
    url(r'^ports/update/$', login_required(network_modify_access(UpdatePort.as_view())), name='update_port'),
    url(r'^ports/form/$', login_required(network_access(RetrievePortForm.as_view())), name='form_port'),
    url(r'^ports/change_status/$', login_required(network_modify_access(change_port_status)), name='change_port_status'),
    url(r'^ports/remove/$', login_required(network_modify_access(RemovePort.as_view())), name='remove_port'),

    url(r'^ports/info_frame/(?P<pk>\b[0-9]+\b)/$', login_required(network_access(PortFrameView.as_view())), name='port_info_frame'),
    url(r'^ports/ajax/chained_port/$', PortChainedAjaxView.as_view(), name='ports_chained_port'),

    url(r'^access-points/$', login_required(network_access(AccessPointsView.as_view())), name='access_points'),
    url(r'^access-points/populate/$', login_required(network_access(PopulateAccessPoints.as_view())), name='populate_access_points'),
    url(r'^access-points/update/$', login_required(network_modify_access(UpdateAccessPoint.as_view())), name='update_access_point'),
    url(r'^access-points/form/$', login_required(network_access(RetrieveAccessPointForm.as_view())), name='form_access_point'),
    url(r'^access-points/remove/$', login_required(network_modify_access(RemoveAccessPoint.as_view())), name='remove_access_point'),
    url(r'^access-points/info_frame/(?P<pk>\b[0-9]+\b)/$', login_required(network_access(AccessPointFrameView.as_view())), name='access_point_info_frame'),
]

# Roster Generator
urlpatterns += [
    url(r'^rosters/$', login_required(RosterGenerateView.as_view()), name='rosters')
]

# Resident Lookup
urlpatterns += [
    url(r'^residents/$', login_required(SearchView.as_view()), name='resident_lookup'),
]

# Raise errors on purpose
urlpatterns += [
    url(r'^500/$', handler500),
    url(r'^403/$', permission_denied),
    url(r'^404/$', page_not_found),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
