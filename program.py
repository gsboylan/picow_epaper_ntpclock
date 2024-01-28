from time import sleep_ms

import ntptime
from machine import RTC, SPI, Pin

from wifi import Wifi
from writer import Writer
import display
import wificreds
import monaspace_neon_medium
import DEPG0213BN
import waveshare_2_13_v3


def run():
    # epd = display.LandscapeDisplay()
    epd = DEPG0213BN.EPD(spi=SPI(1),
                         cs=Pin(waveshare_2_13_v3.CS_PIN),
                         dc=Pin(waveshare_2_13_v3.DC_PIN),
                         rst=Pin(waveshare_2_13_v3.RST_PIN),
                         busy=Pin(waveshare_2_13_v3.BUSY_PIN),
                         rotation=DEPG0213BN.ROTATION_90)
    epd.fill(0xFF)

    textwriter = Writer(epd, monaspace_neon_medium,
                        invert_mono=True,  # display black on white epaper
                        # swap_dimensions=True,  # screen is natively portrait
                        verbose=True)
    Writer.set_textpos(epd, textwriter.screenheight//2 - textwriter.height, 0)
    textwriter.set_clip(col_clip=True)
    textwriter.printstring("Hello!")

    epd.update_partial()
    # epd.show(display_type=display.DISPLAY_PARTIAL)
    # epd.sleep()
    print("done")

    # sleep_ms(5000)

    # epd.wipe()
    # epd.println("Finished font test...")
    # epd.println("Activating wifi...")
    # wifi = Wifi()

    # epd.println("Attempting to connect to SSID:")
    # epd.println(f"{wificreds.SSID}")
    # wlan = wifi.tryConnectWlan(wificreds.SSID, wificreds.PASS, 3)

    # if wlan:
    #     if wlan.isconnected():
    #         epd.println("Wlan was able to connect!")

    #     epd.println("Trying to fetch network time...")
    #     ntptime.settime()

    #     rtc = RTC()
    #     epd.println(f"Time is: {rtc.datetime()}")
    # else:
    #     epd.println("Wlan was not able to connect! Sad...")


if __name__ == "__main__":
    run()


#     epd.println("""
# This place is a message... and
# part of a system of
# messages... pay attention to
# it!

# Sending this message was
# important to us. We considered
# ourselves to be a powerful
# culture.

# This place is not a place of
# honor... no highly esteemed
# deed is commemorated here...
# nothing valued is here.

# What is here was dangerous and
# repulsive to us. This message
# is a warning about danger.

# The danger is in a particular
# location... it increases
# towards a center... the center
# of danger is here... of a
# particular size and shape, and
# below us.

# The danger is still present,
# in your time, as it was in ours.

# The danger is to the body, and
# it can kill.

# The form of the danger is an
# emanation of energy.

# The danger is unleashed only if
# you substantially disturb this
# place physically. This place is
# best shunned and left
# uninhabited.

# """)
