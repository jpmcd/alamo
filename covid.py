from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
# from selenium.webdriver.firefox.options import Options
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import time
import datetime
import sys
import requests
import argparse
from random import uniform

from sms import send_sms
from config import numbers

parser = argparse.ArgumentParser()
parser.add_argument('--alamo', action='store_true')
parser.add_argument('--heb', action='store_true')
parser.add_argument('--kinney', action='store_true')
parser.add_argument('--nys', action='store_true')

URL = 'https://emrinventory.cdpehs.com/ezEMRxPHR/DOMECOVID_genRegQuest.htm'
URL2 = 'https://emrinventory.cdpehs.com/ezEMRxPHR/DOMECOVID_F_genRegQuest.htm'
site_alamo = "https://emrinventory.cdpehs.com/ezEMRxPHR/html/login/newPortalReg.jsp"
site_alamo_new = "https://covid19.sanantonio.gov/Services/Vaccination-for-COVID-19"
site_kinney = "https://secure.kinneydrugs.com/pharmacy/covid-19/vaccination-scheduling/ny/"
site_nys = "https://apps3.health.ny.gov/doh2/applinks/cdmspr/2/counties?OpID=50501047"


def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36")
    driver = webdriver.Chrome(options=options)
    # driver = webdriver.Firefox(firefox_options=options)
    # options = webdriver.FirefoxOptions().set_headless()
    # driver = webdriver.Firefox(firefox_options=options)
    # driver.get("http://www.python.org")
    # print("The title is {}!".format(driver.title))
    return driver

def check_alamo(driver):
    driver.get(site_alamo)
    textbox = driver.find_element(By.ID, "groupCode")
    textbox.clear()
    textbox.send_keys("DOMECOVID")
    textbox.send_keys(Keys.ENTER)
    time.sleep(1)
    try:
        element = driver.find_element(By.ID, "schSlotsMsg")
        outcome = element.text == "Registration full"
    except NoSuchElementException as e:
        print(type(e), e)
        outcome = False
    return outcome

def check_alamo_new(driver):
    driver.get(site_alamo_new)
    text = "Due to limited quantity, vaccine registration is temporarily unavailable."
    time.sleep(3)
    element = driver.find_element(By.TAG_NAME, "body")
    outcome = text in element.text
    return outcome

def check_request(*args):
    response = requests.get(URL)
    if response.status_code == 404:
        return True
    return False

def check_kinney(driver):
    driver.get(site_kinney)
    time.sleep(1)
    element = driver.find_element(By.TAG_NAME, "body")
    text = "all appointments in New York are BOOKED"
    outcome = text in element.text
    return outcome

def check_nys(driver):
    driver.get(site_nys)
    time.sleep(5)
    try:
        element = driver.find_element(By.ID, "notfound")
        outcome = "No Appointments Available" in element.text
    except NoSuchElementException as e:
        print(type(e), e)
        outcome = False
    return outcome

def check_heb(driver):
    page = "https://vaccine.heb.com/"

args = parser.parse_args()
if args.alamo:
    check_func = check_alamo_new
    site = site_alamo_new
    driver = get_driver()
elif args.kinney:
    check_func = check_kinney
    site = site_kinney
    driver = get_driver()
elif args.nys:
    check_func = check_nys
    site = site_nys
    driver = get_driver()
else:
    check_func = check_request
    site = site_alamo
    driver = None
try:
    while True:
        try:
            outcome = check_func(driver)
            if not outcome:
                # Detected change in registration status
                print("Sending alerts, {}...".format(datetime.datetime.now()))
                message = "Possible change in vaccine registration availability. Check {}".format(site)
                for cell in [numbers['me']]:
                    send_sms(cell, message)
                break
                time.sleep(300)
            else:
                time.sleep(50 + uniform(0, 5))
        except requests.exceptions.RequestException as e:
            print(type(e), e)
            print("Pausing... Error occurred, {}".format(datetime.datetime.now()))
            time.sleep(120)
except KeyboardInterrupt:
    print("\rInterrupted, {}...".format(datetime.datetime.now()))
    # send_sms(numbers['me'], "Process interrupted.")
except Exception as e:
    print(type(e), e)
    print("Error occurred, {}".format(datetime.datetime.now()))
    send_sms(numbers['me'], "Error occurred.")
    if driver:
        driver.quit()
    raise
if driver:
    driver.quit()
