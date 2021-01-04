from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from pydub import AudioSegment
import numpy as np
import scipy.interpolate as si
import json, sys
from googleauthenticator import get_mfa
import os, sys, boto3
import time, requests, random, pickle
from fake_useragent import UserAgent


class Warmane:

    def __init__(self):

        with open("secrets.json", "r") as f:
            json_data = json.load(f)

        self.wittoken = json_data["wittoken"]
        self.warmane_acc = json_data["warmane_acc"]
        self.warmane_pass = json_data["warmane_pass"]
        self.access_token = json_data["ACCESS_TOKEN"]
        self.psid = json_data["CSABI"]
        self.ack = json_data["ACK"]
        self.sck = json_data["SCK"]
        self.fb_api_url = 'https://graph.facebook.com/v8.0/me/'
        self.filename = 'test.mp3'
        self.startpage = 'https://www.warmane.com/account'
        self.log_list = []
        self.proxy = 0
        self.cookies = "cookies.txt"
        self.cookie_worked = False
        self.s3 = boto3.resource('s3', aws_access_key_id = self.ack, aws_secret_access_key = self.sck)
        self.obj = self.s3.Object('bucket-for-cookies','cookies.txt')

    def save_cookies(self):
        self.obj.delete()

        pickle.dump(self.driver.get_cookies(), open(self.cookies, "wb"))

        with open('cookies.txt', 'rb') as data:
            self.obj.upload_fileobj(data)


    def load_cookies(self):

        with open('cookies.txt', 'wb') as data:
            self.obj.download_fileobj(data)

        cookies = pickle.load(open(self.cookies, "rb"))
        self.driver.delete_all_cookies()
        # have to be on a page before you can add any cookies, any page - does not matter which
        for cookie in cookies:
            if isinstance(cookie.get('expiry'), float):#Checks if the instance expiry a float 
                cookie['expiry'] = int(cookie['expiry'])# it converts expiry cookie to a int
            self.driver.add_cookie(cookie)

    def get_proxies(self):

        try:
            proxy_listed = []
            res = requests.get('https://free-proxy-list.net/', headers={'User-Agent':'Mozilla/5.0'})
            soup = BeautifulSoup(res.text,"lxml")
            for items in soup.select("#proxylisttable tbody tr"):

                for item in items.select("td", class_="hx sorting_1")[::6]:
                    if "yes" in item.text:
                        proxy_list = ':'.join([item.text for item in items.select("td")[:2]])
                        proxy_listed.append(proxy_list)

                    else:
                        pass
            ip_range = len(proxy_listed)

            random_proxy = random.randint(0, ip_range)

            selected_proxy = proxy_listed[random_proxy]

            print(f"The following proxy were selected: {selected_proxy}")

            return selected_proxy

        except:
            time.sleep(10)
            self.get_proxies()

    def setup_chrome(self, proxy):

        ua = UserAgent()
        user_agent = ua.random
        #print(f"Using the following user agent: {user_agent}")

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--disable-notifications")
        chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")#"/usr/bin/google-chrome-stable"
        chrome_options.add_argument("--headless")
        #chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows Phone 10.0; Android 4.2.1; Microsoft; Lumia 640 XL LTE) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Mobile Safari/537.36 Edge/12.10166")
        #chrome_options.add_argument('--profile-directory="Default"')
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument(f'user-agent={user_agent}')
        if proxy == 0:
            pass
        else:
            chrome_options.add_argument(f'--proxy-server={proxy}')

        driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=chrome_options)#"/media/csabi/Samsung T7/VScode/heroku test/heroku_warmane/chromedriver", options=chrome_options)
        driver.set_page_load_timeout(120)

        self.driver = driver

    # Using B-spline for simulate humane like mouse movments
    def human_like_mouse_move(self, action, start_element):
        points = [[6, 2], [3, 2],[0, 0], [0, 2]]
        points = np.array(points)
        x = points[:,0]
        y = points[:,1]

        t = range(len(points))
        ipl_t = np.linspace(0.0, len(points) - 1, 100)

        x_tup = si.splrep(t, x, k=1)
        y_tup = si.splrep(t, y, k=1)

        x_list = list(x_tup)
        xl = x.tolist()
        x_list[1] = xl + [0.0, 0.0, 0.0, 0.0]

        y_list = list(y_tup)
        yl = y.tolist()
        y_list[1] = yl + [0.0, 0.0, 0.0, 0.0]

        x_i = si.splev(ipl_t, x_list)
        y_i = si.splev(ipl_t, y_list)

        startElement = start_element

        action.move_to_element(startElement)
        action.perform()

        c = 5 # change it for more move
        i = 0
        for mouse_x, mouse_y in zip(x_i, y_i):
            action.move_by_offset(mouse_x,mouse_y)
            action.perform()
            i += 1
            if i == c:
                break


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

    def audioToText(self, wavaudiofilename):

        url = 'https://api.wit.ai/speech'
        headers = {
            'Authorization': f'Bearer {self.wittoken}',
            'Content-Type': 'audio/wav',
        }

        params = (
            ('v', '20200513'),
        )

        data = open(wavaudiofilename, 'rb').read()
        response = requests.post(url, headers=headers, params=params, data=data)

        json_data = response.json()

        return json_data["text"]

    def saveFile(self, content):
        with open(self.filename, "wb") as handle:
            for data in content.iter_content():
                handle.write(data)

    def captcha(self, n):
        
        try:
            time.sleep(2)
            self.driver.get(self.startpage)
            time.sleep(2)
            try:
                self.load_cookies()
                print("Got cookies from S3")
                time.sleep(2)
                self.driver.find_element_by_class_name("navigation-logo")
                time.sleep(5)
                self.driver.refresh()
            except:
                self.driver.quit()
                print(f"{n} retries left")

                if n == 0 or n < 0:
                    sys.exit()

                else:

                    proxy = self.get_proxies()
                    self.setup_chrome(proxy)
                    self.captcha(n-1)
            try:
                self.driver.find_element_by_id("userID")
            except:
                print("Cookies were loaded up successfully")
                self.cookie_worked = True
                time.sleep(2)
            
            if self.cookie_worked == True:
                pass
            else:

                print("Opened the startpage and now checking the iframes for recaptcha")

                self.driver.implicitly_wait(30)
                outeriframe = self.driver.find_element_by_tag_name('iframe')
                outeriframe.click()


                allIframesLen = self.driver.find_elements_by_tag_name('iframe')
                audioBtnFound = False
                audioBtnIndex = -1

                for index in range(len(allIframesLen)):
                    self.driver.switch_to.default_content()
                    iframe = self.driver.find_elements_by_tag_name('iframe')[index]
                    self.driver.switch_to.frame(iframe)
                    self.driver.implicitly_wait(10)
                    try:
                        audioBtn = self.driver.find_element_by_id('recaptcha-audio-button') or self.driver.find_element_by_id('recaptcha-anchor')
                        action =  ActionChains(self.driver)
                        self.human_like_mouse_move(action, audioBtn)
                        audioBtn.click()

                        time.sleep(random.randint(5, 10))

                        audioBtnFound = True
                        audioBtnIndex = index
                        break
                    except Exception as e:
                        pass

                if audioBtnFound:
                    try:
                        while True:
                            print("Check audio button")
                            href = self.driver.find_element_by_id('audio-source').get_attribute('src')
                            response = requests.get(href, stream=True)

                            self.saveFile(response)


                            print("Converting the mp3 audiofile to wav")
                            sound = AudioSegment.from_mp3("test.mp3")
                            sound.export("test.wav", format='wav')

                            response = self.audioToText("test.wav") #os.getcwd() + '/' + "test.wav")

                            print("Text from the response was: " + response)
                            print("Sending the text result back to captcha")

                            self.driver.switch_to.default_content()
                            iframe = self.driver.find_elements_by_tag_name('iframe')[audioBtnIndex]
                            self.driver.switch_to.frame(iframe)

                            try:
                                inputbtn = self.driver.find_element_by_id('audio-response')

                                action =  ActionChains(self.driver)
                                self.human_like_mouse_move(action, inputbtn)
                                inputbtn.send_keys(response)

                                inputbtn.send_keys(Keys.ENTER)
                                
                                time.sleep(random.randint(10, 12))
                                errorMsg = self.driver.find_elements_by_class_name('rc-audiochallenge-error-message')[0]

                                if errorMsg.text == "" or errorMsg.value_of_css_property('display') == 'none':

                                    print("Recaptcha solved")
                                    break
                                try:
                                    print("Captcha's response: " + errorMsg.text)
                                except:
                                    print("Captcha's response: " + errorMsg.value_of_css_property('display'))
                            except:
                                print("Recaptcha solved")
                                break
                            
                    except Exception as e:
                        print(e)
                        print('Recaptcha temporarily banned your IP')
                        self.driver.quit()
                        print("Driver Closed")
                        print(f"{n} retries left")
                        if n == 0 or n < 0:
                            sys.exit()
                        else:
                            proxy = self.get_proxies()
                            self.setup_chrome(proxy)
                            self.captcha(n-1)
                else:
                    print('Button not found.')
                    #self.send_text_message(log_list)
                    self.driver.quit()
                    print(f"{n} retries left")

                    if n == 0 or n < 0:
                        sys.exit()

                    else:

                        proxy = self.get_proxies()
                        self.setup_chrome(proxy)
                        self.captcha(n-1)
        except:
            self.driver.quit()
            print(f"{n} retries left")

            if n == 0 or n < 0:
                sys.exit()

            else:

                proxy = self.get_proxies()
                self.setup_chrome(proxy)
                self.captcha(n-1)        

    def run_page(self):

        self.captcha(5)

        if self.cookie_worked == True:
            try:
                self.driver.find_element_by_id("authCode").send_keys(f"{get_mfa()}")

                self.driver.find_element_by_class_name("wm-ui-btn").click()
                print("Passed MFA successfully.")
            except NoSuchElementException:
                print("MFA wasn't requested")
                pass
        else:
            self.driver.switch_to.default_content()

            self.driver.find_element_by_id("userID").send_keys(self.warmane_acc)
            self.driver.find_element_by_id("userPW").send_keys(self.warmane_pass)
            self.driver.find_element_by_xpath("//button[@type='submit']").click()

            print("Added UserID and Password and clicked on login")
            self.driver.implicitly_wait(10)

            ##############################
            try:
                self.driver.find_element_by_id("authCode").send_keys(f"{get_mfa()}")

                self.driver.find_element_by_class_name("wm-ui-btn").click()
                print("Passed MFA successfully.")
            except NoSuchElementException:
                print("MFA wasn't requested")
                pass

        self.driver.implicitly_wait(10)

        try:
            self.driver.find_element_by_link_text("Collect points").click()
            print("Daily points collected successfully")
            self.log_list.append("Daily points collected successfully")
            current_points = self.driver.find_element_by_class_name("myPoints")
            self.log_list.append(f"Your current points are: {current_points.text}")
            self.log_list.append("------------------")
            self.save_cookies()
            print("Cookies were uploaded successfully")
        except NoSuchElementException:
            print("Daily points were already collected")
            self.log_list.append("Daily points were already collected")
            current_points = self.driver.find_element_by_class_name("myPoints")
            self.log_list.append(f"Your current points are: {current_points.text}")
            self.log_list.append("------------------")

        except:
            print("!!!Something went wrong!!!")
            self.log_list.append("!!!Something went wrong!!!")
            self.send_text_message(self.log_list)
            self.driver.quit()
            sys.exit()

        print("Successful script run")
        self.log_list.append("Successful script run")
        self.send_text_message(self.log_list)

        self.driver.quit()

if __name__ == "__main__":
    b = Warmane()
    b.setup_chrome(0)
    b.run_page()