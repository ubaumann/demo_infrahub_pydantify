from typing import TYPE_CHECKING
from collections import defaultdict

from pydantic import RootModel
import pydantic_srlinux.models.interfaces as srl_if
import pydantic_srlinux.models.network_instance as srl_ni

if TYPE_CHECKING:
    from ipaddress import IPv4Interface
    from custom_helper.protocols import NetworkDevice, NetworkInterface, NetworkVlan


class SRLYangPayloadHelper:
    def __init__(self) -> None:
        self.mac_vrfs: dict[int, list[str]] = defaultdict(list)

    @staticmethod
    def routed_subinterface_payload(
        ip: "IPv4Interface",
    ) -> "srl_if.SubinterfaceListEntry":
        return srl_if.SubinterfaceListEntry(
            index=0,
            # admin_state=srl_if.EnumerationEnum.enable,
            ipv4=srl_if.Ipv4Container(
                address=[srl_if.AddressListEntry(ip_prefix=str(ip))]
            ),
        )

    @staticmethod
    def fabric_subinterface_payload() -> "srl_if.SubinterfaceListEntry":
        return srl_if.SubinterfaceListEntry(
            index=0,
            # admin_state=srl_if.EnumerationEnum.enable,
            ipv6=srl_if.Ipv6Container(admin_state=srl_if.EnumerationEnum.enable),
        )

    def access_subinterface_payload(
        self, vlan: "NetworkVlan", interface_name: str
    ) -> "srl_if.SubinterfaceListEntry":
        # Add interface to the mac_vrf to be able to create the network-instance later
        self.mac_vrfs[vlan.peer.vlan_id.value].append(f"{interface_name}.0")

        return srl_if.SubinterfaceListEntry(
            index=0,
            # admin_state=srl_if.EnumerationEnum.enable,
            vlan=srl_if.VlanContainer(
                encap=srl_if.EncapContainer(untagged=srl_if.UntaggedContainer())
            ),
        )

    def trunk_subinterface_payload(
        self,
        vlans: list["NetworkVlan"],
        interface_name: str,
    ) -> list["srl_if.SubinterfaceListEntry"]:
        subinterfaces: list["srl_if.SubinterfaceListEntry"] = []
        for peer in vlans:
            vlan: NetworkVlan = peer.peer  # type: ignore
            vlan_number = vlan.vlan_id.value

            # Add interface to the mac_vrf to be able to create the network-instance later
            self.mac_vrfs[vlan_number].append(f"{interface_name}.{vlan_number}")

            subinterfaces.append(
                srl_if.SubinterfaceListEntry(
                    index=vlan_number,
                    # admin_state=srl_if.EnumerationEnum.enable,
                    vlan=srl_if.VlanContainer(
                        encap=srl_if.EncapContainer(
                            single_tagged=srl_if.SingleTaggedContainer(
                                vlan_id=srl_if.VlanIdType(vlan_number)
                            )
                        )
                    ),
                )
            )
        return subinterfaces

    def interface_payload(
        self, interface: "NetworkInterface"
    ) -> "srl_if.InterfaceListEntry":
        admin_state = (
            srl_if.EnumerationEnum.enable
            if interface.status.value == "up"
            else srl_if.EnumerationEnum.enable
        )
        subinterfaces: list[srl_if.SubinterfaceListEntry] | None = None
        match interface.mode.value:
            case "routed":
                subinterfaces = [
                    self.routed_subinterface_payload(interface.ip_address.peer)
                ]
            case "fabric":
                subinterfaces = [self.fabric_subinterface_payload()]
            case "access":
                subinterfaces = [
                    self.access_subinterface_payload(
                        interface.vlan.peers[0], interface_name=interface.name.value
                    )
                ]
            case "trunk":
                subinterfaces = self.trunk_subinterface_payload(
                    interface.vlan.peers, interface_name=interface.name.value
                )
            case _:
                ...  # ToDo

        return srl_if.InterfaceListEntry(
            name=interface.name.value,
            admin_state=admin_state,
            description=interface.description.value,
            subinterface=subinterfaces,
        )

    def mac_vrf_payload(self) -> list["srl_ni.NetworkInstanceListEntry"]:
        network_instances: list[srl_ni.NetworkInstanceListEntry] = []
        for vlan, interfaces in self.mac_vrfs.items():
            network_instances.append(
                srl_ni.NetworkInstanceListEntry(
                    name=f"bridge-{vlan}",
                    type="mac-vrf",
                    interface=[
                        srl_ni.InterfaceListEntry(name=eth) for eth in interfaces
                    ],
                )
            )
        return network_instances


class PyloadData(RootModel):
    root: list[srl_if.Model | srl_ni.Model]


async def main(device: "NetworkDevice") -> str:
    helper = SRLYangPayloadHelper()

    # Interfaces
    interface_models: list[srl_if.InterfaceListEntry] = []
    for interface in device.interfaces.peers:
        interface_models.append(helper.interface_payload(interface.peer))
    interface_model = srl_if.Model(interface=interface_models)

    # Mac-Vrf
    network_instance_model = srl_ni.Model(network_instance=helper.mac_vrf_payload())

    # return interface_model.model_dump_json(
    #     exclude_defaults=True, by_alias=True, indent=2
    # )
    # return network_instance_model.model_dump_json(
    #     exclude_defaults=True, by_alias=True, indent=2
    # )
    return PyloadData(root=[interface_model, network_instance_model]).model_dump_json(
        exclude_defaults=True, by_alias=True, indent=2
    )
