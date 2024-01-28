import network
from time import sleep_ms


class Wifi:
    def __init__(self) -> None:
        self._wifi: network.WLAN = network.WLAN(network.STA_IF)
        self._wifi.active(True)

    def get_wlan_status(self):
        status = self._wifi.status()
        if status == network.STAT_IDLE:
            return 'STAT_IDLE'
        elif status == network.STAT_CONNECTING:
            return 'STAT_CONNECTING'
        elif status == network.STAT_WRONG_PASSWORD:
            return 'STAT_WRONG_PASSWORD'
        elif status == network.STAT_NO_AP_FOUND:
            return 'STAT_NO_AP_FOUND'
        elif status == network.STAT_CONNECT_FAIL:
            return 'STAT_CONNECT_FAIL'
        elif status == network.STAT_GOT_IP:
            return 'STAT_GOT_IP'
        else:
            return "Unknown wlan status: {}".format(status)

    def tryConnectWlan(self, ssid: str, passw: str, retries: int) -> Optional[network.WLAN]:
        self._wifi.connect(ssid, passw)

        remaining_tries = retries
        while (remaining_tries >= 0):
            if self._wifi.status() < 0 or self._wifi.status() >= 3:
                break
            print(f"remaining tries: {remaining_tries}, Waiting... ({self.get_wlan_status()}")
            sleep_ms(1000)
            remaining_tries = remaining_tries - 1

        if self._wifi.status() != network.STAT_GOT_IP:
            print("DHCP failed ???")
            return None

        print(f"self._Wifi status is: [{self.get_wlan_status()}] and ifconfig is [{self._wifi.ifconfig()}]")
        return self._wifi
