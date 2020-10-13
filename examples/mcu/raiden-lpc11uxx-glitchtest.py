from raiden-python import raiden
import argparse
import time
import serial

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--port',
                    required=True,
                    type=str,
                    default="/dev/cu.usbserial-00004014B", 
                    dest="port",
                    metavar="<port>",
                    help="Raiden serial port")
parser.add_argument('-l', '--lpc',
                    required=True,
                    type=str,
                    default="/dev/cu.usbmodem14101", 
                    dest="lpc",
                    metavar="<lpc>",
                    help="LPC11Uxx UART/CDC serial port")
parser.add_argument('-d', '--debug',
                    required=False,
                    type=str,
                    default=False, 
                    dest="debug",
                    metavar="<debug>",
                    help="Raiden debug commands")

args = parser.parse_args()
print(args)


raiden = raiden.Raiden(mhz= 100, serial_dev= args.port, baud= 115200, ticks= True, debug=args.debug)
#except:
#    print("Can't open Raiden!")
#    exit(True)

raiden.reset_glitcher()
raiden.arm(0)

# reboot target
raiden.set_target_power("off")
time.sleep(1)
raiden.set_target_power("on")
time.sleep(1)
raiden.set_target_power("auto")

raiden.set_param(param="CMD_VSTART", value= 1)
raiden.set_param(param="CMD_GLITCH_COUNT", value= 1)
raiden.set_param(param="CMD_GLITCH_MAX", value= 1)

try:
    lpc = serial.Serial(args.lpc, baudrate= 115200, timeout= 0.1)
except:
    print("Can't open STM11Uxx!")
    exit(True)


# escape glitch mode in case we're re-starting
lpc.write(b' ')
lpc.write(b' ')
while(42):
    text= lpc.readline().decode("UTF-8")
    if text == "":
      break

# enter glitch test mode
lpc.write(b'g')
while(42):
    text= lpc.readline().decode("UTF-8").strip()
    if text == "*":
        break
    print(text)

# total test period is 2.04us so 2040 ns - one tick is 10 ns
for delay in range(205):
	# for width in range(9):
	for width in [8]:
            raiden.arm(0)
            raiden.reset_glitcher()
            raiden.set_param(param="CMD_VSTART", value= 1)
            raiden.set_param(param="CMD_GLITCH_COUNT", value= 1)
            raiden.set_param(param="CMD_GLITCH_MAX", value= 1)
            raiden.set_param(param="CMD_GLITCH_DELAY", seconds= delay)
            raiden.set_param(param="CMD_GLITCH_WIDTH", seconds= width)
            raiden.set_param(param="CMD_GLITCH_GAP", seconds= width)
            raiden.arm()
            lpc.write(b'g')
            while(not raiden.is_finished()):
                pass
            text= lpc.readline().decode("UTF-8").strip()
            if(text == '!'):
                print("")
                print('got it!')
                print('delay %d' % delay)
                print('width %d' % width)
                continue
            print('\rnope! delay %d\twidth %d' % (delay, width), end='')
            if(text != '.'):
                print("")
                print('something bad: %s' % text)
                exit(True)
print("")
