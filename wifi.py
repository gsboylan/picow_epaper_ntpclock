from time import sleep_ms

import network
from micropython import const

_NETWORK_STAT_NO_IP = const(2)  # Not in the docs but can happen


class Wifi:
    DEFAULT_NUM_RETRIES = const(5)
    CONNECT_RETRY_PERIOD_MILLIS = const(1000)

    def __init__(self) -> None:
        self._wifi: network.WLAN = network.WLAN(network.STA_IF)

    def get_wlan_status(self):
        status = self._wifi.status()
        if status == network.STAT_IDLE:
            return "STAT_IDLE"
        elif status == network.STAT_CONNECTING:
            return "STAT_CONNECTING"
        elif status == _NETWORK_STAT_NO_IP:
            return "STAT_NO_IP"
        elif status == network.STAT_GOT_IP:
            return "STAT_GOT_IP"
        elif status == network.STAT_WRONG_PASSWORD:
            return "STAT_WRONG_PASSWORD"
        elif status == network.STAT_NO_AP_FOUND:
            return "STAT_NO_AP_FOUND"
        elif status == network.STAT_CONNECT_FAIL:
            return "STAT_CONNECT_FAIL"
        else:
            return "Unknown wlan status: {}".format(status)

    def tryConnectWlan(self, ssid: str, passw: str, retries: int = DEFAULT_NUM_RETRIES) -> bool:
        print("Activating wifi chip...")
        self._wifi.active(True)
        print(f"Looking for {ssid}...")
        self._wifi.connect(ssid, passw)

        remaining_tries = retries
        while remaining_tries >= 0:
            if self._wifi.status() in [
                network.STAT_GOT_IP,
                network.STAT_CONNECT_FAIL,
                network.STAT_WRONG_PASSWORD,
            ]:
                # Success or non-retryable error code
                break
            elif self._wifi.status() == _NETWORK_STAT_NO_IP:
                print("Connected but waiting on DHCP, resetting retries...")
                remaining_tries = retries

            print(f"Trying to connect, remaining tries: {remaining_tries}, checking again in {Wifi.CONNECT_RETRY_PERIOD_MILLIS//1000} seconds... [{self.get_wlan_status()}]")
            sleep_ms(Wifi.CONNECT_RETRY_PERIOD_MILLIS)
            remaining_tries = remaining_tries - 1

        if self._wifi.status() == network.STAT_GOT_IP:
            print(f"Connected, ifconfig is [{self._wifi.ifconfig()}] and RSSI is {self._wifi.status('rssi')}")
            return True
        else:
            print(f"Failed w/ status [{self.get_wlan_status()}]")
            return False

    def is_connected(self) -> bool:
        return self._wifi.isconnected()

    def deactivate_wifi(self) -> None:
        print("Deactivating wifi...")
        self._wifi.active(False)
        self._wifi.deinit()
        print("Deactivated.")
