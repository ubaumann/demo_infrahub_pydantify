from typing import TYPE_CHECKING

import pydantic_srlinux.models.interfaces as srl_if

if TYPE_CHECKING:
    from ipaddress import IPv4Interface
    from custom_helper.protocols import NetworkDevice, NetworkInterface


def routed_subinterface_payload(ip: "IPv4Interface") -> "srl_if.SubinterfaceListEntry":
    return srl_if.SubinterfaceListEntry(
        index=0,
        ipv4=srl_if.Ipv4Container(address=[srl_if.AddressListEntry(ip_prefix=str(ip))]),
    )


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
