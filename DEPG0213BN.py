from micropython import const
from time import sleep_ms
import framebuf

# Display resolution
EPD_WIDTH = const(128)
EPD_HEIGHT = const(250)

# Display commands
DRIVER_OUTPUT_CONTROL = b'\x01'
GATE_DRIVING_VOLTAGE_CONTROL = b'\x03'
SOURCE_DRIVING_VOLTAGE_CONTROL = b'\x04'
BOOSTER_SOFT_START_CONTROL = b'\x0C'
DEEP_SLEEP_MODE = b'\x10'
DATA_ENTRY_MODE_SETTING = b'\x11'
SW_RESET = b'\x12'
MASTER_ACTIVATION = b'\x20'
DISPLAY_UPDATE_CONTROL_1 = b'\x21'  # 0x0 normal (POR), 0x4 bypass content as 0, 0x8 invert content
DISPLAY_UPDATE_CONTROL_2 = b'\x22'
WRITE_RAM = b'\x24'
WRITE_VCOM_REGISTER = b'\x2C'
WRITE_LUT_REGISTER = b'\x32'
SET_GATE_TIME = b'\x3B'
BORDER_WAVEFORM_CONTROL = b'\x3C'
SET_RAM_X_ADDRESS_START_END_POSITION = b'\x44'
SET_RAM_Y_ADDRESS_START_END_POSITION = b'\x45'
SET_RAM_X_ADDRESS_COUNTER = b'\x4E'
SET_RAM_Y_ADDRESS_COUNTER = b'\x4F'
SET_ANALOG_BLOCK_CONTROL = b'\x74'
SET_DIGITAL_BLOCK_CONTROL = b'\x7E'
NOP_FRAME_TERMINATOR = b'\x7F'
TERMINATE_FRAME_READ_WRITE = b'\xFF'  # NOP, terminate frame

# Rotaion
ROTATION_0 = const(0)
ROTATION_90 = const(1)
ROTATION_180 = const(2)
ROTATION_270 = const(3)


LUT_SIZE_TTGO_DKE_PART = 153

PART_UPDATE_LUT_TTGO_DKE = bytearray([
    0x0, 0x40, 0x0, 0x0, 0x0,  0x0,  0x0,  0x0,  0x0,  0x0,  0x0, 0x0, 0x80, 0x80, 0x0, 0x0, 0x0, 0x0,  0x0, 0x0,
    0x0, 0x0,  0x0, 0x0, 0x40, 0x40, 0x0,  0x0,  0x0,  0x0,  0x0, 0x0, 0x0,  0x0,  0x0, 0x0, 0x0, 0x80, 0x0, 0x0,
    0x0, 0x0,  0x0, 0x0, 0x0,  0x0,  0x0,  0x0,  0x0,  0x0,  0x0, 0x0, 0x0,  0x0,  0x0, 0x0, 0x0, 0x0,  0x0, 0x0,
    0xF, 0x0,  0x0, 0x0, 0x0,  0x0,  0x0,  0x1,  0x0,  0x0,  0x0, 0x0, 0x0,  0x0,  0x0, 0x0, 0x0, 0x0,  0x0, 0x0,
    0x0, 0x0,  0x0, 0x0, 0x0,  0x0,  0x0,  0x0,  0x0,  0x0,  0x0, 0x0, 0x0,  0x0,  0x0, 0x0, 0x0, 0x0,  0x0, 0x0,
    0x0, 0x0,  0x0, 0x0, 0x0,  0x0,  0x0,  0x0,  0x0,  0x0,  0x0, 0x0, 0x0,  0x0,  0x0, 0x0, 0x0, 0x0,  0x0, 0x0,
    0x0, 0x0,  0x1, 0x0, 0x0,  0x0,  0x0,  0x0,  0x0,  0x1,  0x0, 0x0, 0x0,  0x0,  0x0, 0x0, 0x0, 0x0,  0x0, 0x0,
    0x0, 0x0,  0x0, 0x0, 0x22, 0x22, 0x22, 0x22, 0x22, 0x22, 0x0, 0x0, 0x0
    ])


class EPD(framebuf.FrameBuffer):
    def __init__(self, spi, cs, dc, rst, busy, rotation=ROTATION_0):
        self.init_spi(spi, cs, dc, rst, busy)
        self.init_buffer(rotation)

        self.hard_reset()
        self.soft_reset()

    def init_buffer(self, rotation):
        self._rotation = rotation
        size = EPD_WIDTH * EPD_HEIGHT // 8
        self.buffer = bytearray(size)

        if self._rotation == ROTATION_0 or self._rotation == ROTATION_180:
            self.width = EPD_WIDTH
            self.height = EPD_HEIGHT
        else:
            self.width = EPD_HEIGHT
            self.height = EPD_WIDTH

        print('width:{}, height:{}'.format(self.width, self.height))

        super().__init__(self.buffer,
                         self.width,
                         self.height,
                         framebuf.MONO_HLSB if self._rotation == ROTATION_0 or self._rotation == ROTATION_180
                         else framebuf.MONO_VLSB)

    def init_spi(self, spi, cs, dc, rst, busy):
        self.spi = spi
        self.spi.init(baudrate=4000_000)
        self.cs = cs
        self.dc = dc
        self.rst = rst
        self.busy = busy
        self.cs.init(self.cs.OUT, value=1)
        self.dc.init(self.dc.OUT, value=0)
        self.rst.init(self.rst.OUT, value=0)
        self.busy.init(self.busy.IN, value=0)

    def _command(self, command, data=None):
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(command)
        self.cs(1)
        if data is not None:
            self._data(data)

    def _data(self, data):
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(data)
        self.cs(1)

    def _wait_until_idle(self):
        while self.busy.value() == 1:
            sleep_ms(10)

    def hard_reset(self):
        self.rst(1)
        sleep_ms(10)
        self.rst(0)
        sleep_ms(10)
        self.rst(1)

    def soft_reset(self):
        self._command(SW_RESET)
        self._wait_until_idle()

    def deep_sleep(self):
        self._command(DEEP_SLEEP_MODE)

    def _update_common(self):
        self.hard_reset()
        self.soft_reset()

        # entry mode 3 (x increase, y increase -- POR)
        self._command(DATA_ENTRY_MODE_SETTING, b'\x03')

        # Start = 0x00, End = 0x0f (15 = 128/8-1)
        self._command(SET_RAM_X_ADDRESS_START_END_POSITION, b'\x00\x0F')

        # Start = 0x00, End = 0xF9 (250 - 1)
        self._command(SET_RAM_Y_ADDRESS_START_END_POSITION, b'\x00\x00\xf9\x00')

        # Set the X address counter to 0x00 (POR)
        self._command(SET_RAM_X_ADDRESS_COUNTER, b'\x00')

        # Set the Y address counter to 0x000 (POR)
        self._command(SET_RAM_Y_ADDRESS_COUNTER, b'\x00\x00')

    def update(self):
        self._update_common()

        self._command(WRITE_RAM, self._get_rotated_buffer())
        self._command(MASTER_ACTIVATION)
        self._wait_until_idle()

    def update_partial(self):
        self._update_common()

        # https://github.com/lewisxhe/GxEPD/blob/master/src/GxDEPG0213BN/GxDEPG0213BN.cpp

        # set up partial update
        self._command(WRITE_LUT_REGISTER, PART_UPDATE_LUT_TTGO_DKE)

        # self._command(SET_GATE_TIME, b'\x22')

        self._command(GATE_DRIVING_VOLTAGE_CONTROL, b'\x17')

        self._command(SOURCE_DRIVING_VOLTAGE_CONTROL, b'\x41\x00\x32')  # POR is b'\x41\xA8\x32'

        # POR is 0x00
        self._command(WRITE_VCOM_REGISTER, b'\x00')
        self._wait_until_idle()

        # POR is 0xFF (clock on, analog on, load temperature, display in mode 2, analog off, osc off)
        # here use 0x99: enable clock, load lut in mode 2, disable clock
        self._command(DISPLAY_UPDATE_CONTROL_2, b'\x99')
        self._command(MASTER_ACTIVATION)
        self._wait_until_idle()

        # POR is 0xC0 (VBD <- HIZ)
        # here use 0x0N = (GS transition LUTN)
        self._command(BORDER_WAVEFORM_CONTROL, b'\x01')
        self._wait_until_idle()

        self._command(WRITE_RAM, self._get_rotated_buffer())
        # here use 0xCF: enable clock, enable analog, display in mode 2, disable analog, osc off
        self._command(DISPLAY_UPDATE_CONTROL_2, b'\xCF')
        self._command(MASTER_ACTIVATION)
        self._wait_until_idle()

        # partial update leaves artifacts, draw again for a better image
        self._command(WRITE_RAM, self._get_rotated_buffer())
        self._command(DISPLAY_UPDATE_CONTROL_2, b'\xCF')
        self._command(MASTER_ACTIVATION)
        self._wait_until_idle()

    def _get_rotated_buffer(self):
        # no need to rotate
        if self._rotation == ROTATION_0:
            return self.buffer
        # create buffer and rotate
        size = EPD_WIDTH * EPD_HEIGHT // 8
        fbuffer = memoryview(bytearray(size))
        frame = framebuf.FrameBuffer(
            fbuffer, EPD_WIDTH, EPD_HEIGHT, framebuf.MONO_HLSB)
        # copy buffer
        if self._rotation == ROTATION_270:
            for x in range(self.width):
                for y in range(self.height):
                    frame.pixel(y, EPD_HEIGHT-x-1, self.pixel(x, y))
        if self._rotation == ROTATION_90:
            for x in range(self.width):
                for y in range(self.height):
                    frame.pixel(EPD_WIDTH-y-1, x, self.pixel(x, y))
            frame.scroll(-6, 0)
        if self._rotation == ROTATION_180:
            for i in range(size):
                fbuffer[size-i-1] = self.buffer[i]
            frame.scroll(-6, 0)
        return fbuffer
