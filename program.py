from time import ticks_diff, ticks_ms

import ntptime
import utime
from machine import (PWRON_RESET, RTC, Pin, Timer, enable_irq, lightsleep,
                     reset_cause)
from micropython import const

import monaspace_neon_medium
import wificreds
from display import LandscapeDisplay
from wifi import Wifi
from writer import Writer

DTT_YEAR = const(0)
DTT_MONTH = const(1)
DTT_DAY = const(2)
DTT_WEEKDAY = const(3)
DTT_HOUR = const(4)
DTT_MINUTE = const(5)
DTT_SECOND = const(6)

NTP_SYNC_RETRIES = const(5)

# these are (hour, minute), None = match all
FULL_REFRESH_AT = (None, None, None, None, None, const(30), None)  # On the half hour
NTP_SYNC_AT = (None, None, None, None, const(0), const(0), None)  # at 00:00 midnight

TIME_ZONE = -5  # Eastern Standard Time


epd = LandscapeDisplay()

wifi = Wifi()
rtc = RTC()

textwriter = Writer(
    epd,
    monaspace_neon_medium,
    invert_mono=True,  # display black on white epaper
    verbose=True,
)
textwriter.set_clip(col_clip=True)


def vcenter_hcenter_Writer(num_chars: int) -> None:
    Writer.set_textpos(device=epd, row=(textwriter.screenheight - textwriter.height) // 2, col=(textwriter.screenwidth - textwriter.stringlen("0" * num_chars)) // 2)


def move_to_clock_position():
    vcenter_hcenter_Writer(5)


def attempt_ntp_sync() -> None:
    print(f"Attempting to fetch ntp time... current machine.RTC time is {rtc.datetime()}")
    try:
        connect_successful = wifi.tryConnectWlan(wificreds.SSID, wificreds.PASS)

        if connect_successful:
            print("Connected, fetching time...")
            ntptime.timeout = 4  # seconds
            ntptime.settime()
            print(f"New time is {rtc.datetime()}")

        else:
            print("Failed to connect to network")

    except Exception as e:
        print("Error, see logs!")
        print(e)

    finally:
        wifi.deactivate_wifi()


#  Only param 1 should have None entries, for sanity
def dtt_matches(current_time: tuple, match_against: tuple) -> bool:
    for i in range(len(match_against)):
        if match_against[i] is not None and match_against[i] != current_time[i]:
            return False
    return True


def update_display() -> int:
    start_ms = ticks_ms()

    current_time = rtc.datetime()
    move_to_clock_position()
    textwriter.printstring(f"{' ' if current_time[DTT_HOUR] < 10 else ''}{current_time[DTT_HOUR]}:{current_time[DTT_MINUTE]:02d}")

    # TODO: print date on the bottom row

    # TODO: print last sync time (wifi icon?)

    if dtt_matches(current_time, FULL_REFRESH_AT):
        epd.update()
    else:
        epd.update_partial()
    epd.deep_sleep()

    delta_ms = ticks_diff(ticks_ms(), start_ms)
    print(f"{current_time[DTT_HOUR]:02d}:{current_time[DTT_MINUTE]:02d} - Updated display in {delta_ms/1000:.3f}s")
    return delta_ms


def run():
    epd.wipe()
    attempt_ntp_sync()
    should_retry_ntp = False
    while True:
        delta_ms = update_display()

        if dtt_matches(rtc.datetime(), NTP_SYNC_AT) or should_retry_ntp:
            ntp_success = attempt_ntp_sync()
            if ntp_success:
                should_retry_ntp = False
            else:
                print("Will retry NTP on next run")
                should_retry_ntp = True

        ms_to_next_minute = ((60 - rtc.datetime()[DTT_SECOND]) * 1000) - delta_ms
        print(f"Sleeping for {ms_to_next_minute} ms")
        lightsleep(ms_to_next_minute)
