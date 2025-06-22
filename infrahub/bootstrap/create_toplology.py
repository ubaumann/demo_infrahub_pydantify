import logging

from typing import Optional, Literal
from dataclasses import dataclass

from infrahub_sdk import InfrahubClient
from infrahub_sdk.batch import InfrahubBatch
from custom_helper.protocols import (
    NetworkDevice,
    NetworkInterface,
    IpamIPPrefix,
    IpamIPAddress,
    CoreIPAddressPool,
    CoreIPPrefixPool,
)


@dataclass
class Prefixe:
    prefix: str
    member_type: str
    description: str
    is_pool: bool = False
    resource_pool_key: Optional[str] = None


PLATFORM = "nokia_srlinux"
PREFIXES = [
    Prefixe(
        prefix="10.0.0.0/8",
        member_type="prefix",
        description="underlay network",
    ),
    Prefixe(
        prefix="10.255.255.0/24",
        member_type="address",
        description="Loopback IP address pool",
        is_pool=True,
        resource_pool_key="loopback_network",
    ),
    Prefixe(
        prefix="10.255.252.0/23",
        member_type="prefix",
        description="p2p network",
        resource_pool_key="p2p_network",
    ),
]


async def create_device_and_add_to_batch(
    client: InfrahubClient,
    log: logging.Logger,
    branch: str,
    device_role: str,
    number: int,
    batch_devices: InfrahubBatch,
    batch_interfaces: InfrahubBatch,
    allow_upsert: Optional[bool] = True,
) -> NetworkDevice:
    """Creates a device and adds it to a batch for deferred saving."""
    device_name = f"{device_role}{number:02d}"
    log.info(f"Creating {device_role} {device_name} and adding to batch")
    device = await client.create(
        NetworkDevice,
        name=device_name,
        platform=PLATFORM,
        status="active",
        branch=branch,
    )
    batch_devices.add(task=device.save, allow_upsert=allow_upsert, node=device)

    client.store.set(key=device_name, node=device)

    # Create Loopback 0 interface for the device
    await create_loopback_interface(
        client,
        log,
        branch,
        device,
        batch_interfaces,
    )
    return device


async def create_interfaces_and_add_to_batch(
    client: InfrahubClient,
    log: logging.Logger,
    branch: str,
    device_name: str,
    neighbor_role: str,
    neighbor_number: int,
    batch: InfrahubBatch,
    allow_upsert: bool = True,
    offset: int = 0,
    port_mode: Literal["routed", "access", "fabric"] = "access",
) -> None:
    """Creates interfaces for a device and add them to a batch for deferred saving."""
    for i in range(1, neighbor_number + 1):
        interface_name = f"ethernet-1/{i + offset}"
        neighbor_name = f"{neighbor_role}{i:02d}"
        log.info(
            f"Creating interface {interface_name} {device_name} and adding to batch"
        )
        device = client.store.get(key=device_name)
        neighbor_interface = client.store.get(
            key=f"{neighbor_name}__{device_name}", raise_when_missing=False
        )
        if port_mode == "routed":
            # get the IP address for the interface
            ip_address = await get_interface_ip(
                client=client,
                log=log,
                branch=branch,
                prefix_identifier="_to_".join(sorted([device_name, neighbor_name])),
                ip_index=0 if device_name < neighbor_name else 1,
                allow_upsert=allow_upsert,
            )
        else:
            ip_address = None

        interface = await client.create(
            NetworkInterface,
            name=interface_name,
            status="up",
            device=device.hfid,
            mode=port_mode,
            description=f"{device_name} to {neighbor_name}",
            ip_address=ip_address,
            remote_interface=neighbor_interface,
            branch=branch,
        )
        client.store.set(key=f"{device_name}__{neighbor_name}", node=interface)
        batch.add(task=interface.save, allow_upsert=allow_upsert, node=interface)


async def create_loopback_interface(
    client: InfrahubClient,
    log: logging.Logger,
    branch: str,
    device: NetworkDevice,
    batch: InfrahubBatch,
    allow_upsert: Optional[bool] = True,
) -> None:
    log.info(f"Creating Loopback 0 for {device.name.value} and adding to batch")
    pool = client.store.get(key="loopback_network")
    ip_address = await client.allocate_next_ip_address(
        resource_pool=pool,
        identifier=f"{device.name.value}_loopback0",
        prefix_length=32,
    )

    interface = await client.create(
        NetworkInterface,
        name="Loopback0",
        status="up",
        device=device.hfid,
        mode="routed",
        ip_address=ip_address,
        branch=branch,
    )
    batch.add(task=interface.save, allow_upsert=allow_upsert, node=interface)


async def get_interface_ip(
    client: InfrahubClient,
    log: logging.Logger,
    branch: str,
    prefix_identifier: str,
    ip_index: int,
    allow_upsert: bool = True,
) -> IpamIPAddress:
    log.info(f"Get IP link {prefix_identifier}")
    pool = client.store.get(key="p2p_network")
    p2p_prefix = await client.allocate_next_ip_prefix(
        resource_pool=pool,
        identifier=f"{prefix_identifier}",
        prefix_length=31,
        prefix_type="IpamIPPrefix",
    )

    p2p_network = p2p_prefix.prefix.value
    ip_address = list(p2p_network.hosts())[ip_index]
    ip = await client.create(
        IpamIPAddress,
        branch=branch,
        address=f"{ip_address}/{p2p_network.prefixlen}",
        description=f"P2P link {prefix_identifier}",
    )
    await ip.save(allow_upsert=allow_upsert)
    return ip


async def init_ipam(
    client: InfrahubClient,
    log: logging.Logger,
    branch: str,
    allow_upsert: bool = True,
) -> None:
    log.info("Initializing IPAM with prefixes")
    batch = await client.create_batch()
    batch_pools = await client.create_batch()
    for prefix in PREFIXES:
        log.info(f"Creating prefix {prefix.prefix} and adding to batch")
        prefix_obj = await client.create(
            IpamIPPrefix,
            prefix=prefix.prefix,
            member_type=prefix.member_type,
            description=prefix.description,
            is_pool=prefix.is_pool,
            branch=branch,
        )
        batch.add(task=prefix_obj.save, allow_upsert=allow_upsert, node=prefix_obj)

        if prefix.resource_pool_key:
            log.info(
                f"Creating Resource Pool {prefix.resource_pool_key} with prefix {prefix.prefix}"
            )
            is_ip_pool = prefix.member_type == "address"
            pool = await client.create(
                CoreIPAddressPool if is_ip_pool else CoreIPPrefixPool,
                name=prefix.resource_pool_key,
                default_address_type="IpamIPAddress" if is_ip_pool else "IpamIPPrefix",
                default_prefix_size=32 if is_ip_pool else 31,
                resources=[prefix_obj],
                is_pool=True,
                ip_namespace={"id": "default"},
            )
            batch_pools.add(task=pool.save, allow_upsert=allow_upsert, node=pool)
            client.store.set(key=prefix.resource_pool_key, node=pool)

    async for node, _ in batch.execute():
        log.info(
            f"Created IP prefix {node.prefix.value} with member type {node.member_type.value}"
        )

    async for node, _ in batch_pools.execute():
        log.info(f"Created Resource Pool {node.name.value}")


# ---------------------------------------------------------------
# Use the `infrahubctl run` command line to execute this script
#
#   infrahubctl run infrahub/bootstrap/create_topology.py leafs=3 spines=2
#   infrahubctl run infrahub/bootstrap/create_topology.py leafs=3 spines=2 borders=2 routers=3 edges=1
#
# ---------------------------------------------------------------
async def run(
    client: InfrahubClient,
    log: logging.Logger,
    branch: str,
    leafs: str = "3",
    spines: str = "2",
    borders: str = "0",
    routers: str = "0",
    edges: str = "0",
) -> None:
    log.info("Creating Infrahub objects")
    await init_ipam(client, log, branch)

    batch_devices = await client.create_batch()
    batch_interfaces = await client.create_batch()

    for i in range(1, int(leafs) + 1):
        device = await create_device_and_add_to_batch(
            client, log, branch, "leaf", i, batch_devices, batch_interfaces
        )
        await create_interfaces_and_add_to_batch(
            client,
            log,
            branch,
            device.name.value,
            "spine",
            int(spines),
            batch_interfaces,
            port_mode="fabric",
        )
        # Create interfaces to borders if any
        if int(borders) > 0 and i <= 2:
            await create_interfaces_and_add_to_batch(
                client,
                log,
                branch,
                device.name.value,
                "border",
                int(borders),
                batch_interfaces,
                offset=2,  # Offset to avoid duplicate interface names
                port_mode="routed",
            )

    for i in range(1, int(spines) + 1):
        device = await create_device_and_add_to_batch(
            client, log, branch, "spine", i, batch_devices, batch_interfaces
        )
        await create_interfaces_and_add_to_batch(
            client,
            log,
            branch,
            device.name.value,
            "leaf",
            int(leafs),
            batch_interfaces,
            port_mode="fabric",
        )

    for i in range(1, int(borders) + 1):
        device = await create_device_and_add_to_batch(
            client, log, branch, "border", i, batch_devices, batch_interfaces
        )
        # Create interfaces to leafs
        await create_interfaces_and_add_to_batch(
            client,
            log,
            branch,
            device.name.value,
            "leaf",
            min(int(leafs), 2),
            batch_interfaces,
            port_mode="routed",
        )
        # Create interfaces to routers
        await create_interfaces_and_add_to_batch(
            client,
            log,
            branch,
            device.name.value,
            "router",
            int(routers),
            batch_interfaces,
            offset=min(int(leafs), 2),
            port_mode="routed",
        )

    for i in range(1, int(routers) + 1):
        device = await create_device_and_add_to_batch(
            client, log, branch, "router", i, batch_devices, batch_interfaces
        )
        # Create interfaces to borders
        await create_interfaces_and_add_to_batch(
            client,
            log,
            branch,
            device.name.value,
            "border",
            int(borders),
            batch_interfaces,
            port_mode="routed",
        )
        # Create interfaces to edges
        await create_interfaces_and_add_to_batch(
            client,
            log,
            branch,
            device.name.value,
            "edge",
            int(edges),
            batch_interfaces,
            offset=int(borders),
            port_mode="routed",
        )

    for i in range(1, int(edges) + 1):
        device = await create_device_and_add_to_batch(
            client, log, branch, "edge", i, batch_devices, batch_interfaces
        )
        # Create interfaces to routers
        await create_interfaces_and_add_to_batch(
            client,
            log,
            branch,
            device.name.value,
            "router",
            int(routers),
            batch_interfaces,
            port_mode="routed",
        )

    async for node, _ in batch_devices.execute():
        log.info(
            f"Created device {node.name.value} with platform {node.platform.value}"
        )

    async for node, _ in batch_interfaces.execute():
        log.info(f"Created interface {node.name.value} {node.device.hfid[0]}")
