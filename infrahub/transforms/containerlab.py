from typing import TYPE_CHECKING

from ruamel.yaml import YAML, CommentedMap, CommentedSeq
from ruamel.yaml.compat import StringIO
from infrahub_sdk.transforms import InfrahubTransform

if TYPE_CHECKING:
    from .protocols import (
        NetworkDevice,
        NetworkInterface,
    )

CLAB_KIND_DATA = {"nokia_srlinux": {"kind": "nokia_srlinux", "type": "ixrd2"}}
CLAB_BASE_DATA = {
    "name": "demo",
    "topology": {
        "kinds": {
            "nokia_srlinux": {"image": "ghcr.io/nokia/srlinux"},
            "linux": {"image": "ghcr.io/hellt/network-multitool"},
        },
        "nodes": {},
        "links": [],
    },
}


class TransformContainerlabTopology(InfrahubTransform):
    query = "GetNetworkDevices"
    processed_endpoints: list[str] = []

    async def transform(self, data):
        await self.fetch()

        devices: list[NetworkDevice] = self.nodes  # type: ignore

        yaml = YAML()
        yaml.indent(mapping=2, sequence=4, offset=2)

        nodes = CommentedMap()
        links: list[dict[str, CommentedSeq]] = []

        for device in devices:
            # Add the device to the nodes map with description as a comment
            nodes.insert(
                0,
                device.name.value,
                CommentedMap(CLAB_KIND_DATA.get(device.platform.value)),
                comment=device.description.value,
            )
            await self.get_endpoints(links, device)

        clab_topology = CommentedMap(CLAB_BASE_DATA)
        clab_topology["topology"]["nodes"] = nodes
        clab_topology["topology"]["links"] = links
        clab_topology.yaml_set_start_comment(
            "yaml-language-server: $schema=https://github.com/srl-labs/containerlab/blob/main/schemas/clab.schema.json"
        )

        stream = StringIO()
        yaml.dump(clab_topology, stream)
        return stream.getvalue()

    async def fetch(self):
        batch = await self.client.create_batch()
        for device in self.nodes:
            batch.add(task=device.interfaces.fetch)

        # Asynchronous List Comprehensions
        [_ async for _ in batch.execute()]

    @classmethod
    async def get_endpoints(
        cls, endpoints: list[dict[str, CommentedSeq]], device: "NetworkDevice"
    ) -> None:
        # await device.interfaces.fetch()
        for peer in device.interfaces.peers:
            interface: NetworkInterface = peer.peer  # type: ignore

            if not interface.remote_interface.id:
                continue
            endpoint_1 = f"{device.name.value}:{interface.name.value}"

            if endpoint_1 in cls.processed_endpoints:
                continue

            # await interface.remote_interface.fetch()
            remote_interface: NetworkInterface = interface.remote_interface.peer  # type: ignore
            # await remote_interface.device.fetch()
            remote_device: NetworkDevice = remote_interface.device.peer  # type: ignore
            endpoint_2 = f"{remote_device.name.value}:{remote_interface.name.value}"

            interfaces = CommentedSeq()
            interfaces.append(endpoint_1)
            if interface.ip_address.id:
                interfaces.yaml_add_eol_comment(interface.ip_address.display_label, 0)

            interfaces.append(endpoint_2)
            if remote_interface.ip_address.id:
                interfaces.yaml_add_eol_comment(
                    remote_interface.ip_address.display_label, 1
                )

            cls.processed_endpoints.extend([endpoint_1, endpoint_2])

            endpoints.append({"endpoints": interfaces})
        return
