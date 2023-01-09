# Webscraper for x-prize competition for carbon capture technology
import requests
import os
import json
from dotenv import load_dotenv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys
import pandas as pd
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options


def authenticate_static(url: str) -> requests.Session():
    """
    Authenticate for static websites needing to be scraped with static html content
    :param url:
    :return:
    """
    payload = {
            'Email': os.environ.get('XPRIZE_USER'),
            'Password': os.environ.get('XPRIZE_PWD'),
    }
    with requests.Session() as sesh:
        response = sesh.post(url, json=payload)

        if response.status_code == 200:
            return sesh
        return None


def selenium_setup() -> webdriver:
    """
    Function for setting up seleniums environment
    :return:
    """
    firefox = os.environ.get('FIREFOX')

    if firefox is True:
        #profile_path = r'/Users/cameronbailey/Library/Application Support/Firefox/Profiles/f08wt13m.default-1668902584215' # mac
        profile_path = r'' # ubuntu
        options = Options()
        options.set_preference('profile', profile_path)
        service = Service(r'/Users/cameronbailey/PycharmProjects/WebScraper/selenium_drivers_mac/geckodriver')
        driver = Firefox(service=service, options=options)
    else:
        driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver') #make sure path is correct
        driver.get("https://pop.xprize.org/Account/Login")
        driver.implicitly_wait(8)
        driver.maximize_window()
    return driver


def login(driver: webdriver) -> webdriver:
    """
    Function for logging into x-prize
    :param driver:
    :return webdriver:
    """
    inputs = driver.find_elements(By.TAG_NAME, "input")
    time.sleep(1)
    inputs[0].send_keys(os.environ.get('XPRIZE_USER'))
    inputs[1].send_keys(os.environ.get('XPRIZE_PWD'))
    driver.find_element(By.CLASS_NAME, "ids-submit-btn").click()
    time.sleep(1)
    return driver


def navigate_teams(driver: webdriver) -> webdriver:
    driver.get('https://pop.xprize.org/prizes/xprize_carbon_capture/overview')
    time.sleep(1)
    number_of_pages = int(driver.find_elements("//a[contains(text(),'Next')]/preceding-sibling::a[1]").text)
    teams = driver.find_elements(By.TAG_NAME, "team-card")

def main():
    load_dotenv()
    driver = selenium_setup()
    driver = login(driver)
    navigate_teams(driver)



if __name__ == '__main__':
    main()
