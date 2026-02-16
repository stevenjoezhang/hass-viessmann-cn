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

    except AuthError as e:
        print(f"Authentication failed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
