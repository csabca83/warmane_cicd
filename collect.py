# source /media/csabi/Samsung_T7/VirtualEnvs/Warmane/bin/activate


import unittest
import os
# import boto3
import json
import requests
import random
# import pickle
from independent_functions.googleauthenticator import get_totp_token as get_mfa
from independent_functions.get_proxies import get_proxies
from independent_functions.wait_between import wait_between
from independent_functions.human_like_mouse_move import human_like_mouse_move
from time import sleep
from pydub import AudioSegment
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import TimeoutException


# Randomization Related
MIN_RAND = 0.64
MAX_RAND = 1.27
LONG_MIN_RAND = 4.78
LONG_MAX_RAND = 11.1


class Warmane(unittest.TestCase):

    previous_response = ""
    default_page_proxy = 0
    wittoken = os.environ.get("wittoken")
    warmane_acc = os.environ.get("warmane_acc")
    warmane_pass = os.environ.get("warmane_pass")
    access_token = os.environ.get("ACCESS_TOKEN")
    psid = os.environ.get("FB_ID")
    ack = os.environ.get("ACK")
    sck = os.environ.get("SCK")
    MFA = os.environ.get("mfa")
    fb_api_url = 'https://graph.facebook.com/v8.0/me/'
    filename = 'test.mp3'
    startpage = 'https://www.warmane.com/account'
    log_list = []
    proxy = 0
    cookies = "cookies.txt"
    cookie_worked = False
    # s3 = boto3.resource(
    #     's3',
    #     aws_access_key_id=ack,
    #     aws_secret_access_key=sck
    #     )
    # obj = s3.Object(
    #     'bucket-for-cookies',
    #     'cookies.txt'
    #     )
    stop_s3 = False
    headless = True
    options = None
    profile = None
    capabilities = None
    captcha_retries = 15

    # Setup options for webdriver
    def setUpOptions(self):
        self.options = webdriver.FirefoxOptions()
        self.options.headless = self.headless
        self.options.binary_location = os.environ.get("FIREFOX_BIN")

    # Enable Marionette, An automation driver for Mozilla's Gecko engine
    def setUpCapabilities(self):
        self.capabilities = webdriver.DesiredCapabilities.FIREFOX
        self.capabilities['marionette'] = True

    #  Setup settings
    def setUp(self, proxy=default_page_proxy):
        self.setUpOptions()
        self.setUpCapabilities()
        if proxy == 0:
            pass
        else:
            self.stop_s3 = True

            # Splitting the proxy because the port
            # needs to be an integer
            try:
                proxy, proxy_port = proxy.split(":")
            except AttributeError:
                self.test_run()

            self.options.set_preference(
                'network.proxy.type', 1
                )  # int
            self.options.set_preference(
                'network.proxy.socks', proxy
                )  # string
            self.options.set_preference(
                'network.proxy.socks_port', int(proxy_port)
                )  # int
            self.options.set_preference(
                'network.proxy.socks_version', 4
                )  # int
        setting_up = True

        while setting_up is True:
            try:
                self.driver = webdriver.Firefox(
                    options=self.options,
                    capabilities=self.capabilities,
                    firefox_profile=self.profile,
                    executable_path="./geckodriver"
                    )
                setting_up = False
            except Exception as e:
                print(e)
                try:
                    self.driver.quit()
                except Exception:
                    pass
                print("Driver unexpectedly closed, retrying....")

        self.driver.set_page_load_timeout(15)

    # def save_cookies(self):
    #     self.obj.delete()

    #     with open(self.cookies, "wb") as f:
    #         pickle.dump(self.driver.get_cookies(), f)

    #     with open('cookies.txt', 'rb') as data:
    #         self.obj.upload_fileobj(data)

    # def load_cookies(self):

    #     if self.stop_s3 is False:
    #         with open('cookies.txt', 'wb') as data:
    #             self.obj.download_fileobj(data)

    #         print("Got cookies from S3")
    #     else:
    #         pass
    #     try:
    #         with open(self.cookies, "rb") as f:
    #             cookies = pickle.load(f)
    #         self.driver.delete_all_cookies()
    #         have to be on a page before you can
    #         add any cookies, any page - does not matter which
    #         for cookie in cookies:
    #             Checks if the instance expiry a float
    #             if isinstance(cookie.get('expiry'), float):
    #                 it converts expiry cookie to an int
    #                 cookie['expiry'] = int(cookie['expiry'])
    #             self.driver.add_cookie(cookie)
    #     except Exception:
    #         print("No cookies found")

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
        response = requests.post(
            api_url,
            headers=headers,
            params=params,
            data=json.dumps(data)
            )

        print(response.content)
        print(data)

    def audioToText(self, wavaudiofilename):

        url = 'https://api.wit.ai/speech'
        headers = {
            'Authorization': f'Bearer {self.wittoken}',
            'Content-Type': 'audio/wav',
        }

        params = (
            ('v', '20200513'),
        )

        with open(wavaudiofilename, 'rb') as e:
            data = e.read()
        response = requests.post(
            url,
            headers=headers,
            params=params,
            data=data
            )

        data = response.json()

        return data["text"]

    def saveFile(self, content):
        with open(self.filename, "wb") as handle:
            for data in content.iter_content():
                handle.write(data)

    def something_went_wrong(self):
        print("!!!Something went wrong!!!")
        self.log_list = [
                     ("Unsuccessful try, "
                      "please try to run "
                      "the script chmod +x"
                      " geckodriver && "
                      "python collect.py"
                      " manually on"
                      " https://dashboard.heroku.com/"
                      "apps/warmane-app .")]
        self.send_text_message(self.log_list)
        self.driver.quit()
        os._exit(os.EX_OK)

    def recursive_retry(self):
        self.driver.quit()
        proxy = get_proxies()
        self.setUp(proxy)

        self.captcha_retries -= 1
        print(
            str(self.captcha_retries) +
            " retries left"
            )
        self.test_run()

    def captcha(self, n):

        try:
            self.driver.get(self.startpage)
            try:
                # self.load_cookies()
                sleep(2)
                self.driver.find_element_by_class_name("navigation-logo")
                self.driver.refresh()
            except Exception:
                self.driver.quit()
                print(f"{n} retries left")

                if n == 0 or n < 0:
                    os._exit(os.EX_OK)

                else:

                    proxy = get_proxies()
                    self.setUp(proxy)
                    self.captcha(n-1)
            try:
                self.driver.find_element_by_id("userID")
                print("Cookies are no longer working for this website")
            except NoSuchElementException:
                print("Cookies were loaded up successfully")
                self.cookie_worked = True
                sleep(2)

            if self.cookie_worked is not True:

                print("Opened the startpage, "
                      "checking the iframes for recaptcha")

                self.driver.implicitly_wait(10)
                outeriframe = self.driver.find_element_by_tag_name('iframe')
                outeriframe.click()

                allIframesLen = self.driver.find_elements_by_tag_name('iframe')
                audioBtnFound = False
                audioBtnIndex = -1

                for index in range(len(allIframesLen)):
                    self.driver.switch_to.default_content()
                    iframe = self.driver.find_elements_by_tag_name(
                        'iframe'
                        )[index]
                    self.driver.switch_to.frame(iframe)
                    self.driver.implicitly_wait(10)
                    try:
                        audioBtn = self.driver.find_element_by_id(
                            'recaptcha-audio-button'
                            ) or \
                                   self.driver.find_element_by_id(
                            'recaptcha-anchor'
                            )
                        action = ActionChains(self.driver)
                        human_like_mouse_move(action, audioBtn)
                        audioBtn.click()

                        audioBtnFound = True
                        audioBtnIndex = index
                        break
                    except Exception:
                        pass

                if audioBtnFound:
                    try:
                        while audioBtnFound:
                            href = self.driver.find_element_by_id(
                                'audio-source'
                                ).get_attribute(
                                    'src'
                                    )
                            response = requests.get(href, stream=True)
                            if self.previous_response == response:
                                pass
                            else:
                                href = self.driver.find_element_by_id(
                                    'audio-source'
                                    ).get_attribute(
                                        'src'
                                        )
                                response = requests.get(href, stream=True)
                                print("Check audio button")
                                self.saveFile(response)

                                print("Converting the mp3 audiofile to wav")
                                sound = AudioSegment.from_mp3("test.mp3")
                                sound = sound.export("test.wav", format='wav')
                                sound.close()

                                # os.getcwd() + '/' + "test.wav")
                                response = self.audioToText("test.wav")

                                print("Text from the response was: " +
                                      response)
                                print("Sending the text "
                                      "result back to captcha")

                                self.driver.switch_to.default_content()
                                iframe = self.driver.find_elements_by_tag_name(
                                    'iframe'
                                    )[audioBtnIndex]
                                self.driver.switch_to.frame(iframe)

                                try:
                                    if self.previous_response == response:
                                        print("Recaptcha solved")
                                        audioBtnFound = False
                                    else:
                                        inputbtn = \
                                            self.driver.find_element_by_id(
                                                'audio-response'
                                                )

                                        inputbtn.send_keys(response)

                                        inputbtn.send_keys(Keys.ENTER)

                                        sleep(random.randint(3, 5))
                                        errorMsg = \
                                            self.driver.\
                                            find_elements_by_class_name(
                                                'rc-audiochallenge'
                                                '-error-message'
                                                )[0]

                                    if errorMsg.text == "" or \
                                       errorMsg.\
                                       value_of_css_property('display') \
                                       == 'none':

                                        print("Recaptcha solved")
                                        audioBtnFound = False
                                    else:
                                        try:
                                            print("Captcha's response: " +
                                                  errorMsg.text)
                                            self.previous_response = response
                                        except Exception:
                                            print(
                                                "Captcha's response: " +
                                                errorMsg.value_of_css_property(
                                                    'display')
                                                    )
                                            self.previous_response = response
                                except Exception:
                                    print("Recaptcha solved")
                                    audioBtnFound = False

                    except Exception:
                        print('Recaptcha temporarily banned your IP')
                        self.driver.quit()
                        print("Driver Closed")
                        print(f"{n} retries left")
                        if n == 0 or n < 0:
                            print("Unsuccessful tries")
                            os._exit(os.EX_OK)

                        elif n == 3:
                            self.captcha(n-1)

                        else:
                            proxy = get_proxies()
                            self.setUp(proxy)
                            self.captcha(n-1)
                else:
                    print('Button not found.')
                    # self.send_text_message(log_list)
                    self.driver.quit()
                    print(f"{n} retries left")

                    if n == 0 or n < 0:
                        print("Unsuccessful tries")
                        os._exit(os.EX_OK)

                    elif n == 3:
                        self.captcha(n-1)

                    else:

                        proxy = get_proxies()
                        self.setUp(proxy)
                        self.captcha(n-1)

        except Exception:
            self.driver.quit()
            print(f"{n} retries left")

            if n == 0 or n < 0:
                print("Unsuccessful tries")
                self.send_text_message(
                    [("Unsuccessful try, "
                      "please try to run "
                      "the script chmod +x"
                      " geckodriver && "
                      "python collect.py"
                      " manually on"
                      " https://dashboard.heroku.com/"
                      "apps/warmane-app .")])
                sleep(15)
                os._exit(os.EX_OK)

            elif n == 3:
                self.captcha(n-1)

            else:

                proxy = get_proxies()
                self.setUp(proxy)
                self.captcha(n-1)

    # Main function
    def test_run(self):
        self.captcha(self.captcha_retries)

        try:
            if self.captcha_retries <= 0:
                raise Exception

        except Exception:
            self.something_went_wrong()

        if self.cookie_worked is True:
            try:
                self.driver.find_element_by_id(
                    "authCode"
                    ).send_keys(f"{get_mfa(self.MFA)}")

                self.driver.find_element_by_class_name("wm-ui-btn").click()
                print("Passed MFA successfully.")
            except NoSuchElementException:
                print("MFA wasn't requested")
                pass
        else:
            try:
                self.driver.switch_to.default_content()
                self.driver.find_element_by_id(
                    "userID"
                    ).send_keys(self.warmane_acc)
                self.driver.find_element_by_id(
                    "userPW"
                    ).send_keys(self.warmane_pass)
                self.driver.find_element_by_xpath(
                    "//button[@type='submit']"
                    ).click()

            except ElementClickInterceptedException or \
                    TimeoutException or \
                    Exception:
                print(
                    "Click/Timeout interception"
                    " happened retrying captcha."
                    )
                self.recursive_retry()

            except Exception as e:
                print(
                    "The following random"
                    f" exception has happened:{e}")
                self.recursive_retry()

            print(
                "Added UserID and Password and clicked on login"
                )
            self.driver.implicitly_wait(10)

            ##############################
            try:
                self.driver.find_element_by_id(
                    "authCode"
                    ).send_keys(f"{get_mfa(self.MFA)}")

                self.driver.find_element_by_class_name(
                    "wm-ui-btn"
                    ).click()
                print("Passed MFA successfully.")

            except TimeoutException:
                self.recursive_retry()

            except NoSuchElementException:
                print("MFA wasn't requested")
                pass

        self.driver.implicitly_wait(10)

        try:
            points_before = self.driver.find_element_by_class_name("myPoints")
            points_before = points_before.text
            self.driver.find_element_by_link_text("Collect points").click()
            self.driver.refresh()
            self.driver.implicitly_wait(10)
            current_points = self.driver.find_element_by_class_name("myPoints")
            if (points_before) == (current_points.text):
                self.log_list.append(
                    "You have not logged in-game today"
                    )
                self.log_list.append(
                    f"Your current points are: {current_points.text}"
                    )
                self.log_list.append("------------------")
            else:
                print("Daily points collected successfully")
                self.log_list.append("Daily points collected successfully")
                self.log_list.append(
                    f"Your current points are: {current_points.text}"
                    )
                self.log_list.append("------------------")
            # self.save_cookies()
            # print("Cookies were saved")

        except TimeoutException:
            self.recursive_retry()

        except NoSuchElementException:
            print("Daily points were already collected")
            self.log_list.append("Daily points were already collected")
            try:
                current_points = \
                    self.driver.find_element_by_class_name("myPoints")
            except NoSuchElementException or \
                    TimeoutException:
                self.recursive_retry()

            self.log_list.append(
                f"Your current points are: {current_points.text}"
                )
            self.log_list.append("------------------")
            # self.save_cookies()
            # print("Cookies were saved")
            self.driver.quit()

        except Exception:
            self.something_went_wrong()

        print("Successful script run")
        self.log_list.append("Successful script run")
        self.send_text_message(self.log_list)

        self.driver.quit()

    def tearDown(self):
        wait_between(10.13, 15.05)


if __name__ == "__main__":
    response = (unittest.main(exit=False).result.errors)

    if len(response) != 0:
        Warmane().send_text_message(response)
        Warmane().driver.quit()
    else:
        pass
