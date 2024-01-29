from machine import SPI, Pin
from micropython import const

import DEPG0213BN

SPI_MODULE = const(1)
CS_PIN = const(9)
DC_PIN = const(8)
RST_PIN = const(12)
BUSY_PIN = const(13)


class LandscapeDisplay(DEPG0213BN.EPD):
    def __init__(self):
        super().__init__(
            spi=SPI(SPI_MODULE),
            cs=Pin(CS_PIN),
            dc=Pin(DC_PIN),
            rst=Pin(RST_PIN),
            busy=Pin(BUSY_PIN),
            rotation=DEPG0213BN.ROTATION_90,
        )
        self.text_row = 1
        self.fill(0xFF)

    def wipe(self):
        self.fill(0xFF)
        self.text_row = 1
        self.update()

    def clear_screen(self):
        self._command(DEPG0213BN.WRITE_RAM, [0xFF] * self.height * (self.width // 8))

    def println(self, text: str, x: int = 0):
        for line in text.strip().splitlines():
            y = self.text_row * 10

            if self.text_row == 12:
                self.scroll(0, -10)
                self.rect(0, self.height - 10, self.width, 10, 0xFF, True)
            else:
                self.text_row += 1

            print(f"({x}, {y})\t|| {line}")
            self.text(line, x, y, 0x00)
            self.update_partial()
