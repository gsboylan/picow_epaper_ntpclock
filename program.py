from time import ticks_diff, ticks_ms

import ntptime
from machine import RTC, Pin, lightsleep
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

# these are (hour, minute), None => match all, value => match multiples of that value
FULL_REFRESH_AT = (None, None, None, None, None, const(30), None)  # On the half hour
NTP_SYNC_AT = (None, None, None, None, const(0), const(0), None)  # at 00:00 midnight

UTC_OFFSET = -5  # Eastern Standard Time


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


def attempt_ntp_sync() -> bool:
    print(f"Attempting to fetch ntp time... current machine.RTC time is {rtc.datetime()}")
    try:
        indicator = Pin("LED", Pin.OUT, value=1)
        connect_successful = wifi.tryConnectWlan(wificreds.SSID, wificreds.PASS)

        if connect_successful:
            print("Connected, fetching time...")
            ntptime.timeout = 4  # seconds
            ntptime.settime()
            print(f"New time is {rtc.datetime()}")
            return True

        else:
            print("Failed to connect to network")

    except Exception as e:
        print("Error, see logs!")
        print(e)

    finally:
        indicator.off()
        del indicator
        wifi.deactivate_wifi()

    return False


#  Only param 1 should have None entries, for sanity
def dtt_matches(current_time: tuple, match_against: tuple) -> bool:
    for i in range(len(match_against)):
        if match_against[i] is not None:
            if match_against[i] == 0:
                if current_time[i] != 0:
                    return False

            if not current_time[i] % match_against[i] == 0:
                return False

    return True


def update_display() -> int:
    start_ms = ticks_ms()

    move_to_clock_position()

    current_time = rtc.datetime()
    twelve_hour_time = current_time[DTT_HOUR] % 12
    local_twelve = twelve_hour_time + UTC_OFFSET
    if local_twelve < 0:
        local_twelve += 12

    textwriter.printstring(f"{' ' if local_twelve < 10 else ''}{local_twelve}:{current_time[DTT_MINUTE]:02d}")

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
    ntp_succeeded = attempt_ntp_sync()
    while True:
        if dtt_matches(rtc.datetime(), NTP_SYNC_AT) or not ntp_succeeded:
            ntp_succeeded = attempt_ntp_sync()
            if not ntp_succeeded:
                print("Will retry NTP on next run")

        update_display()
        ms_to_next_minute = (60 - rtc.datetime()[DTT_SECOND]) * 1000
        print(f"Sleeping for {ms_to_next_minute} ms")
        # On the RP2 port of upython, this is the lowest energy mode that keeps the RTC running
        lightsleep(ms_to_next_minute)
