import random
import requests
from time import sleep
from concurrent.futures import ThreadPoolExecutor, as_completed
from independent_functions.proxy_health_check import proxy_health_check


def get_proxies():

    try:

        url = ("https://api.proxyscrape.com/"
               "v2/"
               "?"
               "request=displayproxies"
               "&"
               "protocol=socks4"
               "&"
               "timeout=200"
               "&"
               "country=all"
               "&"
               "ssl=all"
               "&"
               "anonymity=elite")

        resp = requests.get(url)

        proxies = (resp.text).splitlines()
        random.shuffle(proxies)
        pool_number = len(proxies)
        healthy_proxies = []
        print(
            '{: <20}{: <9}{: <15}{: <14}'.format(
                'IP', 'HEALTH', 'RESP', 'MS')
        )

        with ThreadPoolExecutor(max_workers=pool_number) as executor:
            futures = [
                executor.submit(proxy_health_check, proxy)
                for proxy in proxies
                ]

            for future in as_completed(futures):
                result = future.result()
                if result:
                    healthy_proxies.append(result)

        if healthy_proxies == []:
            print("None of the proxies met with the defined latency")
            raise Exception

        healthy_proxies = random.choice(healthy_proxies)

        print(f"The following proxy were selected: {healthy_proxies}")

        return healthy_proxies

    except Exception as e:
        print(e)
        sleep(5)
        get_proxies()
