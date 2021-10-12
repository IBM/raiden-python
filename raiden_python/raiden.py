import struct 
import serial
import os
import math
import time

class Raiden:
    """
    Raiden defines class fields and methods
    """
    def __init__(self, baud= 115200, mhz= 100, serial_dev="/dev/cu.usbserial-00004114B", ticks= False, debug=False):
        """
        Construct a new 'Raiden' object.

        :param mhz: FPGA used frequency
        :param baud: Baud rate for UART 
        :param serial_dev: UART serial port for FPGA
        :param ticks: if set to True, seconds param take clock ticks, if set to False take time in seconds
        """
        self._hz= float(mhz * 1000000)
        self.ticks= ticks
        self.debug = debug
        self._commands = {
            "CMD_RST_GLITCHER":65,
            "CMD_FORCE_GLITCH_OUT_STATE": 66,
            "CMD_FLAGS_STATUS":68,
            "CMD_GLITCH_DELAY":69,
            "CMD_GLITCH_WIDTH":70,
            "CMD_GLITCH_COUNT":71,
            "CMD_ARM":72,
            "CMD_GLITCH_GAP":73,
            "CMD_RST": 74,
            "CMD_VSTART":75,
            "CMD_GLITCH_MAX":76,
            "CMD_BUILDTIME":77,
            "CMD_INVERT_TRIGGER":78,
            "CMD_RESET_TARGET":79,
            "CMD_GPIO_OUT": 80,
            "CMD_EMMC_DATA": 81        
        }
        
        self.device = serial.Serial(serial_dev, baudrate= baud, timeout=2.5, writeTimeout=2.5)
        self.device.rtscts = False
        self.device.dsrdtr = False 
        print("Raiden started...")


    def __raiden_cmd(self, device, command, value=None):

        cmd = [k for k,v in self._commands.items() if v == command][0]
        byte_cmd = chr(command).encode("ASCII")

        if cmd == "CMD_BUILDTIME":
            self.device.write(chr(command).encode("ASCII"))
            raw = device.read(4)
            return raw

        if cmd == "CMD_FLAGS_STATUS":
             self.device.write(chr(command).encode("ASCII"))
             raw =  device.read(1)[0]
             return raw

        #  CMD assertion
        if self.debug:
            print("[+] CMD byte to send {0}, CMD: {1}".format(byte_cmd, cmd))
        self.device.write(chr(command).encode("ASCII"))
        raw =  device.read(1)
        if self.debug:
            print("[+] CMD byte recv {0}, CMD int recv: {1}".format(raw, raw[0]))
        assert (raw == byte_cmd), "send:{0} recv_raw:{1}".format(byte_cmd, raw)
        
        # Single Byte command handling
        if (ord(raw) == self._commands["CMD_VSTART"] or 
            ord(raw) == self._commands["CMD_ARM"] or 
            ord(raw) == self._commands["CMD_FORCE_GLITCH_OUT_STATE"] or 
            ord(raw) == self._commands["CMD_RST"] or
            ord(raw) == self._commands["CMD_INVERT_TRIGGER"] or
            ord(raw) == self._commands["CMD_GPIO_OUT"] or
            ord(raw) == self._commands["CMD_RST_GLITCHER"]):

            data = struct.pack(">B", value)
            if self.debug:
                print("[+] outgoing byte", data)
            self.device.write(data)
            raw = device.read(1)
            assert (raw == data), "send:{0} recv_raw:{1}".format(data, raw)
            if self.debug:
                print("[+] incoming byte", raw)
            return

        # 4 byte command handling
        if (ord(raw) == self._commands["CMD_GLITCH_DELAY"] or 
            ord(raw) == self._commands["CMD_GLITCH_WIDTH"] or 
            ord(raw) == self._commands["CMD_GLITCH_COUNT"] or
            ord(raw) == self._commands["CMD_GLITCH_GAP"] or
            ord(raw) == self._commands["CMD_GLITCH_MAX"] or
            ord(raw) == self._commands["CMD_EMMC_DATA"] or
            ord(raw) == self._commands["CMD_RESET_TARGET"]):

            data = struct.pack(">I", value)
            if self.debug:
                print("[+] outgoing bytes", data)
            self.device.write(data)
            raw = device.read(4)[::-1]
            assert (raw == data), "send:{0} recv_raw:{1}".format(data, raw)
            if self.debug:
                print("[+] incoming bytes", raw)
            return
        return

    def set_param(self, param="CMD_GLITCH_DELAY", value=1):
        """
        Set glitching params before arming Raiden.

        :param param: Raiden command
        :param seconds: FPGA ticks or seconds
        :param value: value for CMD_GLITCH_COUNT, CMD_VSTART, CMD_GLITCH_MAX
        """
        if(param == "CMD_GLITCH_COUNT" or param == "CMD_VSTART" or param == "CMD_GLITCH_MAX" or param == "CMD_INVERT_TRIGGER" or param == "CMD_GPIO_OUT"):
            self.__raiden_cmd(self.device, self._commands[param], int(value))
            return
        if(self.ticks):
            fpga_ticks= int(value)
        else:
            fpga_ticks= math.ceil(self._hz * value)
        self.__raiden_cmd(self.device, self._commands[param], fpga_ticks)
    
    def arm(self, value=1):
        """
        Arm Raiden for pulse generation.

        :param value: True/False 0/1, where True arm Raiden and False disarm
        """
        if(value == 0 or value == 1):
             self.__raiden_cmd(self.device, self._commands["CMD_ARM"], value)
             return
        else:
            print("Supported values arm values 1 or 0")
            return

    def set_target_power(self, power="auto"):
        """
        Target reset control.

        :param power: "on" set voltage line HIGH, "off set voltage line LOW
        """
        if power.lower() == "auto":
            self.__raiden_cmd(self.device, self._commands["CMD_FORCE_GLITCH_OUT_STATE"], 2)
        if power.lower() == "on":
            self.__raiden_cmd(self.device, self._commands["CMD_FORCE_GLITCH_OUT_STATE"], 1)
        if power.lower() == "off":
            self.__raiden_cmd(self.device, self._commands["CMD_FORCE_GLITCH_OUT_STATE"], 0)

    def flag_status(self):
        """
        Return status of internal flags

        :return bitfield:
          flags[0] armed       - API armed
          flags[1] glitched    - glitching has started
          flags[2] finished    - glitching has completed
          flags[3] glitch_out  - current state of glitch out
          flags[4] trigger_in  - current state of trigger in
          flags[5] gpio_in - current GPIO_IN status
          flags[6] gpio1_out - current GPIO1_OUT status
          flags[7] gpio2_out - current GPIO2_OUT status
        """
        return self.__raiden_cmd(self.device, self._commands["CMD_FLAGS_STATUS"])

    def is_armed(self):
        """
        Checks status of armed flag

        :return 0 if not armed, 1 if armed
        """
        return ((self.flag_status()) & 0x01)
    
    def is_glitched(self):
        """
        Checks status of glitched flag

        :return 0 if glitching has not started, 1 if started
        """
        return ((self.flag_status() >> 1) & 0x01)
    
    def is_finished(self):
        """
        Checks status of finished flag

        :return 0 if glitching has not finished, 1 if finished
        """
        return ((self.flag_status() >> 2) & 0x01)
    
    def glitch_out(self):
        """
        Checks status of glitch_out

        :return 0 if glitch_out is LOW and 1 if HIGH
        """
        return ((self.flag_status() >> 3) & 0x01)
    
    def is_triggered(self):
        """
        Checks status of trigger

        :return 0 if external trigger is LOW and 1 if HIGH
        """
        return ((self.flag_status() >> 4) & 0x01)
   
    def is_gpio1_in_high(self):
        """
        :return 0 if GPIO is not HIGH, else return 1
        """
        return ((self.flag_status()>>5) & 0x01)

    def is_gpio2_in_high(self):
        """
        :return 0 if GPIO is not HIGH, else return 1
        """
        return ((self.flag_status()>>7) & 0x01)

    def gpio_out_status(self):
        """
        return 0 if GPIO LOW or 1 if GPIO HIGH
        """
        return ((self.flag_status()>>6) &0x01)

    def reset_glitcher(self):
        """
        Reset Raiden modules to default values
        """
        self.__raiden_cmd(self.device, self._commands["CMD_RST_GLITCHER"], 1)
    
    
    def disc(self):
        """
        Reset Raiden modules to default values
        """
        self.__raiden_cmd(self.device, self._commands["CMD_RST"], 1)
        self.device.close()
    
    def available_commands(self):
        """
        Available commands for Raiden

        :return available Raiden commands as a list
        """
        return [x for x in self._commands]

    def get_buildtime(self):
        raw = self.__raiden_cmd(self.device, self._commands["CMD_BUILDTIME"])
        day = raw[3] >> 3
        month = ((raw[3] & 0x7) << 1) + (raw[2] >> 7)
        year = ((raw[2] >> 1) & 0x3f) + 2000
        hour = ((raw[2] & 0x1) << 4) + (raw[1] >> 4)
        minute = ((raw[1] & 0xf) << 2) + (raw[0] >> 6)
        return "Raiden build time: {}/{}/{}, {}:{}".format(day, month, year, hour, minute)

