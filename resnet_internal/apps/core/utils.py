"""
.. module:: resnet_internal.apps.core.utils
   :synopsis: ResNet Internal Core Utilities.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

import logging
import os
from copy import deepcopy

from resnet_internal.apps.core.models import NetworkDevice

logger = logging.getLogger(__name__)


class NetworkReachabilityTester:

    def _is_system_reachable(self, system_ip_address):
        response = os.system("ping -c 1 -t 1" + system_ip_address)
        return True if response == 0 else False
    
    def get_network_device_reachability(self):
        reachability_responses = []
        
        network_devices = NetworkDevice.objects.all()
        
        for network_device in network_devices:
            reachability_responses.append({'display_name': network_device.display_name,
                                           'dns_name': network_device.dns_name,
                                           'ip_address': network_device.ip_address,
                                           'status': self._is_system_reachable(network_device.ip_address),
                                           })
        return reachability_responses


def dict_merge(base, merge):
    """ Recursively merges dictionaries.

    :param base: The base dictionary.
    :type base: dict
    :param merge: The dictionary to merge with base.
    :type merge: dict

    """

    if not isinstance(merge, dict):
        return merge
    result = deepcopy(base)

    for key, value in merge.items():
        if key in result and isinstance(result[key], dict):
                result[key] = dict_merge(result[key], value)
        else:
            result[key] = deepcopy(value)

    return result
