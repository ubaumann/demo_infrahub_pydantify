from typing import TYPE_CHECKING

import pydantic_srlinux.models.interfaces as srl_if

if TYPE_CHECKING:
    from custom_helper.protocols import NetworkDevice, NetworkInterface


def get_interface_payload(interface: "NetworkInterface") -> "srl_if.InterfaceListEntry":
    return srl_if.InterfaceListEntry(name=interface.name.value)


async def main(device: "NetworkDevice") -> str:
    interface_models: list[srl_if.InterfaceListEntry] = []
    for interface in device.interfaces.peers:
        interface_models.append(get_interface_payload(interface.peer))
    model = srl_if.Model(interface=interface_models)
    return model.model_dump_json(exclude_defaults=True, by_alias=True, indent=2)
