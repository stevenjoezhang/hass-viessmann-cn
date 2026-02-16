import asyncio
import logging
import sys
from custom_components.viessmann_cn import ViessmannClient, AuthError

# Configure logging
logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)


async def main():
    if len(sys.argv) < 3:
        print("Usage: python3 test_api.py <username> <password>")
        return

    username = sys.argv[1]
    password = sys.argv[2]

    client = ViessmannClient(username, password)

    try:
        print("Logging in...")
        await client.login()
        print("Login successful!")

        print("Getting user info...")
        user_info = await client.get_user_info()
        print(f"User ID: {user_info.get('userId')}")

        print("Getting family list...")
        families = await client.get_family_list()
        print(f"Found {len(families)} families.")
        if families:
            print(f"Family ID: {families[0].get('familyId')}")

        print("Getting devices...")
        devices = await client.get_family_devices()
        print("Devices retrieved.")

        # Get detailed status
        print("Getting detailed status...")
        status = await client.update()
        print("Current Status:")
        print(status)

        print("Getting scan status...")
        scan_status = await client.get_scan_status()
        print("Scan Status:")
        print(scan_status)

        # Interactive control
        while True:
            print("Select an action:")
            print("1. Set Heating Temperature")
            print("2. Set DHW Temperature")
            print("3. Set Mode")
            print("4. Refresh Status")
            print("q. Quit")

            choice = input("Enter choice: ")

            if choice == "q":
                break

            try:
                if choice == "1":
                    temp = float(input("Enter heating temperature: "))
                    print(f"Setting heating temperature to {temp}...")
                    await client.set_heating_temp(temp)
                    print("Done.")
                elif choice == "2":
                    temp = float(input("Enter DHW temperature: "))
                    print(f"Setting DHW temperature to {temp}...")
                    await client.set_dhw_temp(temp)
                    print("Done.")
                elif choice == "3":
                    print(
                        "Common modes: 10 (Standby/Off), 15 (DHW only), 20 (Heating+DHW)"
                    )
                    mode = int(input("Enter mode: "))
                    print(f"Setting mode to {mode}...")
                    await client.set_mode(mode)
                    print("Done.")
                elif choice == "4":
                    print("Refreshing status...")
                    status = await client.update()
                    print("Current Status:")
                    print(status)
                else:
                    print("Invalid choice")
            except ValueError:
                print("Invalid input value")
            except Exception as e:
                print(f"Operation failed: {e}")

    except AuthError as e:
        print(f"Authentication failed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
