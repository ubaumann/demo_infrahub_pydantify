import logging

from infrahub_sdk import InfrahubClient


# ---------------------------------------------------------------
# Use the `infrahubctl run` command line to execute this script
#
#   infrahubctl run infrahub/bootstrap/create_topology.py
#
# ---------------------------------------------------------------
async def run(
    client: InfrahubClient, log: logging.Logger, branch: str, **kwargs
) -> None:
    log.info("creating Infrahub objects")
    