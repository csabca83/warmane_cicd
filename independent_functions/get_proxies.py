from time import sleep
from lxml.html import fromstring
import requests
import random


def get_proxies():

    try:
        url = 'https://free-proxy-list.net/'
        response = requests.get(url)
        parser = fromstring(response.text)
        proxies = []
        for i in parser.xpath('//tbody/tr')[:299]:  # 299 proxies max
            proxy = [i.xpath(
                        './/td[1]/text()'
                        )[0], i.xpath(
                            './/td[2]/text()'
                            )[0]]

            proxies.append(proxy)

        ip_range = len(proxies)

        random_proxy = random.randint(0, ip_range)

        selected_proxy = proxies[random_proxy]

        print(f"The following proxy were selected: {selected_proxy}")

        return selected_proxy

    except Exception:
        sleep(10)
        get_proxies()
