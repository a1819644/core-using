"""
security.py: defines security services (vpnclient, vpnserver, ipsec and
firewall)
"""

import logging
from typing import Tuple

from core import constants
from core.nodes.base import CoreNode
from core.nodes.interface import CoreInterface
from core.services.coreservices import CoreService


class VPNClient(CoreService):
    name: str = "VPNClient"
    group: str = "Security"
    configs: Tuple[str, ...] = ("vpnclient.sh",)
    startup: Tuple[str, ...] = ("sh vpnclient.sh",)
    shutdown: Tuple[str, ...] = ("killall openvpn",)
    validate: Tuple[str, ...] = ("pidof openvpn",)
    custom_needed: bool = True

    @classmethod
    def generate_config(cls, node: CoreNode, filename: str) -> str:
        """
        Return the client.conf and vpnclient.sh file contents to
        """
        cfg = "#!/bin/sh\n"
        cfg += "# custom VPN Client configuration for service (security.py)\n"
        fname = f"{constants.CORE_DATA_DIR}/examples/services/sampleVPNClient"
        try:
            with open(fname, "r") as f:
                cfg += f.read()
        except IOError:
            logging.exception(
                "error opening VPN client configuration template (%s)", fname
            )
        return cfg


class VPNServer(CoreService):
    name: str = "VPNServer"
    group: str = "Security"
    configs: Tuple[str, ...] = ("vpnserver.sh",)
    startup: Tuple[str, ...] = ("sh vpnserver.sh",)
    shutdown: Tuple[str, ...] = ("killall openvpn",)
    validate: Tuple[str, ...] = ("pidof openvpn",)
    custom_needed: bool = True

    @classmethod
    def generate_config(cls, node: CoreNode, filename: str) -> str:
        """
        Return the sample server.conf and vpnserver.sh file contents to
        GUI for user customization.
        """
        cfg = "#!/bin/sh\n"
        cfg += "# custom VPN Server Configuration for service (security.py)\n"
        fname = f"{constants.CORE_DATA_DIR}/examples/services/sampleVPNServer"
        try:
            with open(fname, "r") as f:
                cfg += f.read()
        except IOError:
            logging.exception(
                "Error opening VPN server configuration template (%s)", fname
            )
        return cfg


class IPsec(CoreService):
    name: str = "IPsec"
    group: str = "Security"
    configs: Tuple[str, ...] = ("ipsec.sh",)
    startup: Tuple[str, ...] = ("sh ipsec.sh",)
    shutdown: Tuple[str, ...] = ("killall racoon",)
    custom_needed: bool = True

    @classmethod
    def generate_config(cls, node: CoreNode, filename: str) -> str:
        """
        Return the ipsec.conf and racoon.conf file contents to
        GUI for user customization.
        """
        cfg = "#!/bin/sh\n"
        cfg += "# set up static tunnel mode security assocation for service "
        cfg += "(security.py)\n"
        fname = f"{constants.CORE_DATA_DIR}/examples/services/sampleIPsec"
        try:
            with open(fname, "r") as f:
                cfg += f.read()
        except IOError:
            logging.exception("Error opening IPsec configuration template (%s)", fname)
        return cfg


class Firewall(CoreService):
    name: str = "Firewall"
    group: str = "Security"
    configs: Tuple[str, ...] = ("firewall.sh",)
    startup: Tuple[str, ...] = ("sh firewall.sh",)
    custom_needed: bool = True

    @classmethod
    def generate_config(cls, node: CoreNode, filename: str) -> str:
        """
        Return the firewall rule examples to GUI for user customization.
        """
        cfg = "#!/bin/sh\n"
        cfg += "# custom node firewall rules for service (security.py)\n"
        fname = f"{constants.CORE_DATA_DIR}/examples/services/sampleFirewall"
        try:
            with open(fname, "r") as f:
                cfg += f.read()
        except IOError:
            logging.exception(
                "Error opening Firewall configuration template (%s)", fname
            )
        return cfg


class Nat(CoreService):
    """
    IPv4 source NAT service.
    """

    name: str = "NAT"
    group: str = "Security"
    executables: Tuple[str, ...] = ("iptables",)
    configs: Tuple[str, ...] = ("nat.sh",)
    startup: Tuple[str, ...] = ("sh nat.sh",)
    custom_needed: bool = False

    @classmethod
    def generate_iface_nat_rule(cls, iface: CoreInterface, prefix: str = "") -> str:
        """
        Generate a NAT line for one interface.
        """
        cfg = prefix + "iptables -t nat -A POSTROUTING -o "
        cfg += iface.name + " -j MASQUERADE\n"
        cfg += prefix + "iptables -A FORWARD -i " + iface.name
        cfg += " -m state --state RELATED,ESTABLISHED -j ACCEPT\n"
        cfg += prefix + "iptables -A FORWARD -i "
        cfg += iface.name + " -j DROP\n"
        return cfg

    @classmethod
    def generate_config(cls, node: CoreNode, filename: str) -> str:
        """
        NAT out the first interface
        """
        cfg = "#!/bin/sh\n"
        cfg += "# generated by security.py\n"
        cfg += "# NAT out the first interface by default\n"
        have_nat = False
        for iface in node.get_ifaces(control=False):
            if have_nat:
                cfg += cls.generate_iface_nat_rule(iface, prefix="#")
            else:
                have_nat = True
                cfg += "# NAT out the " + iface.name + " interface\n"
                cfg += cls.generate_iface_nat_rule(iface)
                cfg += "\n"
        return cfg
