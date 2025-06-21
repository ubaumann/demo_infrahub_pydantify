from typing import TYPE_CHECKING

from infrahub_sdk.transforms import InfrahubTransform

from custom_helper import main

if TYPE_CHECKING:
    from .protocols import (
        NetworkDevice,
        NetworkInterface,
    )


class TransformSRLNetconf(InfrahubTransform):
    query = "GetInterfacefromDevice"

    async def transform(self, data):
        return main()
