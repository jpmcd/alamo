import time
import datetime
import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
# from selenium.webdriver.firefox.options import Options
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

from covid import check_uth
from covid import check_cvs

def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36")
    driver = webdriver.Chrome(options=options)
    # driver = webdriver.Firefox(options=options)
    return driver

def test_alamo(driver):
    url = "https://emrinventory.cdpehs.com/ezEMRxPHR/html/login/newPortalReg.jsp"
    driver.get(url)
    threshold = datetime.datetime(2021, 1, 17, 22, 39, 00)
    while True:
        if datetime.datetime.now() >= threshold:
            break
    textbox = driver.find_element(By.ID, "groupCode")
    textbox.clear()
    textbox.send_keys("DOMECOVID")
    textbox.send_keys(Keys.ENTER)
    time.sleep(.5)
    try:
        element = driver.find_element(By.ID, "schSlotsMsg")
        outcome = element.text == "Registration full"
    except NoSuchElementException as e:
        print(type(e), e)

def test_alamo_new(driver):
    url = "https://covid19.sanantonio.gov/Services/Vaccination-for-COVID-19"
    driver.get(url)
    text = "Due to limited quantity, vaccine registration is temporarily unavailable."
    time.sleep(3)
    element = driver.find_element(By.TAG_NAME, "body")
    outcome = text in element.text
    print(outcome)
    print(element.text)

def test_uth(driver):
    outcome = check_uth(driver)
    print(outcome)

def test_kinney(driver):
    try:
        url = "https://secure.kinneydrugs.com/pharmacy/covid-19/vaccination-scheduling/ny/"
        driver.get(url)
        time.sleep(1)
        element = driver.find_element(By.TAG_NAME, "body")
        text = "all appointments in New York are BOOKED"
        outcome = text in element.text
        print("Outcome:", outcome)
        return outcome
    except Exception as e:
        print(e)

def test_nys(driver):
    try:
        url = "https://apps3.health.ny.gov/doh2/applinks/cdmspr/2/counties?OpID=50501047"
        driver.get(url)
        time.sleep(2)
        text = "No Appointments Available"
        element = driver.find_element(By.ID, "notfound")
        outcome = text in element.text
        print(outcome)
    except Exception as e:
        print(e)

def test_cvs():
    print(check_cvs('South Boston', 'VA')())

if __name__ == "__main__":
    driver = None
    try:
        driver = get_driver()
        test_uth(driver)
        # test_cvs()
    except Exception as e:
        print(e)
        if driver:
            driver.quit()
        raise
if driver:
    driver.quit()