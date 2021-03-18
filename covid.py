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
import json
import argparse
from random import uniform

from sms import send_sms
from config import contacts
# from config import info

parser = argparse.ArgumentParser()
parser.add_argument('--alamo', action='store_true')
parser.add_argument('--uth', action='store_true')
parser.add_argument('--heb', action='store_true')
parser.add_argument('--kinney', action='store_true')
parser.add_argument('--nys', action='store_true')
parser.add_argument('--city', nargs='+')
parser.add_argument('--state')
parser.add_argument('--rec')

URL = 'https://emrinventory.cdpehs.com/ezEMRxPHR/DOMECOVID_genRegQuest.htm'
URL2 = 'https://emrinventory.cdpehs.com/ezEMRxPHR/DOMECOVID_F_genRegQuest.htm'
site_alamo = "https://emrinventory.cdpehs.com/ezEMRxPHR/html/login/newPortalReg.jsp"
site_alamo_new = "https://covid19.sanantonio.gov/Services/Vaccination-for-COVID-19"
site_kinney = "https://secure.kinneydrugs.com/pharmacy/covid-19/vaccination-scheduling/ny/"
site_nys = "https://apps3.health.ny.gov/doh2/applinks/cdmspr/2/counties?OpID=50501047"
# site_uth = "https://uthealth.qualtrics.com/jfe/form/SV_9AkzYKyGfVMP9k2"
site_uth = "https://schedule.utmedicinesa.com/identity/account/register"
site_cvs = "https://www.cvs.com/immunizations/covid-19-vaccine?icid=cvs-home-hero1-link2-coronavirus-vaccine"

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

def get_cvs_data(state='MA'):
    site_cvs_json = "https://www.cvs.com/immunizations/covid-19-vaccine.vaccine-status.json?vaccineinfo"
    cvs_dict = {'authority': 'www.cvs.com',
                'sec-ch-ua': '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
                'sec-ch-ua-mobile': '?0',
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36',
                'accept': '*/*',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
                'referer': 'https://www.cvs.com/immunizations/covid-19-vaccine',
                'accept-language': 'en-US,en;q=0.9'}
    r = requests.get(site_cvs_json, headers=cvs_dict)
    d = json.loads(r.text)
    d = d['responsePayloadData']['data'][state]
    d = {x['city']: x['status'] for x in d}
    return d

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

def check_uth(driver):
    driver.get(site_uth)
    time.sleep(3)
    element = driver.find_element(By.TAG_NAME, "body")
    text = "Sign-up is currently closed"
    outcome = text in element.text
    # if not outcome:
    #     driver.find_element(By.ID, "Input_FullName").send_keys(info['name'])
    #     driver.find_element(By.ID, "Input_PhoneNumber").send_keys(info['phone'])
    #     driver.find_element(By.ID, "Input_Email").send_keys(info['email'])
    #     driver.find_element(By.ID, "Input_Password").send_keys(info['pass'])
    #     driver.find_element(By.ID, "Input_ConfirmPassword").send_keys(info['pass'])
    return outcome

def check_uth_old(driver):
    driver.get(site_uth)
    text = "At this time, based off the amount of vaccine shipped to UTHealth, our COVID-19 registry is full."
    time.sleep(3)
    element = driver.find_element(By.TAG_NAME, "body")
    outcome = text in element.text
    return outcome

def check_cvs(city, state):
    def f(*args):
        data = get_cvs_data(state.upper())
        outcome = True
        cities = city
        if type(city) != list:
            cities = [city]
        for c in cities:
            if data[c.upper()] != 'Fully Booked':
                outcome = False
        return outcome
    return f

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

if __name__ == "__main__":
    driver = None
    message = None
    args = parser.parse_args()
    me = contacts['me']
    numbers = [me]
    if args.rec:
        numbers.append(contacts[args.rec])
    if args.alamo:
        check_func = check_alamo_new
        site = site_alamo_new
        driver = get_driver()
    elif args.uth:
        check_func = check_uth
        site = site_uth
        driver = get_driver()
    elif args.kinney:
        check_func = check_kinney
        site = site_kinney
        driver = get_driver()
    elif args.nys:
        check_func = check_nys
        site = site_nys
        driver = get_driver()
    elif bool(args.city) or bool(args.state):
        if bool(args.city) != bool(args.state):
            parser.error("Missing city or state, please supply both")
        check_func = check_cvs(args.city, args.state)
        # site = site_cvs
        site = ', '.join([site_cvs, ' '.join(args.city), args.state])
    else:
        check_func = check_request
        site = site_alamo
    try:
        while True:
            try:
                outcome = check_func(driver)
                if not outcome:
                    # Detected change in registration status
                    print("Sending alerts, {}...".format(datetime.datetime.now()))
                    message = "Possible change in vaccine registration availability. Check {}".format(site)
                    for cell in numbers:
                        print(message)
                        send_sms(cell, message)
                        if driver:
                            print(driver.page_source)
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
        # send_sms(me, "Process interrupted.")
    except Exception as e:
        print(type(e), e)
        print("Error occurred, {}".format(datetime.datetime.now()))
        send_sms(me, "Error occurred.")
        if driver:
            driver.quit()
        raise
    if driver:
        driver.quit()
