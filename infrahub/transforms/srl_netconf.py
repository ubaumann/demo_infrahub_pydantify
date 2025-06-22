from typing import TYPE_CHECKING

from infrahub_sdk.transforms import InfrahubTransform
from custom_helper.srl_netconf import main

if TYPE_CHECKING:
    from custom_helper.protocols import (
        NetworkDevice,
    )


class TransformSRLNetconf(InfrahubTransform):
    query = "GetInterfacefromDevice"

    async def transform(self, data):
        device: NetworkDevice = self.nodes[0]
        return await main(device)
