from typing import Annotated, Any, Optional

import base64
import zlib
import logging
from collections import defaultdict

import httpx
from infrahub_sdk.transforms import InfrahubTransform
from pydantic import BaseModel, AliasPath, Field, BeforeValidator
from jinja2 import Template


# Remove the 2 digits at the end of the device name to get the role
DeviceRole = Annotated[str, BeforeValidator(lambda x: x[:-2])]

log = logging.getLogger("infrahub.tasks")


class Neighbor(BaseModel):
    device_name: str = Field(
        validation_alias=AliasPath("device", "node", "name", "value")
    )
    interface_name: str = Field(None, validation_alias=AliasPath("name", "value"))


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
    id: str = Field(validation_alias=AliasPath("node", "id"))
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


def _kroki_get_url(base_url: str, diagram: str):
    encoded_diagram = base64.urlsafe_b64encode(zlib.compress(diagram.encode(), 9))
    return f"{base_url}{encoded_diagram.decode()}"


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
{% for role, devices in groups.items() %}
subgraph cluster_{{ role }} {
{%    for device in devices %}
 "{{ device.name }}"
{%-   endfor %}
}
{%- endfor %}

{% for endpoint1, endpoint2 in links %}
 "{{ endpoint1[0] }}" -- "{{ endpoint2[0] }}"{# [label="{{ endpoint1[1] }}|{{ endpoint2[1] }}"] #}
{%- endfor %}
}
"""

    async def transform(self, data):
        m = Topology.model_validate(data)

        links = []
        groups = defaultdict(list)

        for device in m.devices:
            for interface in device.interfaces:
                if interface.neighbor:
                    endpoints = [
                        (device.name, interface.name),
                        (
                            interface.neighbor.device_name,
                            interface.neighbor.interface_name,
                        ),
                    ]
                    endpoints.sort()
                    if endpoints not in links:
                        links.append(endpoints)
            groups[device.role].append(device)

        graphiz = Template(self.graphiz_template).render(
            groups=groups,
            links=links,
        )
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://kroki.io/graphviz/svg/", data=graphiz
                )
                response.raise_for_status()

        except httpx.HTTPError as exc:
            raise Exception(f"Failed to generate SVG: {exc}") from exc
        return response.text


class TransformTopologySVGD2(InfrahubTransform):
    query = "GetNetworkDevices"
    d2_template = """
vars: {
  d2-config: {
    layout-engine: elk # dagre
  }
}
direction: left

classes: {
  router_green: {
    shape: image
    icon: https://svg.infrastructureascode.ch/square/green/sq_router2_green.svg
  }
  router_red: {
    shape: image
    icon: https://svg.infrastructureascode.ch/square/red/sq_router2_red.svg
  }
  switch_green: {
    shape: image
    icon: https://svg.infrastructureascode.ch/square/green/sq_switch_green.svg
  }
  switch_red: {
    shape: image
    icon: https://svg.infrastructureascode.ch/square/red/sq_switch_red.svg
  }
  link: {
    style.animated: true
  }
}

title: |md
  # Network Topology using D2
  This diagram is generated using [D2](https://d2lang.com/).
| {near: top-center}

{% for role, devices in groups.items() %}
{%    for device in devices %}
{# Would be nicer to use computed attribute or do it in the Python code #}
{% if device.role in ["leaf", "spine"] %}
{% set class_type = "switch" %}
{% else %}
{% set class_type = "router" %}
{% endif %}
{% set colour = "green" if device.status == "active" else "red" %}
{{ device.role }}.{{ device.name }}: {{ device.name }} {
  class: {{ class_type }}_{{ colour }}
  link: http://10.8.34.1:8000/objects/NetworkDevice/{{ device.id}}
  tooltip: Interfaces:\\n{% for interface in device.interfaces | sort(attribute="name") %}{{ interface.name }}\\t{{ interface.description }}\\t{{ interface.mode }}\\n{% endfor %}
}
{%-   endfor %}
{%- endfor %}

{% for endpoint1, endpoint2 in links %}
 {{ endpoint1[0][:-2] }}.{{ endpoint1[0] }} -- {{ endpoint2[0][:-2] }}.{{ endpoint2[0] }} {
  class: link
  source-arrowhead.label: {{ endpoint1[1] }}
  target-arrowhead.label: {{ endpoint2[1] }}
}
{%- endfor %}
"""

    async def transform(self, data):
        m = Topology.model_validate(data)

        links = []
        groups = defaultdict(list)

        for device in m.devices:
            for interface in device.interfaces:
                if interface.neighbor:
                    endpoints = [
                        (device.name, interface.name.split("-")[1]),  # Todo
                        (
                            interface.neighbor.device_name,
                            interface.neighbor.interface_name.split("-")[1],  # Todo
                        ),
                    ]
                    endpoints.sort()
                    if endpoints not in links:
                        links.append(endpoints)
            groups[device.role].append(device)

        d2 = Template(self.d2_template).render(
            groups=groups,
            links=links,
        )
        log.warning(_kroki_get_url("https://kroki.io/d2/svg/", d2))
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post("https://kroki.io/d2/svg/", data=d2)
                response.raise_for_status()

        except httpx.HTTPError as exc:
            raise Exception(f"Failed to generate SVG: {exc}") from exc
        return response.text
