from collections import namedtuple
from tqdm import tnrange
import sys

from raiden_gen import raiden

delay = 0
Range = namedtuple('Range', ['min', 'max', 'step'])
width_range = Range(17, 18, 1)
width = width_range.min
max_delay = 150
#150
rest = 0
try:
    raiden = raiden.Raiden(mhz="100", serial_dev="/dev/cu.usbserial-00004114B", ticks=True)
    while(True):
        status = raiden.is_triggered()
        if(status):
            width = width_range.min
            while width < width_range.max:
                print("Current width: {0}".format(width))
                for delay in range(delay, max_delay, 10):
                    for glitch in range(1, 3, 1):
                        raiden.arm(0)
                        raiden.set_param(param="CMD_GLITCH_DELAY", seconds=delay)
                        raiden.set_param(param="CMD_GLITCH_WIDTH", seconds=width)
                        raiden.set_param(param="CMD_GLITCH_COUNT", value=glitch)
                        raiden.arm(1)
                    # print("Current delay: {0}".format(delay))
                width += width_range.step
                delay = 0
        else:
            raiden.arm(0)
except KeyboardInterrupt:
    print("Raiden is going to stop...")
    raiden.arm(0)
finally:
     raiden.arm(0)
     raiden.target_reset(seconds=1000000)
