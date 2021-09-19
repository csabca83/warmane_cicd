import requests
from datetime import datetime


def proxy_health_check(proxy):

    tbr = False

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
            timeout=3
            )
        end = datetime.now()
        time_result = str(end - start)

        if resp.status_code == 200:
            print(
                '{: <20}{: <9}{: <15}{: <14}'.format(
                    proxy, 'HEALTHY', '200', time_result)
                    )
            tbr = proxy

        else:
            pass

    except requests.exceptions.ConnectTimeout or \
            requests.exceptions.ConnectionError or \
            requests.exceptions.ReadTimeout:

        pass

    finally:

        try:
            s.close()
        except Exception:
            pass

        return tbr
