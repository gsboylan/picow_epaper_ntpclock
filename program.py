from micropython import const
from time import sleep_ms
from machine import RTC, SPI, Pin

from wifi import Wifi
import wificreds
import ntptime

from writer import Writer
import monaspace_neon_medium
from display import LandscapeDisplay


def run():
    epd = LandscapeDisplay()
    epd.wipe()

    print("Activating wifi...")
    wifi = Wifi()

    print("Attempting to connect to SSID:")
    print(f"{wificreds.SSID}")
    wlan = wifi.tryConnectWlan(wificreds.SSID, wificreds.PASS, 3)

    if wlan:
        if wlan.isconnected():
            print("Wlan was able to connect!")

        print("Trying to fetch network time...")
        try:
            ntptime.settime()
        except Exception as e:
            print("Error, see logs!")
            print(e)

    else:
        print("Wlan was not able to connect! Sad...")
        return

    rtc = RTC()
    print(f"Time is: {rtc.datetime()}")

    textwriter = Writer(epd, monaspace_neon_medium,
                        invert_mono=True,  # display black on white epaper
                        verbose=True)
    textwriter.set_clip(col_clip=True)

    Writer.set_textpos(epd, textwriter.screenheight//2 - textwriter.height//2, textwriter.screenwidth//2 - textwriter.stringlen("00:00")//2)
    now = rtc.datetime()
    textwriter.printstring(f"{now[4] - 5:02d}:{now[5]:02d}")

    epd.update()
