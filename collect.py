
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from pydub import AudioSegment
import numpy as np
import scipy.interpolate as si
import requests, json, sys
from googleauthenticator import get_mfa
import os, sys
import time,requests

with open("secrets.json", "r") as f:
    json_data = json.load(f)

wittoken = json_data["wittoken"]
warmane_acc = json_data["warmane_acc"]
warmane_pass = json_data["warmane_pass"]
access_token = json_data["ACCESS_TOKEN"]
psid = json_data["CSABI"]
fb_api_url = 'https://graph.facebook.com/v8.0/me/'
filename = 'test.mp3'
startpage = 'https://www.warmane.com/account/login'

chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=chrome_options)
log_list = []

# Using B-spline for simulate humane like mouse movments
def human_like_mouse_move(action, start_element):
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


def send_text_message(message):

    message = ('\n'.join(map(str, message)))

    headers = {
        'Content-Type': 'application/json'
    }

    data = {
        'messaging_type': 'RESPONSE',
        'recipient': {'id': psid},
        'message': {'text': message}
    }

    params = {'access_token': access_token}
    api_url = fb_api_url + 'messages'
    response = requests.post(api_url, headers=headers, params=params, data=json.dumps(data))

    print(response.content)
    print(data)

def audioToText(wavaudiofilename):

    url = 'https://api.wit.ai/speech'
    headers = {
        'Authorization': f'Bearer {wittoken}',
        'Content-Type': 'audio/wav',
    }

    params = (
        ('v', '20200513'),
    )

    data = open(wavaudiofilename, 'rb').read()
    response = requests.post(url, headers=headers, params=params, data=data)

    json_data = response.json()

    return json_data["text"]

def saveFile(content,filename):
    with open(filename, "wb") as handle:
        for data in content.iter_content():
            handle.write(data)


driver.get(startpage)

log_list.append("Opened the startpage and now checking the iframes for recaptcha")
log_list.append("------------------")
print("Opened the startpage and now checking the iframes for recaptcha")

driver.implicitly_wait(50)
outeriframe = driver.find_element_by_tag_name('iframe')
outeriframe.click()

allIframesLen = driver.find_elements_by_tag_name('iframe')
audioBtnFound = False
audioBtnIndex = -1

for index in range(len(allIframesLen)):
    driver.switch_to.default_content()
    iframe = driver.find_elements_by_tag_name('iframe')[index]
    driver.switch_to.frame(iframe)
    driver.implicitly_wait(10)
    try:
        audioBtn = driver.find_element_by_id('recaptcha-audio-button') or driver.find_element_by_id('recaptcha-anchor')
        action =  ActionChains(driver)
        human_like_mouse_move(action, audioBtn)
        audioBtn.click()

        time.sleep(5)

        audioBtnFound = True
        audioBtnIndex = index
        break
    except Exception as e:
        pass

if audioBtnFound:
    try:
        while True:
            log_list.append("Check audio button")
            log_list.append("------------------")
            print("Check audio button")
            href = driver.find_element_by_id('audio-source').get_attribute('src')
            response = requests.get(href, stream=True)

            saveFile(response,filename)

            log_list.append("Converting the mp3 audiofile to wav")
            log_list.append("------------------")
            print("Converting the mp3 audiofile to wav")
            sound = AudioSegment.from_mp3("test.mp3")
            sound.export("test.wav", format='wav')

            response = audioToText("test.wav") #os.getcwd() + '/' + "test.wav")

            log_list.append("Text from the response was: " + response)
            log_list.append("------------------")
            print("Text from the response was: " + response)

            driver.switch_to.default_content()
            iframe = driver.find_elements_by_tag_name('iframe')[audioBtnIndex]
            driver.switch_to.frame(iframe)

            log_list.append("Sending the text result back to captcha")
            log_list.append("------------------")
            print("Sending the text result back to captcha")
            try:
                inputbtn = driver.find_element_by_id('audio-response')

                action =  ActionChains(driver)
                human_like_mouse_move(action, inputbtn)

                inputbtn.send_keys(response)
                inputbtn.send_keys(Keys.ENTER)

                log_list.append("Sending the text result back to captcha")
                log_list.append("------------------")
                print("Sending the text result back to captcha")
                
                time.sleep(2)
                errorMsg = driver.find_elements_by_class_name('rc-audiochallenge-error-message')[0]

                if errorMsg.text == "" or errorMsg.value_of_css_property('display') == 'none':

                    log_list.append("Recaptcha solved")
                    log_list.append("------------------")
                    print("Recaptcha solved")
                    break
                try:
                    log_list.append("Captcha's response: " + errorMsg.text)
                    log_list.append("------------------")
                    print("Captcha's response: " + errorMsg.text)
                except:
                    log_list.append("Captcha's response: " + errorMsg.value_of_css_property('display'))
                    log_list.append("------------------")
                    print("Captcha's response: " + errorMsg.value_of_css_property('display'))
            except:
                log_list.append("Recaptcha solved")
                log_list.append("------------------")
                print("Recaptcha solved")
                break
             
    except Exception as e:
        print(e)
        log_list.append('Recaptcha temporarily banned your IP')
        log_list.append("------------------")
        print('Recaptcha temporarily banned your IP')
        driver.quit()
        log_list.append("Driver Closed")
        print("Driver Closed")
        send_text_message(log_list)
        sys.exit()
else:
    print('Button not found.')
    send_text_message(log_list)
    driver.quit()
    sys.exit()

driver.switch_to.default_content()

driver.find_element_by_id("userID").send_keys(warmane_acc)
driver.find_element_by_id("userPW").send_keys(warmane_pass)
driver.find_element_by_xpath("//button[@type='submit']").click()

print("Added UserID and Password and clicked on login")
log_list.append("Added UserID and Password and clicked on login")
log_list.append("------------------")
driver.implicitly_wait(10)

##############################
try:
    driver.find_element_by_id("authCode").send_keys(f"{get_mfa()}")

    driver.find_element_by_class_name("wm-ui-btn").click()
    log_list.append("Passed MFA successfully.")
    log_list.append("------------------")
    print("Passed MFA successfully.")
except NoSuchElementException:
    log_list.append("MFA wasn't requested")
    log_list.append("------------------")
    print("MFA wasn't requested")
    pass

driver.implicitly_wait(10)

try:
    driver.find_element_by_link_text("Collect points").click()
    print("Daily points collected successfully")
    log_list.append("Daily points collected successfully")
    log_list.append("------------------")

except NoSuchElementException:
    print("Daily points were already collected")
    log_list.append("Daily points were already collected")

except:
    print("!!!Something went wrong!!!")
    log_list.append("!!!Something went wrong!!!")
    send_text_message(log_list)
    driver.quit()
    sys.exit()

print("Successful script run")
log_list.append("Successful script run")
send_text_message(log_list)

driver.quit()