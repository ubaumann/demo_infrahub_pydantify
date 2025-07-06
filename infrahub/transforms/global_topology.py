from typing import Annotated, Any, Optional

import httpx
from infrahub_sdk.transforms import InfrahubTransform
from pydantic import BaseModel, AliasPath, Field, BeforeValidator
from jinja2 import Template



# Remove the 2 digits at the end of the device name to get the role
DeviceRole = Annotated[str, BeforeValidator(lambda x: x[:-2])]


class Neighbor(BaseModel):
    device_name: str = Field(validation_alias=AliasPath("device", "node", "name", "value"))
    interface_name: str = Field(
        None, validation_alias=AliasPath("name", "value")
    )

class Interface(BaseModel):
    name: str = Field(validation_alias=AliasPath("node", "name", "value"))
    description: Optional[str] = Field(
        None, validation_alias=AliasPath("node", "description", "value")
    )
    mode: str = Field(validation_alias=AliasPath("node", "mode", "value"))
    neighbor: Optional[Neighbor] = Field(
        None, validation_alias=AliasPath("node", "remote_interface", "node")
    )


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

    def model_post_init(self, context: Any) -> None:
        self.devices = sorted(self.devices, key=lambda x: x.name.lower())


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


class TransformTopologySVGGraphviz(InfrahubTransform):
    query = "GetNetworkDevices"
    graphiz_template = """
graph {
 node [shape=box, style="rounded,filled"]
{% for device in devices %}
 "{{ device.name }}"
{%- endfor %}
{% for endpoint1, endpoint2 in links %}
 "{{ endpoint1[0] }}" -- "{{ endpoint2[0] }}" [label="{{ endpoint1[1] }} - {{ endpoint2[1] }}"]
{%- endfor %}
}
"""

    async def transform(self, data):
        m = Topology.model_validate(data)

        links = []

        for device in m.devices:
            for interface in device.interfaces:
                if interface.neighbor:
                    endpoints = [(device.name, interface.name), (interface.neighbor.device_name,interface.neighbor.interface_name)]
                    endpoints.sort()
                    if endpoints not in links:
                        links.append(endpoints)

        graphiz = Template(self.graphiz_template).render(
            devices=m.devices,
            links=links,
        )
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post("https://kroki.io/graphviz/svg/", data=graphiz)
                response.raise_for_status()

        except httpx.HTTPError as exc:
            raise Exception(f"Failed to generate SVG: {exc}") from exc
        return response.text

