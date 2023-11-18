class UWBDevice:
    def __init__(self, ip, device_port, uwb_address, x_pos=None, y_pos=None, z_pos=None):
        self.ip = ip
        self.device_port = device_port
        self.uwb_address = uwb_address

        self.x_pos = x_pos
        self.y_pos = y_pos
        self.z_pos = z_pos

        self.distance = None
    
    @property
    def address(self):
        return (self.ip, self.device_port)