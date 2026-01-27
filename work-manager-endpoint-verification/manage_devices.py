import argparse
import json
from whitelist_service import (
    add_device,
    remove_device,
    get_device,
    list_devices
)


def main():
    parser = argparse.ArgumentParser(
        description="Work Manager – Device Whitelist Manager"
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # add
    add = sub.add_parser("add", help="Add device")
    add.add_argument("device_id")
    add.add_argument("--disabled", action="store_true")

    # remove
    remove = sub.add_parser("remove", help="Remove device")
    remove.add_argument("device_id")

    # get
    get = sub.add_parser("get", help="Get device info")
    get.add_argument("device_id")

    # list
    sub.add_parser("list", help="List all devices")

    args = parser.parse_args()

    if args.command == "add":
        add_device(args.device_id, enabled=not args.disabled)
        print(f"[OK] Device {args.device_id} added")

    elif args.command == "remove":
        remove_device(args.device_id)
        print(f"[OK] Device {args.device_id} removed")

    elif args.command == "get":
        device = get_device(args.device_id)
        print(json.dumps(device, indent=2))

    elif args.command == "list":
        devices = list_devices()
        print(json.dumps(devices, indent=2))


if __name__ == "__main__":
    main()
