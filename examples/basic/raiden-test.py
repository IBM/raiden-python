from raiden_python import raiden
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-b', '--baud',
                    required=False,
                    type=int,
                    default=115200, 
                    dest="baud",
                    metavar="<baud>",
                    help="Serial port baudrate")
parser.add_argument('-c', '--count',
                    required=False,
                    type=int,
                    default=5, 
                    dest="count",
                    metavar="<glitches>",
                    help="Number of glitches")
parser.add_argument('-d', '--delay',
                    required=False,
                    type=float,
                    default=0.0, 
                    dest="delay",
                    metavar="<delay>",
                    help="Delay in seconds (or ticks) from trigger")
parser.add_argument('-g', '--gap',
                    required=False,
                    type=float,
                    default=0.0, 
                    dest="gap",
                    metavar="<gap>",
                    help="Gap in seconds (or ticks) between glitches")
parser.add_argument('-m', '--mhz',
                    required=False,
                    type=int,
                    default=100, 
                    dest="mhz",
                    metavar="<mhz>",
                    help="Speed in MHz of FPGA clock")
parser.add_argument('-p', '--port',
                    required=False,
                    type=str,
                    default=100, 
                    dest="port",
                    metavar="<port>",
                    help="Serial port")
parser.add_argument('-r', '--repeat',
                    required=False,
                    type=int,
                    default=0, 
                    dest="repeat",
                    metavar="<repeat>",
                    help="Number of times to repeat glitch cycle (0 == no limit)")
parser.add_argument('-t', '--ticks',
                    required=False,
                    action= 'store_true',
                    default= False,
                    dest="ticks",
                    help="Specifiy timings in TICKS instead of SECONDS")
parser.add_argument('-v', '--vstart',
                    required=False,
                    type=int,
                    default=1, 
                    dest="vstart",
                    metavar="<vstart>",
                    help="output Voltage held LOW (0) or HIGH (1) until trigger")
parser.add_argument('-w', '--width',
                    required=False,
                    type=float,
                    default=0.0, 
                    dest="width",
                    metavar="<width>",
                    help="Width in seconds (or ticks) of glitch")

args = parser.parse_args()
print(args)

try:
    raiden = raiden.Raiden(mhz= args.mhz, serial_dev= args.port, baud= args.baud, ticks= args.ticks)
    raiden.reset_fpga()
    raiden.set_param(param="CMD_GLITCH_DELAY", seconds= args.delay)
    raiden.set_param(param="CMD_GLITCH_WIDTH", seconds= args.width)
    raiden.set_param(param="CMD_GLITCH_GAP", seconds= args.gap)
    raiden.set_param(param="CMD_GLITCH_COUNT", value= args.count)
    raiden.set_param(param="CMD_VSTART", value= args.vstart)
    raiden.set_param(param="CMD_GLITCH_MAX", value= args.repeat)
    raiden.arm(1)
    print("Raiden armed - CTL-C to quit...")		
    while True:		
        pass		
except KeyboardInterrupt:		 
    print("Killing raiden...")
    raiden.arm(0)
    raiden.reset_fpga()

