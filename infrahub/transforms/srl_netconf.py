from typing import TYPE_CHECKING

from infrahub_sdk.transforms import InfrahubTransform
from custom_helper.srl_netconf import main

if TYPE_CHECKING:
    from custom_helper.protocols import (
        NetworkDevice,
        NetworkInterface,
    )


class TransformSRLNetconf(InfrahubTransform):
    query = "GetInterfacefromDevice"

    async def transform(self, data):
        device: NetworkDevice = self.nodes[0]

        # Fetch all needed relations
        await self.fetch(device)

        return await main(device)

    async def fetch(self, device: "NetworkDevice"):
        batch = await self.client.create_batch()
        for interface_relation in device.interfaces.peers:
            interface: "NetworkInterface" = interface_relation.peer
            if interface.ip_address.id:
                batch.add(task=interface.ip_address.fetch)

        # Asynchronous List Comprehensions
        [_ async for _ in batch.execute()]
