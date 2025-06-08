from __future__ import annotations
from typing import List, Union
from pydantic import BaseModel, ConfigDict, Field, RootModel
from typing_extensions import Annotated
from enum import Enum


class AccessLeaf(BaseModel):
    """
    Set Mode Access
    """

    model_config = ConfigDict(
        populate_by_name=True,
    )


class NameLeaf(RootModel[str]):
    model_config = ConfigDict(
        populate_by_name=True,
        regex_engine="python-re",
    )
    root: Annotated[
        str,
        Field(
            pattern="^(?=^(0|[1-9][0-9]*)(/(0|[1-9][0-9]*))*(\\.[0-9]*)?$).*$",
            title="NameLeaf",
        ),
    ]


class TrunkLeaf(BaseModel):
    """
    Set Mode Trunk
    """

    model_config = ConfigDict(
        populate_by_name=True,
    )


class VlanLeaf(RootModel[int]):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    root: Annotated[int, Field(ge=1, le=4094, title="VlanLeaf")]
    """
    Set VLAN when interface is in access mode
    """


class VlanLeaf2(RootModel[int]):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    root: Annotated[int, Field(ge=1, le=4094, title="VlanLeaf2")]
    """
    Set VLAN when interface is in access mode
    """


class VlansLeaf1(RootModel[int]):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    root: Annotated[int, Field(ge=1, le=4094, title="VlansLeaf")]
    """
    Allow a single VLAN id (allowed value range 1-4094)
    or Comma-separated VLAN id range.
    e.g. 99 or 1-30 or  1-20,30,40-50
    """


class VlansLeaf(RootModel[Union[VlansLeaf1, str]]):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    root: Annotated[Union[VlansLeaf1, str], Field(title="VlansLeaf")]
    """
    Allow a single VLAN id (allowed value range 1-4094)
    or Comma-separated VLAN id range.
    e.g. 99 or 1-30 or  1-20,30,40-50
    """


class ModeContainer(BaseModel):
    """
    Set trunking mode of the interface
    """

    model_config = ConfigDict(
        populate_by_name=True,
    )
    access: Annotated[AccessLeaf, Field(None, alias="Cisco-IOS-XE-switch:access")]
    trunk: Annotated[TrunkLeaf, Field(None, alias="Cisco-IOS-XE-switch:trunk")]


class NativeContainer(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    vlan: Annotated[VlanLeaf2, Field(None, alias="Cisco-IOS-XE-switch:vlan")]


class VlanContainer(BaseModel):
    """
    Set access vlan of the interface
    """

    model_config = ConfigDict(
        populate_by_name=True,
    )
    vlan: Annotated[VlanLeaf, Field(None, alias="Cisco-IOS-XE-switch:vlan")]


class VlanContainer2(BaseModel):
    """
    Set allowed VLANs when interface is in trunking mode
    """

    model_config = ConfigDict(
        populate_by_name=True,
    )
    vlans: Annotated[VlansLeaf, Field(None, alias="Cisco-IOS-XE-switch:vlans")]
    """
    Allow a single VLAN id (allowed value range 1-4094)
     or Comma-separated VLAN id range.
     e.g. 99 or 1-30 or  1-20,30,40-50
    """


class AccessContainer(BaseModel):
    """
    Set access mode characteristics of the interface
    """

    model_config = ConfigDict(
        populate_by_name=True,
    )
    vlan: Annotated[VlanContainer, Field(None, alias="Cisco-IOS-XE-switch:vlan")]


class AllowedContainer(BaseModel):
    """
    Set allowed VLAN characteristics when interface is in trunking mode
    """

    model_config = ConfigDict(
        populate_by_name=True,
    )
    vlan: Annotated[VlanContainer2, Field(None, alias="Cisco-IOS-XE-switch:vlan")]


class TrunkContainer(BaseModel):
    """
    Set trunking characteristics of the interface
    """

    model_config = ConfigDict(
        populate_by_name=True,
    )
    allowed: Annotated[
        AllowedContainer, Field(None, alias="Cisco-IOS-XE-switch:allowed")
    ]


class SwitchportContainer(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    mode: Annotated[ModeContainer, Field(None, alias="Cisco-IOS-XE-switch:mode")]
    access: Annotated[AccessContainer, Field(None, alias="Cisco-IOS-XE-switch:access")]
    trunk: Annotated[TrunkContainer, Field(None, alias="Cisco-IOS-XE-switch:trunk")]
    native: Annotated[NativeContainer, Field(None, alias="Cisco-IOS-XE-switch:native")]


class SwitchportConfigContainer(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    switchport: Annotated[
        SwitchportContainer, Field(None, alias="Cisco-IOS-XE-native:switchport")
    ]


class InterfaceListEntry(BaseModel):
    """
    GigabitEthernet IEEE 802.3z
    """

    model_config = ConfigDict(
        populate_by_name=True,
    )
    name: Annotated[NameLeaf, Field(None, alias="Cisco-IOS-XE-native:name")]
    switchport_config: Annotated[
        SwitchportConfigContainer,
        Field(None, alias="Cisco-IOS-XE-native:switchport-config"),
    ]


class InterfaceContainer(BaseModel):
    """
    Configure Interfaces
    """

    model_config = ConfigDict(
        populate_by_name=True,
    )
    gigabit_ethernet: Annotated[
        List[InterfaceListEntry],
        Field(alias="Cisco-IOS-XE-native:GigabitEthernet"),
    ]
    ten_gigabit_ethernet: Annotated[
        List[InterfaceListEntry],
        Field(alias="Cisco-IOS-XE-native:TenGigabitEthernet"),
    ]
    twenty_five_gig_e: Annotated[
        List[InterfaceListEntry], Field(alias="Cisco-IOS-XE-native:TwentyFiveGigE")
    ]
    forty_gigabit_ethernet: Annotated[
        List[InterfaceListEntry],
        Field(alias="Cisco-IOS-XE-native:FortyGigabitEthernet"),
    ]


class NameLeaf(RootModel[str]):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    root: Annotated[str, Field(title="NameLeaf")]
    """
    Interface VLAN name.
    """


class NameLeaf2(RootModel[str]):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    root: Annotated[str, Field(title="NameLeaf2")]
    """
    Interface VLAN name.
    """


class NameLeaf4(RootModel[str]):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    root: str
    """
    The name of the interface.

    A device MAY restrict the allowed values for this leaf,
    possibly depending on the type of the interface.
    For system-controlled interfaces, this leaf is the
    device-specific name of the interface.  The 'config false'
    list interfaces/interface[name]/state contains the currently
    existing interfaces on the device.

    If a client tries to create configuration for a
    system-controlled interface that is not present in the
    corresponding state list, the server MAY reject
    the request if the implementation does not support
    pre-provisioning of interfaces or if the name refers to
    an interface that can never exist in the system.  A
    NETCONF server MUST reply with an rpc-error with the
    error-tag 'invalid-value' in this case.

    The IETF model in RFC 7223 provides YANG features for the
    following (i.e., pre-provisioning and arbitrary-names),
    however they are omitted here:

     If the device supports pre-provisioning of interface
     configuration, the 'pre-provisioning' feature is
     advertised.

     If the device allows arbitrarily named user-controlled
     interfaces, the 'arbitrary-names' feature is advertised.

    When a configured user-controlled interface is created by
    the system, it is instantiated with the same name in the
    /interfaces/interface[name]/state list.
    """


class VlanIdType(RootModel[int]):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    root: Annotated[int, Field(ge=1, le=4094)]
    """
    Type definition representing a single-tagged VLAN
    """


class EnumerationEnum(Enum):
    integer_0 = 0
    integer_1 = 1


class EnumerationEnum2(Enum):
    integer_0 = 0
    integer_1 = 1


class NameLeaf3(RootModel[NameLeaf4]):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    root: NameLeaf4
    """
    References the configured name of the interface
    """


class StatusLeaf(RootModel[EnumerationEnum]):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    root: Annotated[EnumerationEnum, Field(title="StatusLeaf")]
    """
    Admin state of the VLAN
    """


class StatusLeaf2(RootModel[EnumerationEnum2]):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    root: Annotated[EnumerationEnum2, Field(title="StatusLeaf2")]
    """
    Admin state of the VLAN
    """


class VlanIdLeaf2(RootModel[VlanIdType]):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    root: VlanIdType
    """
    Interface VLAN id.
    """


class VlanIdLeaf3(RootModel[VlanIdType]):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    root: Annotated[VlanIdType, Field(title="Vlan-idLeaf3")]
    """
    Interface VLAN id.
    """


class BaseInterfaceRefType(RootModel[NameLeaf3]):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    root: NameLeaf3
    """
    Reusable type for by-name reference to a base interface.
    This type may be used in cases where ability to reference
    a subinterface is not required.
    """


class ConfigContainer(BaseModel):
    """
    Configuration parameters for VLANs
    """

    model_config = ConfigDict(
        populate_by_name=True,
    )
    vlan_id: Annotated[VlanIdLeaf2, Field(None, alias="openconfig-vlan:vlan-id")]
    name: Annotated[NameLeaf, Field(None, alias="openconfig-vlan:name")]
    status: Annotated[StatusLeaf, Field("ACTIVE", alias="openconfig-vlan:status")]


class InterfaceLeaf(RootModel[BaseInterfaceRefType]):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    root: Annotated[BaseInterfaceRefType, Field(title="InterfaceLeaf")]
    """
    Reference to a base interface.
    """


class StateContainer(BaseModel):
    """
    State variables for VLANs
    """

    model_config = ConfigDict(
        populate_by_name=True,
    )
    vlan_id: Annotated[VlanIdLeaf3, Field(None, alias="openconfig-vlan:vlan-id")]
    name: Annotated[NameLeaf2, Field(None, alias="openconfig-vlan:name")]
    status: Annotated[StatusLeaf2, Field("ACTIVE", alias="openconfig-vlan:status")]


class StateContainer2(BaseModel):
    """
    Operational state for base interface reference
    """

    model_config = ConfigDict(
        populate_by_name=True,
    )
    interface: Annotated[InterfaceLeaf, Field(None, alias="openconfig-vlan:interface")]


class VlanIdLeaf(RootModel[VlanIdLeaf2]):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    root: Annotated[VlanIdLeaf2, Field(title="Vlan-idLeaf")]
    """
    references the configured vlan-id
    """


class MemberListEntry(BaseModel):
    """
    List of references to interfaces / subinterfaces
    associated with the VLAN.
    """

    model_config = ConfigDict(
        populate_by_name=True,
    )
    state: Annotated[StateContainer2, Field(None, alias="openconfig-vlan:state")]


class MembersContainer(BaseModel):
    """
    Enclosing container for list of member interfaces
    """

    model_config = ConfigDict(
        populate_by_name=True,
    )
    member: Annotated[List[MemberListEntry], Field(alias="openconfig-vlan:member")]


class VlanListEntry2(BaseModel):
    """
    Configured VLANs keyed by id
    """

    model_config = ConfigDict(
        populate_by_name=True,
    )
    vlan_id: Annotated[VlanIdLeaf, Field(None, alias="openconfig-vlan:vlan-id")]
    config: Annotated[ConfigContainer, Field(None, alias="openconfig-vlan:config")]
    state: Annotated[StateContainer, Field(None, alias="openconfig-vlan:state")]
    members: Annotated[MembersContainer, Field(None, alias="openconfig-vlan:members")]


class VlansContainer(BaseModel):
    """
    Container for VLAN configuration and state
    variables
    """

    model_config = ConfigDict(
        populate_by_name=True,
    )
    vlan: Annotated[List[VlanListEntry2], Field(alias="openconfig-vlan:vlan")]


class NativeContainer(BaseModel):
    """
    Container for VLAN configuration and state
    variables
    """

    model_config = ConfigDict(
        populate_by_name=True,
    )
    interface: Annotated[
        InterfaceContainer, Field(None, alias="Cisco-IOS-XE-native:interface")
    ]


class Model(BaseModel):
    """
    Initialize an instance of this class and serialize it to JSON; this results in a RESTCONF payload.

    ## Tips
    Initialization:
    - all values have to be set via keyword arguments
    - if a class contains only a `root` field, it can be initialized as follows:
        - `member=MyNode(root=<value>)`
        - `member=<value>`

    Serialziation:
    - `exclude_defaults=True` omits fields set to their default value (recommended)
    - `by_alias=True` ensures qualified names are used (necessary)
    """

    model_config = ConfigDict(
        populate_by_name=True,
    )
    native: Annotated[NativeContainer, Field(None, alias="Cisco-IOS-XE-native:native")]
    vlans: Annotated[VlansContainer, Field(None, alias="openconfig-vlan:vlans")]


if __name__ == "__main__":
    model = Model(
        # <Initialize model here>
    )

    restconf_payload = model.model_dump_json(
        exclude_defaults=True, by_alias=True, indent=2
    )

    print(f"Generated output: {restconf_payload}")

    # Send config to network device:
    # from pydantify.utility import restconf_patch_request
    # restconf_patch_request(url='...', user_pw_auth=('usr', 'pw'), data=restconf_payload)
