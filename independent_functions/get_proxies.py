import random
import requests
from time import sleep


def get_proxies():

    try:

        url = ("https://api.proxyscrape.com/"
               "v2/"
               "?request=displayproxies"
               "&"
               "protocol=socks4"
               "&"
               "timeout=100"
               "&"
               "country=all"
               "&"
               "ssl=all"
               "&"
               "anonymity=elite")

        resp = requests.get(url)

        proxies = (resp.text).splitlines()

        selected_proxy = random.choice(proxies)

        print(f"The following proxy were selected: {selected_proxy}")

        return selected_proxy

    except Exception:
        sleep(10)
        get_proxies()
