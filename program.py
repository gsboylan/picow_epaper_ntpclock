from time import sleep_ms

import ntptime
from machine import RTC

import monaspace_neon_medium
import wificreds
from display import LandscapeDisplay
from wifi import Wifi
from writer import Writer


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

    textwriter = Writer(
        epd,
        monaspace_neon_medium,
        invert_mono=True,  # display black on white epaper
        verbose=True,
    )
    textwriter.set_clip(col_clip=True)

    text_row = textwriter.screenheight // 2 - textwriter.height // 2
    text_col = textwriter.screenwidth // 2 - textwriter.stringlen("00:00") // 2

    def move_to_clock_position():
        Writer.set_textpos(device=epd, row=text_row, col=text_col)

    now = rtc.datetime()

    move_to_clock_position()
    textwriter.printstring(f"{now[4] - 5:02d}:{now[5]:02d}")
    epd.update_partial()
    epd.deep_sleep()
    sleep_ms(5000)
    move_to_clock_position()
    textwriter.printstring(f"{now[4]:02d}:{now[5]:02d}")
    epd.update_partial()
    epd.deep_sleep()
