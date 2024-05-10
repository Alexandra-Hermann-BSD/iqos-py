""" iQOS USB reader """

import usb

# try to find the device
device = usb.core.find(idVendor=0x2759, idProduct=0x0003)
if device is None:
    raise ValueError('iqos device not found!')

# if interface is claimed, try to detach it
if device.is_kernel_driver_active(0):
    print("Detaching kernel driver 0")
    device.detach_kernel_driver(0)
if device.is_kernel_driver_active(1):
    print("Detaching kernel driver 1")
    device.detach_kernel_driver(1)

# set default configuration and get the interface
device.set_configuration()
cfg = device.get_active_configuration()
interface_number = cfg[(0, 0)].bInterfaceNumber
alternate_setting = usb.control.get_interface(device, interface_number)
usb_interface = usb.util.find_descriptor(cfg, bInterfaceNumber=interface_number, bAlternateSetting=alternate_setting)

# get the two endpoints
endpoint_out = usb.util.find_descriptor(usb_interface, custom_match=lambda e: usb.util.endpoint_direction(
    e.bEndpointAddress) == usb.util.ENDPOINT_OUT)
endpoint_in = usb.util.find_descriptor(usb_interface, custom_match=lambda e: usb.util.endpoint_direction(
    e.bEndpointAddress) == usb.util.ENDPOINT_IN)

# try reading, 10 attempts max
ATTEMPTS = 10
DATA = None
while DATA is None and ATTEMPTS > 0:
    try:
        DATA = device.read(endpoint_in.bEndpointAddress, endpoint_in.wMaxPacketSize)
    except usb.core.USBError as e:
        DATA = None
        if e.args == ('Operation timed out',):
            print('I used to read, then I took a timeout to the knee...')
            ATTEMPTS -= 1
            continue

print('Raw data:\n')
print(DATA)
print('\nASCII data: \n')
RX_DATA = ''.join([chr(x) for x in DATA])
print(RX_DATA)
