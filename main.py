# Webscraper for x-prize competition for carbon capture technology
import requests
import settings
from workers import SeleniumWorkers
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
from bs4 import Comment
import re


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

    # check for headless state
    if settings.HEADLESS:
        options = Options()
        options.add_argument('--headless')
    else:
        options = None

    if firefox:
        #profile_path = r'/Users/cameronbailey/Library/Application Support/Firefox/Profiles/f08wt13m.default-1668902584215' # mac
        profile_path = r'' # ubuntu
        options.set_preference('profile', profile_path)
        service = Service(r'/Users/cameronbailey/PycharmProjects/WebScraper/selenium_drivers_mac/geckodriver')
        driver = Firefox(service=service, options=options)
    else:
        driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver', options=options) #make sure path is correct
        time.sleep(1)
    return driver


def login(driver: webdriver) -> webdriver:
    """function for logging in using selenium
    Args:
        driver (webdriver): webdriver instance
    Returns:
        webdriver: webdriver instance 
    """
    driver.get(os.environ.get('LOGIN'))
    driver.implicitly_wait(8)
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
    driver.get(os.environ.get('OVERVIEW'))
    time.sleep(5)
    cookie_consent = driver.find_element(By.CSS_SELECTOR, 'body > div > div > a').click()
    next = driver.find_element(By.CSS_SELECTOR, '[aria-label=Next]')

    while next:
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


def scrape_data(soup: BeautifulSoup) -> dict: 
    team_data = {
            "team-name": soup.select_one('.team-name-header').text,
            "about": soup.select_one('.team-about').text,
            "location": soup.select_one('.city-country').text,
            "skills-needed": [],
            "socials": [],
            "members": []
        }
    team_member_names = soup.select('.member-name')
    team_member_roles = soup.select('.member-card-role')
    if team_member_names:
        i = 0
        for name in team_member_names:
            name_split = re.findall('[A-Z][^A-Z]*', name.text)
            team_data["members"].append({"first-name": name_split[0], "last_name": name_split[1], "role": team_member_roles[i].text})
            i += 1
    
    skills = soup.select('.skill')
    if skills:
        for skill in skills:
            team_data["skills-needed"].append(skill.text)

    # socials = soup.findAll('svg', {'class' : lambda L: L.startswith('icon--')})
    socials = soup.select_one('.team-social')
    for social in socials.contents:
        if type(social) is not Comment:
            link = social.get('href')
            team_data["socials"].append({social.children[0].get('class'): link})


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
    # driver = selenium_setup()
    workers = SeleniumWorkers(selenium_setup)
    workers.drivers
    driver = login(driver)
    navigate_teams(driver)


if __name__ == '__main__':
    main()
