"""
.. module:: resnet_internal.apps.core.context_processors
   :synopsis: University Housing Internal Core Context Processors.

.. moduleauthor:: Alex Kavanaugh <alex@kavdev.io>

"""

from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.cache import cache
from django.db.models import Q

from ...settings.base import ORIENTATION_ACCESS
from .models import TechFlair, NavbarLink


def specializations(request):
    """Adds the user's specialization titles and display name to each context request."""

    extra_context = {}

    display_name = None
    user_specializations = []

    if request.user.is_authenticated and not request.is_ajax():
        display_name = request.user.get_full_name()

        for group in request.user.ad_groups.all():
            user_specializations.append(group.display_name)

        try:
            tech_flair = TechFlair.objects.get(tech=request.user)
        except TechFlair.DoesNotExist:
            pass
        else:
            user_specializations.append(tech_flair.flair)

        if "akavanau" in request.user.username:
            user_specializations.append('ResNet Development Team BDFL')

        # User is new technician (requires orientation)
        if request.user.has_access(ORIENTATION_ACCESS) and not request.user.orientation_complete:
            user_specializations = ['New ResNet Technician']

    # Set context
    extra_context['user_display_name'] = display_name
    extra_context['user_specializations'] = user_specializations

    return extra_context


def navbar(request):
    if request.user.is_authenticated and not request.is_ajax():
        cache_key = request.user.username + ':navbar'

        navbar = cache.get(cache_key)

        if not navbar:
            links_for_user = NavbarLink.objects.filter(Q(permission_classes__groups__users__id=request.user.id) | Q(show_to_all=True)).distinct()
            navbar = ''

            def a_inner_html(link):
                return '<img class="link-icon" aria-hidden="true" src="{icon_url}" height="16" width="16"><span id="{link_id}_text">{link_name}</span>'.format(icon_url=static(link.icon),
                                                                                                                                                               link_name=link.display_name,
                                                                                                                                                               link_id=link.html_id)

            for parent_link in links_for_user.filter(parent_group__isnull=True).order_by('sequence_index'):
                navbar += '<div class="link-group-heading">{link_name}</div>\n'.format(link_name=parent_link.display_name)
                navbar += '<div class="link-group">\n'
                navbar += '<ul>\n'

                for link in links_for_user.filter(parent_group__id=parent_link.id).order_by('sequence_index'):

                    if link.is_link_group:
                        collapsable = not link.onclick
                        onclick = not link.url

                        navbar += '<li>'

                        onclick_text = 'onclick="{onclick}"'.format(onclick=link.onclick if not collapsable else "$('#{link_id}_list').collapse('toggle')".format(link_id=link.html_id))
                        href_text = 'href="{link_url}"'.format(link_url=link.url)

                        navbar += '<a id="{link_id}_link" class="{link_classes}" {link_action}>{inner_html}'.format(link_id=link.html_id,
                                                                                                                    link_classes="collapsable-trigger" if collapsable else "",
                                                                                                                    link_action=onclick_text if onclick else href_text,
                                                                                                                    inner_html=a_inner_html(link))

                        # Collapsable identifier
                        navbar += '&nbsp<span class="glyphicon" aria-hidden="true"></span>' if collapsable else ''

                        navbar += '</a>\n'
                        navbar += '</li>\n'

                        # Collapsed sublinks
                        navbar += '<ul id="{sublink_container_id}_list" class="{sublink_container_classes}">\n'.format(sublink_container_id=link.html_id, sublink_container_classes='collapse collapsable' if onclick and collapsable else '')

                        for sublink in links_for_user.filter(parent_group__id=link.id).order_by('sequence_index'):
                            navbar += '<li>'

                            onclick_text = 'onclick="{onclick}"'.format(onclick=sublink.onclick) if sublink.onclick else ''
                            href_text = ' href="{link_url}"'.format(link_url=sublink.url) if sublink.url else ''

                            navbar += '<a {onclick}{href} target="{target}">{sublink_name}</a>'.format(onclick=onclick_text,
                                                                                                       href=href_text,
                                                                                                       target=sublink.target,
                                                                                                       sublink_name=sublink.display_name)

                            navbar += '</li>\n'

                        navbar += '</ul>\n'
                    else:
                        navbar += '<li>'

                        onclick_text = 'onclick="{onclick}"'.format(onclick=link.onclick) if link.onclick else ''
                        href_text = ' href="{link_url}"'.format(link_url=link.url) if link.url else ''

                        navbar += '<a id="{link_id}_link" {onclick}{href} target="{target}">{inner_html}</a>\n'.format(link_id=link.html_id,
                                                                                                                       onclick=onclick_text,
                                                                                                                       href=href_text,
                                                                                                                       target=link.target,
                                                                                                                       inner_html=a_inner_html(link))
                        navbar += '</li>\n'

                navbar += '</ul>\n'
                navbar += '</div>\n'

            cache.set(cache_key, navbar, 60 * 60 * 4)

        return {'navbar': navbar}
    else:
        return {}
