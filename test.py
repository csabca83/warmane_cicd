import sys
import unittest
import logging, json, requests

lista = []

class TestCase(unittest.TestCase):

    with open("secrets.json", "r") as f:
        json_data = json.load(f)

    previous_response = ""
    default_page_proxy = 0
    wittoken = json_data["wittoken"]
    warmane_acc = json_data["warmane_acc"]
    warmane_pass = json_data["warmane_pass"]
    access_token = json_data["ACCESS_TOKEN"]
    psid = json_data["CSABI"]
    ack = json_data["ACK"]
    sck = json_data["SCK"]
    fb_api_url = 'https://graph.facebook.com/v8.0/me/'
    filename = 'test.mp3'
    startpage = 'https://www.warmane.com/account'
    log_list = []
    error_list = []
    proxy = 0
    cookies = "cookies.txt"
    cookie_worked = False
    stop_s3 = False
    headless = True
    options = None
    profile = None
    capabilities = None

    def test_fail(self):
        asd

    def send_text_message(self, message):

        message = ('\n'.join(map(str, message)))

        headers = {
            'Content-Type': 'application/json'
        }

        data = {
            'messaging_type': 'RESPONSE',
            'recipient': {'id': self.psid},
            'message': {'text': message}
        }

        params = {'access_token': self.access_token}
        api_url = self.fb_api_url + 'messages'
        response = requests.post(api_url, headers=headers, params=params, data=json.dumps(data))

        print(response.content)
        print(data)

if __name__ == "__main__":
    response = (unittest.main(exit=False).result.errors)

    if len(response) != 0:
        Warmane().send_text_message(response)
    else:
        pass

