from typing import Annotated, Optional

from infrahub_sdk.transforms import InfrahubTransform
from pydantic import BaseModel, AliasPath, Field, BeforeValidator


# Remove the 2 digits at the end of the device name to get the role
DeviceRole = Annotated[str, BeforeValidator(lambda x: x[:-2])]


class Interface(BaseModel):
    name: str = Field(validation_alias=AliasPath("node", "name", "value"))
    description: Optional[str] = Field(
        None, validation_alias=AliasPath("node", "description", "value")
    )
    mode: str = Field(validation_alias=AliasPath("node", "mode", "value"))


class Device(BaseModel):
    name: str = Field(validation_alias=AliasPath("node", "name", "value"))
    description: Optional[str] = Field(
        None, validation_alias=AliasPath("node", "description", "value")
    )
    status: str = Field(validation_alias=AliasPath("node", "status", "value"))
    interfaces: list[Interface] = Field(
        validation_alias=AliasPath("node", "interfaces", "edges")
    )
    # Better to add it to the schema; works only because of the used naming convention
    role: DeviceRole = Field(
        validation_alias=AliasPath("node", "name", "value"),
    )


class Topology(BaseModel):
    devices: list[Device] = Field(validation_alias=AliasPath("NetworkDevice", "edges"))


class TransformTopologyMarkdown(InfrahubTransform):
    query = "GetNetworkDevices"

    async def transform(self, data):
        m = Topology.model_validate(data)

        markdown = "\n".join(
            [
                f"""# {x.name}
- Role: {x.role}
- Description: {x.description or "N/A"}
- Status: {x.status}

## Interfaces
{chr(10).join([f"- {i.name} ({i.mode}) - {i.description or 'N/A'}" for i in x.interfaces])}
"""
                for x in m.devices
            ]
        )
        return markdown
