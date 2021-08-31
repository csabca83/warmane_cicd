import requests
from datetime import datetime


def proxy_health_check(proxy):

    proxies = {
        "http": f'socks4://{proxy}',
        "https": f'socks4://{proxy}'
        }
    url = 'https://www.warmane.com/'

    req = requests.Request(
        'GET',
        url
    )

    s = requests.Session()
    s.proxies = proxies
    prepped = s.prepare_request(req)

    try:
        start = datetime.now()
        resp = s.send(
            prepped,
            timeout=0.05
            )
        end = datetime.now()
        time_result = str(end - start)

        if resp.status_code == 200:
            print(f"{proxy} - HEALTHY - {resp.status_code} - {time_result}")
            return proxy

        else:
            return False

    except requests.exceptions.ConnectTimeout:

        return False

    except requests.exceptions.ConnectionError:

        return False

    except requests.exceptions.ReadTimeout:

        return False
