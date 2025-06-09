import os
from infrahub_sdk import InfrahubClientSync

_qk_creategroup = """
  mutation CreateGroup {
    CoreStandardGroupUpsert (data: {name: {value: "CiscoSwitche"}}) {
      ok
      object {
        hfid
      }
    }
  }
"""


def main():
    """Use this Main Function correctly."""
    # Needs environment variable `INFRAHUB_API_TOKEN`
    client = InfrahubClientSync(address=os.getenv("INFRAHUB_API_URL"))

    # Create Group
    result = client.execute_graphql(_qk_creategroup)
    print(result)


if __name__ == "__main__":
    main()
