from selenium import webdriver
import os

options = webdriver.FirefoxOptions()
options.headless = True
options.binary_location = os.environ.get("FIREFOX_BIN")
capabilities = webdriver.DesiredCapabilities.FIREFOX
capabilities['marionette'] = True

driver = webdriver.Firefox(
                    options=options,
                    capabilities=capabilities,
                    firefox_profile=None,
                    executable_path="./geckodriver"
                    )

driver.get("https://www.google.com/")
