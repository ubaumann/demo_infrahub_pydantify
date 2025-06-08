from lxml import etree  # nosec B410
from pydantic import BaseModel, RootModel
from enum import Enum
from typing import Dict, Any

"""
Python Module to generate Netconf confirm XML Exporter.

- Takes a Pydantic Base Model as Input.
- Based on OpenConfig YAML Files.
"""


class XMLModelConverter:
    """Class XMLConverter."""

    @staticmethod
    def _formatmodelkeybyalias(modelkey: str) -> tuple[list[str], str]:
        modelkey_parts = modelkey.split(":", 2)
        if "Cisco-IOS-XE" in modelkey_parts[0]:
            namespacelist = ["http://cisco.com/ns/yang/", modelkey_parts[0]]
        else:
            namespacelist = modelkey_parts[0].split("-")
        return namespacelist, modelkey_parts[1]

    @staticmethod
    def _searchnamespace(namespace: str) -> str:
        match namespace:
            case "openconfig":
                return "http://openconfig.net/yang/"
            case "if":
                return "interfaces/"
            case _:
                return namespace

    @staticmethod
    def _getnamespace(namespacelist: list[str]) -> str:
        return "".join(
            XMLModelConverter._searchnamespace(entry) for entry in namespacelist
        )

    @staticmethod
    def _checkifnamespaceisintree(roottree: etree.Element, namespace: str) -> bool:
        if "xmlns" in roottree.attrib and roottree.attrib["xmlns"] == namespace:
            return True
        if roottree.getparent() is not None:
            return XMLModelConverter._checkifnamespaceisintree(
                roottree.getparent(), namespace
            )
        return False

    @staticmethod
    def _createsubelement(
        roottree: etree.Element, model: BaseModel, modelkey: str
    ) -> etree.Element:
        alias = model.model_fields[modelkey].alias
        if alias is None:
            raise ValueError(f"Alias for model key '{modelkey}' cannot be None.")
        namespacelist, keyvalue = XMLModelConverter._formatmodelkeybyalias(alias)
        namespace = XMLModelConverter._getnamespace(namespacelist)
        if not XMLModelConverter._checkifnamespaceisintree(roottree, namespace):
            return etree.SubElement(roottree, keyvalue, attrib={"xmlns": namespace})
        return etree.SubElement(roottree, keyvalue)

    @staticmethod
    def _renderrootmodels(model: BaseModel) -> str | int | None:
        if isinstance(model, RootModel):
            return XMLModelConverter._renderrootmodels(model.root)
        elif isinstance(model, bool):
            return str(model).lower()
        elif isinstance(model, (str, int)):
            return model
        elif isinstance(model, Enum):
            return model.value  # type: ignore[no-any-return]
        return None

    @staticmethod
    def _renderingmodel(model: BaseModel, roottree: etree.Element) -> etree.Element:
        if isinstance(model, BaseModel):
            for modelkey in model.model_fields:
                if isinstance(model, RootModel):
                    roottree.text = str(XMLModelConverter._renderrootmodels(model))
                    continue
                if isinstance(getattr(model, modelkey), list):
                    for modelentry in getattr(model, modelkey):
                        subroottree = XMLModelConverter._createsubelement(
                            roottree, model, modelkey
                        )
                        XMLModelConverter._renderingmodel(modelentry, subroottree)
                    continue
                if isinstance(getattr(model, modelkey), BaseModel):
                    subroottree = XMLModelConverter._createsubelement(
                        roottree, model, modelkey
                    )
                    XMLModelConverter._renderingmodel(
                        getattr(model, modelkey), subroottree
                    )
        return roottree

    @staticmethod
    def to_xml(model: BaseModel) -> etree.Element:
        """Public Method to convert Pydantic into Netconf XML."""
        root = etree.Element("{urn:ietf:params:xml:ns:netconf:base:1.0}config")
        return XMLModelConverter._renderingmodel(model, root)

    @staticmethod
    def _to_dict(tree: etree.Element) -> Dict[str, Any]:
        result: Dict[str, Any] = {}

        # Iteriere über alle direkten Kinder
        for child in tree:
            name = child.tag.split("}", 1)[-1]  # Entferne Namespace
            text = child.text.strip() if child.text else None

            match name:
                case "vlan-id":  # Optional: Namen anpassen
                    name = "vlan_id"
                case "GigabitEthernet":
                    name = "gigabit_ethernet"
                case "TenGigabitEthernet":
                    name = "ten_gigabit_ethernet"
                case "TwentyFiveGigE":
                    name = "twenty_five_gig_e"
                case "FortyGigabitEthernet":
                    name = "forty_gigabit_ethernet"
                case "switchport-config":
                    name = "switchport_config"

            # Wenn das Element Kinder hat, rufe _to_dict rekursiv auf
            if len(child):
                child_dict: Dict[str, Any] = XMLModelConverter._to_dict(child)

                # Falls der Tag mehrfach vorkommt, speichere ihn in einer Liste
                if name in result:
                    if not isinstance(result[name], list):
                        result[name] = [result[name]]
                    result[name].append(child_dict)
                else:
                    result[name] = child_dict
            else:
                # Kein Kind, speichere Textinhalt

                # Falls der Tag mehrfach vorkommt, speichere ihn in einer Liste
                if name in result:
                    if not isinstance(result[name], list):
                        result[name] = [result[name]]
                    result[name].append(text)
                else:
                    # Leeres Element: Speichere ein leeres Dictionary wenn kein Value
                    result[name] = text if text else {}

        return result

    @staticmethod
    def to_basemodel(tree: etree.Element, model: BaseModel) -> BaseModel:
        """Public Method to convert Neconf XML into Pydantic Model."""
        dict = XMLModelConverter._to_dict(tree.getroot())
        return model.model_validate(dict)
