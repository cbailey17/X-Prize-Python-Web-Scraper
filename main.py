# Webscraper for x-prize competition for carbon capture technology
import requests
import os
from dotenv import load_dotenv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import Firefox
import pandas as pd
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pymongo
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup


def requests_setup_cookies(driver: webdriver) -> requests.Session:
    """
    Set up cookies from selenium for requests module in order to make HTTP requests and request html
    Args:
        driver (webdriver): instance of our selenium webdriver
    Returns:
        requests.Session: Session instance used to make requests
    """
    session = requests.Session()
    selenium_user_agent = driver.execute_script("return navigator.userAgent")
    session.headers.update({"user-agent": selenium_user_agent})

    for cookie in driver.get_cookies():
        session.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])
    return session


def authenticate_static(url: str) -> requests.Session():
    """used to authenticate using the requests module
    Args:
        url (str): the url to authenticate for
    Returns:
        _type_: a session object
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
    """used to set up seleniums environment 
    Returns:
        webdriver: selenium webdriver instance
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
        time.sleep(1)
        driver.get("https://pop.xprize.org/Account/Login")
        driver.implicitly_wait(8)
        # driver.maximize_window()
    return driver


def login(driver: webdriver) -> webdriver:
    """function for logging in using selenium
    Args:
        driver (webdriver): webdriver instance
    Returns:
        webdriver: webdriver instance 
    """
    inputs = driver.find_elements(By.TAG_NAME, "input")
    time.sleep(5)
    inputs[0].send_keys(os.environ.get('XPRIZE_USER'))
    inputs[1].send_keys(os.environ.get('XPRIZE_PWD'))
    driver.find_element(By.CLASS_NAME, "ids-submit-btn").click()
    time.sleep(3)
    assert "XPRIZE Prize Operations Platform" in driver.title
    return driver


def navigate_teams(driver: webdriver):
    """
    Function used to navigate the desired website to get to the content needed
    Args:
        driver (webdriver): instance of our selenium webdriver
    """
    teams = []
    driver.get('https://pop.xprize.org/prizes/xprize_carbon_capture/overview')
    time.sleep(5)
    cookie_consent = driver.find_element(By.CSS_SELECTOR, 'body > div > div > a').click()
    next = driver.find_element(By.CSS_SELECTOR, '[aria-label=Next]')
    page = 0

    while next:
        page += 1
        for i in range(1, 11):
            teams += driver.find_elements(By.CSS_SELECTOR, f'team-card.team-card-wrapper:nth-child({i}) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1)')

        for team in teams:
            team.click()
            time.sleep(3)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            scrape_data(soup)

        try:
            elem_present = EC.presence_of_element_located((By.CSS_SELECTOR, '[aria-label=Next]'))
            element = WebDriverWait(driver, 20).until(elem_present)
            time.sleep(20)
            element.click()
        except TimeoutException:
            print('Took to long to find element')

    print('Done')


def scrape_data(soup: BeautifulSoup) -> None:
    team_data = []
    


def mongoConnect():
    """
    Function used to connect to our MongoDB and set up the database 
    """
    ATLAS_URI = os.environ.get('ATLAS_URI')
    client = pymongo.MongoClient(ATLAS_URI)
    db = client[os.environ.get('DB_NAME')]
    collection = db[os.environ.get('COLLECTION_NAME')]


def main():
    load_dotenv()
    mongoConnect()
    driver = selenium_setup()
    driver = login(driver)
    navigate_teams(driver)


if __name__ == '__main__':
    main()
