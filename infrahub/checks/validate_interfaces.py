from infrahub_sdk.checks import InfrahubCheck
from typing import Any


class AccessModeCheck(InfrahubCheck):
    """Checks if an interface in 'access' mode has only one VLAN."""

    query = "GetInterfaceDetails"

    def validate(self, data: dict[str, Any]) -> None:
        """Validate the data returned by the query."""
        for edge in data["NetworkInterface"]["edges"]:
            interface = edge["node"]
            if interface["mode"]["value"] == "access":
                vlan_count = len(interface["vlan"]["edges"])
                if vlan_count != 1:
                    self.log_error(
                        message=f"Interface '{interface['name']['value']}' is in 'access' mode but has {vlan_count}(s)",
                    )
