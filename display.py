from waveshare_2_13_v3 import BUSY_PIN, CS_PIN, DC_PIN, RST_PIN, EPD_2in13_V3_Landscape

DISPLAY_NORMAL = 0
DISPLAY_BASE = 1
DISPLAY_PARTIAL = 2


class LandscapeDisplay(EPD_2in13_V3_Landscape):
    def __init__(self, rst_pin: int = RST_PIN,
                 dc_pin: int = DC_PIN,
                 cs_pin: int = CS_PIN,
                 busy_pin: int = BUSY_PIN,
                 print_reads: bool = False):
        super().__init__(rst_pin, dc_pin, cs_pin, busy_pin, print_reads)
        self.text_row = 1
        self.Clear()
        self.fill(0xff)

    def wipe(self):
        self.fill(0xFF)
        self.text_row = 1
        self.show(DISPLAY_BASE)

    def show(self, display_type: int = DISPLAY_NORMAL):
        if display_type == DISPLAY_NORMAL:
            self.display(self.buffer)
        elif display_type == DISPLAY_BASE:
            self.display_Base(self.buffer)
        elif display_type == DISPLAY_PARTIAL:
            self.display_Partial(self.buffer)

    def println(self, text: str, x: int = 0):
        for line in text.strip().splitlines():
            y = self.text_row * 10

            if self.text_row == 12:
                self.scroll(0, -10)
                self.rect(0, self.height-10, self.width, 10, 0xFF, True)
                self.show()
            else:
                self.text_row += 1

            print(f"({x}, {y})\t|| {line}")
            self.text(line, x, y, 0x00)
            self.show()

    def render_buf_to_logs(self):
        # device native dimensions swap width/height
        for row in range(self.width):
            line = (
                "|"
                + "".join(
                    f"{' ' if self.pixel(col, row) else 'X'}"
                    for col in range(self.height)
                )
                + "|"
            )
            print(line)

    def render_braille_to_logs(self):
        for row in range(0, self.width // 4):
            line = "".join(
                self.get_braille_at(col, row) for col in range(0, self.height // 2)
            )
            print(line)

    def get_braille_at(self, col, row):
        base = 0
        base += (not self.pixel(col * 2, row * 4)) << 0
        base += (not self.pixel(col * 2, row * 4 + 1)) << 1
        base += (not self.pixel(col * 2, row * 4 + 2)) << 2
        base += (not self.pixel(col * 2, row * 4 + 3)) << 6
        base += (not self.pixel(col * 2 + 1, row * 4)) << 3
        base += (not self.pixel(col * 2 + 1, row * 4 + 1)) << 4
        base += (not self.pixel(col * 2 + 1, row * 4 + 2)) << 5
        base += (not self.pixel(col * 2 + 1, row * 4 + 3)) << 7
        base += 0x2800

        return chr(base)
