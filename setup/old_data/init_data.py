import os
from infrahub_sdk import InfrahubClientSync, exceptions
import time as time


_qk_create_devices = [
    """
mutation MyMutation1 {
  NetworkDeviceUpsert(
    data: {name: {value: "sa1-infra-automation.network.garden"}, status: {value: "active"}, description: {value: "My awesome switch"}, platform: {value: "iosxe"}, user: {value: "ins"}, port: {value: 830}, password: {value: "ins@lab"}}
  ) {
    ok
  }
}""",
    """
mutation MyMutation2 {
  NetworkDeviceUpsert(
    data: {name: {value: "sa2-infra-automation.network.garden"}, status: {value: "active"}, description: {value: "My awesome switch"}, platform: {value: "iosxe"}, user: {value: "ins"}, port: {value: 830}, password: {value: "ins@lab"}}
  ) {
    ok
  }
}
""",
]


_qk_createinterface = """
mutation MyMutation {
  NetworkInterfaceUpsert(data: {
    name: {value: "%s"}, 
    mode: {value: "none"},
    status: {value: "up"},
    device: {hfid: "%s"}
  }
  ){
    ok
  }
}
 
"""

_qk_updategroup = """
  mutation UpdateGroupMembers {
    CoreStandardGroupUpdate(data: {
      hfid: "CiscoSwitche",
      members: [
        {id: "%s"},
        {id: "%s"},
      ]
    }
    ){
      ok
    }
  }
"""


def createinterface(device, intfname):
    """Use this Function to create Interfaces."""
    client = InfrahubClientSync(address=os.getenv("INFRAHUB_API_URL"))

    res = client.execute_graphql(_qk_createinterface % (str(intfname), device))
    time.sleep(0.5)
    return res


def main():
    """Use this Main Function correctly."""
    # Needs environment variable `INFRAHUB_API_TOKEN`
    client = InfrahubClientSync(address=os.getenv("INFRAHUB_API_URL"))

    # Create Devices
    for device_mutation in _qk_create_devices:
        result = client.execute_graphql(device_mutation)
        print(result)

    # Put Device in Groups
    deviceid1 = client.get(
        kind="NetworkDevice", name__value="sa1-infra-automation.network.garden"
    ).id
    deviceid2 = client.get(
        kind="NetworkDevice", name__value="sa2-infra-automation.network.garden"
    ).id
    result = client.execute_graphql(_qk_updategroup % (deviceid1, deviceid2))
    print(result)

    for device in [
        "sa1-infra-automation.network.garden",
        "sa2-infra-automation.network.garden",
    ]:
        for i in (1, 2):
            try:
                result = createinterface(device, "FortyGigabitEthernet1/1/" + str(i))
                print(result)
            except exceptions.GraphQLError:
                print(f"FortyGigabitEthernet1/1/{str(i)} is Wrong")
                continue
        for i in range(1, 25):
            try:
                result = createinterface(device, "GigabitEthernet1/0/" + str(i))
                print(result)
            except exceptions.GraphQLError:
                print(f"GigabitEthernet1/0/{str(i)} is Wrong")
                continue
        for i in range(1, 5):
            try:
                result = createinterface(device, "GigabitEthernet1/1/" + str(i))
                print(result)
            except exceptions.GraphQLError:
                print(f"GigabitEthernet1/1/{str(i)} is Wrong")
                continue
        for i in range(0, 1):
            try:
                result = createinterface(device, "GigabitEthernet0/" + str(i))
                print(result)
            except exceptions.GraphQLError as e:
                print(f"GigabitEthernet0/{str(i)} is Wrong" + str(e))
                continue
        for i in range(1, 9):
            try:
                result = createinterface(device, "TenGigabitEthernet1/1/" + str(i))
                print(result)
            except exceptions.GraphQLError:
                print(f"TenGigabitEthernet1/1/{str(i)} is Wrong")
                continue
        for i in range(1, 3):
            try:
                result = createinterface(device, "TwentyFiveGigE1/1/" + str(i))
                print(result)
            except exceptions.GraphQLError:
                print(f"TwentyFiveGigE1/1/{str(i)} is Wrong")
                continue


if __name__ == "__main__":
    main()
