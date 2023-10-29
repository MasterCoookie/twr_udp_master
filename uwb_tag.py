from uwb_device import UWBDevice

class UWBTag(UWBDevice):
    def __init__(self, ip, device_port, uwb_address, available_devices):
        super().__init__(ip, device_port, uwb_address)
        self.available_devices = available_devices

