
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from pydub import AudioSegment
import requests, json, sys
from googleauthenticator import get_mfa
import os, sys
import time,requests

with open("secrets.json", "r") as f:
    json_data = json.load(f)

wittoken = json_data["wittoken"]
warmane_acc = json_data["warmane_acc"]
warmane_pass = json_data["warmane_pass"]
filename = 'test.mp3'
startpage = 'https://www.warmane.com/account/login'

chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=chrome_options)

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
        audioBtn.click()
        audioBtnFound = True
        audioBtnIndex = index
        break
    except Exception as e:
        pass

if audioBtnFound:
    try:
        while True:
            print("Check audio button")
            href = driver.find_element_by_id('audio-source').get_attribute('src')
            response = requests.get(href, stream=True)

            saveFile(response,filename)

            print("Converting the mp3 audiofile to wav")
            sound = AudioSegment.from_mp3("test.mp3")
            sound.export("test.wav", format='wav')

            response = audioToText("test.wav") #os.getcwd() + '/' + "test.wav")
            print("Text from the response was: " + response)

            driver.switch_to.default_content()
            iframe = driver.find_elements_by_tag_name('iframe')[audioBtnIndex]
            driver.switch_to.frame(iframe)

            print("Sending the text result back to captcha")
            try:
                inputbtn = driver.find_element_by_id('audio-response')
                inputbtn.send_keys(response)
                inputbtn.send_keys(Keys.ENTER)
                
                time.sleep(2)
                errorMsg = driver.find_elements_by_class_name('rc-audiochallenge-error-message')[0]

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
        driver.quit()
        print("Driver Closed")
        sys.exit()
else:
    print('Button not found.')
    driver.quit()
    sys.exit()

driver.switch_to.default_content()

driver.find_element_by_id("userID").send_keys(warmane_acc)
driver.find_element_by_id("userPW").send_keys(warmane_pass)
driver.find_element_by_xpath("//button[@type='submit']").click()
driver.implicitly_wait(10)

##############################
try:
    driver.find_element_by_id("authCode").send_keys(f"{get_mfa()}")

    driver.find_element_by_class_name("wm-ui-btn").click()
    print("Passed MFA successfully.")
except NoSuchElementException:
    print("MFA wasn't requested")
    pass

driver.implicitly_wait(10)

try:
    driver.find_element_by_link_text("Collect points").click()
    print("Daily points collected successfully")

except NoSuchElementException:
    print("Daily points were already collected")

except:
    print("!!!Something went wrong!!!")

print("Successful script run")

driver.quit()