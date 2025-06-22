from typing import TYPE_CHECKING

import pydantic_srlinux.models.interfaces as srl_if

if TYPE_CHECKING:
    from ipaddress import IPv4Interface
    from custom_helper.protocols import NetworkDevice, NetworkInterface, NetworkVlan


def routed_subinterface_payload(ip: "IPv4Interface") -> "srl_if.SubinterfaceListEntry":
    return srl_if.SubinterfaceListEntry(
        index=0,
        # admin_state=srl_if.EnumerationEnum.enable,
        ipv4=srl_if.Ipv4Container(address=[srl_if.AddressListEntry(ip_prefix=str(ip))]),
    )


def fabric_subinterface_payload() -> "srl_if.SubinterfaceListEntry":
    return srl_if.SubinterfaceListEntry(
        index=0,
        # admin_state=srl_if.EnumerationEnum.enable,
        ipv6=srl_if.Ipv6Container(admin_state=srl_if.EnumerationEnum.enable),
    )


def access_subinterface_payload() -> "srl_if.SubinterfaceListEntry":
    return srl_if.SubinterfaceListEntry(
        index=0,
        # admin_state=srl_if.EnumerationEnum.enable,
        vlan=srl_if.VlanContainer(
            encap=srl_if.EncapContainer(untagged=srl_if.UntaggedContainer())
        ),
    )


def trunk_subinterface_payload(
    vlans: list["NetworkVlan"],
) -> list["srl_if.SubinterfaceListEntry"]:
    subinterfaces: list["srl_if.SubinterfaceListEntry"] = []
    for peer in vlans:
        vlan: NetworkVlan = peer.peer
        subinterfaces.append(
            srl_if.SubinterfaceListEntry(
                index=vlan.vlan_id.value,
                # admin_state=srl_if.EnumerationEnum.enable,
                vlan=srl_if.VlanContainer(
                    encap=srl_if.EncapContainer(
                        single_tagged=srl_if.SingleTaggedContainer(
                            vlan_id=srl_if.VlanIdType(vlan.vlan_id.value)
                        )
                    )
                ),
            )
        )
    return subinterfaces


def interface_payload(interface: "NetworkInterface") -> "srl_if.InterfaceListEntry":
    admin_state = (
        srl_if.EnumerationEnum.enable
        if interface.status.value == "up"
        else srl_if.EnumerationEnum.enable
    )
    subinterfaces: list[srl_if.SubinterfaceListEntry] | None = None
    match interface.mode.value:
        case "routed":
            subinterfaces = [routed_subinterface_payload(interface.ip_address.peer)]
        case "fabric":
            subinterfaces = [fabric_subinterface_payload()]
        case "access":
            subinterfaces = [access_subinterface_payload()]
        case "trunk":
            subinterfaces = trunk_subinterface_payload(interface.vlan.peers)
        case _:
            ...  # ToDo

    return srl_if.InterfaceListEntry(
        name=interface.name.value,
        admin_state=admin_state,
        description=interface.description.value,
        subinterface=subinterfaces,
    )


async def main(device: "NetworkDevice") -> str:
    interface_models: list[srl_if.InterfaceListEntry] = []
    for interface in device.interfaces.peers:
        interface_models.append(interface_payload(interface.peer))
    model = srl_if.Model(interface=interface_models)
    return model.model_dump_json(exclude_defaults=True, by_alias=True, indent=2)
