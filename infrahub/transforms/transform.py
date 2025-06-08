from __future__ import annotations
import xml.etree.ElementTree as ETree  # nosec B405
import re
from .Modules.xmlexporter import XMLModelConverter
from infrahub_sdk.transforms import InfrahubTransform
from xml.dom.minidom import parseString  # nosec B408
from .PydanticStructure.out import (
    InterfaceContainer,
    NativeContainer,
    VlansContainer,
    Model,
    SwitchportConfigContainer,
    InterfaceListEntry,
    VlanContainer,
    AccessContainer,
    AccessLeaf,
    ModeContainer,
    SwitchportContainer,
    VlanContainer2,
    AllowedContainer,
    TrunkContainer,
    TrunkLeaf,
    ConfigContainer,
    VlanListEntry2,
)
from typing import Any, Dict

""" This Public Module provides:
- Get Information from the GraphQL
- Load Data into Pydantic the Pydantic Model, generated from the openconfig Yang Files
- Generate an Netconf Conform XML with the XMLExporter class.
"""


class TransformIntoNetconf(InfrahubTransform):
    """Public Class which inherits from InfrahubTransform."""

    query = "GetInterfacefromDevice"

    async def transform(self, data: Dict[str, Any]) -> str:
        """Public Method for a PythonTransformer to load data into an Netconf XML."""
        vlanlist = []
        gigabit_ethernet_interfacelist = []
        ten_gigabit_ethernet_interfacelist = []
        twenty_five_gigabit_ethernet_interfacelist = []
        forty_gigabit_ethernet_interfacelist = []
        pattern = r"(.*?)([0-9](?:/[0-9](?:/[0-9]([0-9])?)?)?)$"
        ETree.register_namespace("nc", "urn:ietf:params:xml:ns:netconf:base:1.0")

        # VLAN Model
        for vlan in data["NetworkVlan"]["edges"]:
            vlanname = vlan["node"]["name"]["value"]
            vlanid = vlan["node"]["vlan_id"]["value"]
            vlanentry = VlanListEntry2(
                vlan_id=vlanid, config=ConfigContainer(vlan_id=vlanid, name=vlanname)
            )
            vlanlist.append(vlanentry)

        # Interface Model
        for intf in data["NetworkDevice"]["edges"][0]["node"]["interfaces"]["edges"]:
            match = re.match(pattern, intf["node"]["name"]["value"])
            if not match:
                continue  # Skip this interface if the name doesn't match the pattern

            interfacespeed = match.group(1)
            interfacename = match.group(2)
            trunkvlanidlist = []

            match intf["node"]["mode"]["value"]:
                case "trunk":
                    for trunkvlan in intf["node"]["vlan"]["edges"]:
                        trunkvlanidlist.append(trunkvlan["node"]["vlan_id"]["value"])

                    interfacelistentrys = InterfaceListEntry(
                        name=interfacename,
                        switchport_config=SwitchportConfigContainer(
                            switchport=SwitchportContainer(
                                mode=ModeContainer(trunk=TrunkLeaf()),
                                trunk=TrunkContainer(
                                    allowed=AllowedContainer(
                                        vlan=VlanContainer2(
                                            vlans=",".join(map(str, trunkvlanidlist))
                                        )
                                    )
                                ),
                            )
                        ),
                    )

                case "access":
                    interfacelistentrys = InterfaceListEntry(
                        name=interfacename,
                        switchport_config=SwitchportConfigContainer(
                            switchport=SwitchportContainer(
                                mode=ModeContainer(access=AccessLeaf()),
                                access=AccessContainer(
                                    vlan=VlanContainer(
                                        vlan=intf["node"]["vlan"]["edges"][0]["node"][
                                            "vlan_id"
                                        ]["value"]
                                    )
                                ),
                            )
                        ),
                    )

                case _:
                    interfacelistentrys = InterfaceListEntry(
                        name=interfacename,
                        switchport_config=SwitchportConfigContainer(),
                    )

            match interfacespeed:
                case "GigabitEthernet":
                    gigabit_ethernet_interfacelist.append(interfacelistentrys)
                case "TenGigabitEthernet":
                    ten_gigabit_ethernet_interfacelist.append(interfacelistentrys)
                case "TwentyFiveGigE":
                    twenty_five_gigabit_ethernet_interfacelist.append(
                        interfacelistentrys
                    )
                case "FortyGigabitEthernet":
                    forty_gigabit_ethernet_interfacelist.append(interfacelistentrys)

        model = Model(
            vlans=VlansContainer(vlan=vlanlist),
            native=NativeContainer(
                interface=InterfaceContainer(
                    gigabit_ethernet=gigabit_ethernet_interfacelist,
                    ten_gigabit_ethernet=ten_gigabit_ethernet_interfacelist,
                    twenty_five_gig_e=twenty_five_gigabit_ethernet_interfacelist,
                    forty_gigabit_ethernet=forty_gigabit_ethernet_interfacelist,
                )
            ),
        )
        xmlcontent = XMLModelConverter.to_xml(model)
        xml_string = ETree.tostring(xmlcontent, encoding="unicode")
        return parseString(xml_string).toprettyxml()  # nosec B318
