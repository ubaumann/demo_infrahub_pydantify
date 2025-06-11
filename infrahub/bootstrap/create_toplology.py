import logging

from infrahub_sdk import InfrahubClient


# ---------------------------------------------------------------
# Use the `infrahubctl run` command line to execute this script
#
#   infrahubctl run infrahub/bootstrap/create_topology.py leafs=3 spines=2
#   infrahubctl run infrahub/bootstrap/create_topology.py leafs=3 spines=2 borders=2 routers=3 edges=1
#
# ---------------------------------------------------------------
async def run(
    client: InfrahubClient, log: logging.Logger, branch: str, leafs: str = "3", spines: str = "2", borders: str = "0", routers: str = "0", edges: str = "0", 
) -> None:
    log.info("creating Infrahub objects")
    for i in range(int(leafs)):
        log.info(f"creating leaf {i + 1}")
    
    for i in range(int(spines)):
        log.info(f"creating spine {i + 1}")
    
    for i in range(int(borders)):
        log.info(f"creating border {i + 1}")
    
    for i in range(int(routers)):
        log.info(f"creating router {i + 1}")
    
    for i in range(int(edges)):
        log.info(f"creating edge {i + 1}")
