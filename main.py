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
    load_dotenv()
    payload = {
            'Email': os.environ.get('XPRIZE_USER'),
            'Password': os.environ.get('XPRIZE_PWD'),
    }
    with requests.Session() as sesh:
        response = sesh.post(url, json=payload)

        if response.status_code == 200:
            return sesh
        return None


def main():
    profile_path = r'/Users/cameronbailey/Library/Application Support/Firefox/Profiles/f08wt13m.default-1668902584215'
    options = Options()
    options.set_preference('profile', profile_path)
    service = Service(r'/Users/cameronbailey/PycharmProjects/WebScraper/selenium_drivers/geckodriver')
    driver = Firefox(service=service, options=options)

    # driver = webdriver.Firefox('/Users/cameronbailey/PycharmProjects/WebScraper/selenium_drivers/geckodriver')
    driver.get("https://pop.xprize.org/Account/Login")
    driver.implicitly_wait(6)
    driver.maximize_window()
    inputs = driver.find_elements(By.TAG_NAME, "input")
    inputs[0].send_keys('a.cameronbailey@gmail.com')
    inputs[1].send_keys('ACBacb011795!?')
    driver.find_element(By.CLASS_NAME, "ids-submit-btn").click()
    time.sleep(5)
    driver.get('https://pop.xprize.org/prizes/xprize_carbon_capture/overview')
    time.sleep(3)
    foo = driver.find_elements(By.TAG_NAME, "team-card")
    print()


# //*[@id="registered-teams"]/div/div/div/team-card[2]


if __name__ == '__main__':
    main()
