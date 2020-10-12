from raiden_gen import raiden
import argparse
import serial
import time

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--port',
                    required=True,
                    type=str,
                    default="/dev/cu.usbserial-00004014B", 
                    dest="port",
                    metavar="<port>",
                    help="Raiden serial port")

args = parser.parse_args()
print(args)


try:
    raiden = raiden.Raiden(mhz= 100, serial_dev= args.port, baud= 115200, ticks= True)
except:
    print("Can't open Raiden!")
    exit(True)

def showflags():
    stat= raiden.flag_status()
    print("Current flags: %d" % stat)
    print("  Armed: %d" % raiden.is_armed())
    print("  Trigger: %d" % raiden.is_triggered())
    print("  Glitched: %d" % raiden.is_glitched());
    print("  Finished: %d" % raiden.is_finished());
    print("  Power: %d" % raiden.glitch_out());

print(raiden.get_buildtime())
print(raiden.get_buildtime())

print("clearing flags")
print("")
raiden.reset_fpga()
raiden.arm(0)
raiden.set_target_power("off")
showflags()

print("")
print("arming...")
raiden.arm(1)
showflags()

print("")
print("power on...")
raiden.set_target_power("on")
showflags()

