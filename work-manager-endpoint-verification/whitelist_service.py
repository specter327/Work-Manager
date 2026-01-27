from firebase_client import whitelist_ref


def add_device(device_id: str, enabled: bool = True):
    ref = whitelist_ref().child(device_id)
    ref.set({
        "enabled": enabled
    })


def remove_device(device_id: str):
    ref = whitelist_ref().child(device_id)
    ref.delete()


def get_device(device_id: str):
    ref = whitelist_ref().child(device_id)
    return ref.get()


def list_devices():
    ref = whitelist_ref()
    data = ref.get()
    return data if isinstance(data, dict) else {}
