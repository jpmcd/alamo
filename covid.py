from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as firefox_options
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
from config import info

parser = argparse.ArgumentParser()
parser.add_argument('--no-sms', action='store_true', help='Turn off SMS alerts')
parser.add_argument('--head', action='store_true', help='Use headed browsing with Firefox')
parser.add_argument('--wait', type=float, default=25, help='Wait time between checks')
parser.add_argument('--alamo', action='store_true')
parser.add_argument('--uth', action='store_true')
parser.add_argument('--heb', action='store_true')
parser.add_argument('--kinney', action='store_true')
parser.add_argument('--nys', action='store_true')
parser.add_argument('--fpg', action='store_true')
parser.add_argument('--book', action='store_true')
parser.add_argument('--walg', type=str)
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
site_cvs_book = "https://www.cvs.com/vaccine/intake/store/cvd-schedule?icid=coronavirus-lp-vaccine-sd-statetool"
# site_walg = "https://www.walgreens.com/findcare/vaccination/covid-19/location-screening"
site_walg = "https://www.walgreens.com/findcare/vaccination/covid-19?ban=covid_vaccine_landing_schedule"
site_fpg = "https://bookfpg.timetap.com/"
site_bmc = "https://mychartscheduling.bmc.org/MyChartscheduling/covid19#/triage"

def void(*args):
    pass

def get_driver(head=False):
    if head:
        # options = webdriver.FirefoxOptions().set_headless()
        # driver = webdriver.Firefox(firefox_options=options)
        options = firefox_options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36")
        driver = webdriver.Firefox(options=options)
        # driver = webdriver.Firefox()
    else:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36")
        driver = webdriver.Chrome(options=options)
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
    if not outcome:
        print(element.text)
        driver.find_element(By.ID, "Input_FullName").send_keys(info['name'])
        driver.find_element(By.ID, "Input_PhoneNumber").send_keys(info['phone'])
        driver.find_element(By.ID, "Input_Email").send_keys(info['email'])
        driver.find_element(By.ID, "Input_Password").send_keys(info['pass'])
        driver.find_element(By.ID, "Input_ConfirmPassword").send_keys(info['pass'])
        driver.find_element(By.CLASS_NAME, "btn btn-primary").click()
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
                print("{}: {}".format(c, data[c.upper()]))
        return outcome
    return f

def check_cvs_book(driver):
    driver.get(site_cvs_book)
    time.sleep(2)
    element = driver.find_element(By.TAG_NAME, "body")
    text = "We are adding more appointments for you."
    outcome = text in element.text
    return outcome

def check_walg(driver, zipcode):
    driver.get(site_walg)
    time.sleep(2)
    driver.find_element(By.CLASS_NAME, "btn.btn__blue").click()
    time.sleep(3)
    element = driver.find_element(By.ID, "inputLocation")
    element.clear()
    element.send_keys(zipcode)
    element.send_keys(Keys.ENTER)
    driver.find_element(By.CLASS_NAME, "btn").click()
    time.sleep(2)
    try:
        element = driver.find_element(By.CLASS_NAME, "alert.alert__red mt25")
        print(element.text)
    except Exception as e:
        print(type(e), e)

def check_fpg(driver):
    text = "All appointment times are currently reserved."
    driver.get(site_fpg)
    time.sleep(5)
    driver.find_element(By.CSS_SELECTOR, "#nextBtn > .mat-button-wrapper").click()
    time.sleep(5)
    driver.find_element(By.CSS_SELECTOR, "#nextBtn > .mat-button-wrapper").click()
    time.sleep(5)
    driver.find_element(By.ID, "screeningQuestionPassBtn").click()
    time.sleep(5)
    element = driver.find_element(By.ID, "schedulerBox")
    outcome = text in element.text
    return outcome

def check_bmc(driver):
    driver.get(site_bmc)
    # driver.find_element(By.LINK_TEXT, "Click here to continue").click()
    driver.find_element(By.CSS_SELECTOR, ".answer-label:nth-child(2)").click()
    driver.find_element(By.LINK_TEXT, "Next Question").click()
    driver.find_element(By.CSS_SELECTOR, ".answer-label:nth-child(2)").click()
    driver.find_element(By.LINK_TEXT, "Next Question").click()
    driver.find_element(By.CSS_SELECTOR, ".location-card-content > div").click()
    time.sleep(1)
    driver.switch_to.frame(0)
    try:
        date = driver.find_element(By.CSS_SELECTOR, "div:nth-child(1) > .card:nth-child(1) > .header").text
    except NoSuchElementException as e:
        return False
    loc = driver.find_element(By.CSS_SELECTOR, "div:nth-child(1) > .card:nth-child(1) .providername").text
    site = loc.split()[0]
    dt = datetime.datetime.strptime(date, "%A %B %d, %Y")
    earlier = datetime.datetime(2021, 4, 28)
    outcome = (site != "Mattapan") or (dt < earlier)
    print(outcome)
    return outcome
    # element = driver.find_element(By.ID, "main")
    # element = driver.find_element(By.CLASS_NAME, "errormessage")
    # element = driver.find_element(By.TAG_NAME, "body")
    # element = driver.find_element(By.CSS_SELECTOR, "#D6F73C26-7627-4948-95EA-2C630C25C5E9_scheduleOpenings_OpeningsData.p:nth-child(1)")
    # element = driver.find_element(By.CSS_SELECTOR, ".openingsData.openingsNoData")
    # element = driver.find_element(By.CSS_SELECTOR, "#D6F73C26-7627-4948-95EA-2C630C25C5E9_scheduleOpenings_datePickerContainer")

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
    me = contacts['me']
    numbers = [me]
    args = parser.parse_args()
    try:
        if args.no_sms:
            send_sms = void
        if args.rec:
            numbers.append(contacts[args.rec])
        if args.alamo:
            check_func = check_alamo_new
            site = site_alamo_new
            driver = get_driver(head=args.head)
        elif args.uth:
            check_func = check_uth
            site = site_uth
            driver = get_driver(head=args.head)
        elif args.kinney:
            check_func = check_kinney
            site = site_kinney
            driver = get_driver(head=args.head)
        elif args.nys:
            check_func = check_nys
            site = site_nys
            driver = get_driver(head=args.head)
        elif args.fpg:
            check_func = check_fpg
            site = site_fpg
            driver = get_driver(head=args.head)
        elif args.book:
            check_func = check_cvs_book
            site = site_cvs_book
            driver = get_driver(head=args.head)
        elif bool(args.city) or bool(args.state):
            print("Checking cities: {}, state: {}".format(args.city, args.state))
            if bool(args.city) != bool(args.state):
                parser.error("Missing city or state, please supply both")
            check_func = check_cvs(args.city, args.state)
            # site = site_cvs
            site = ' , '.join([site_cvs, args.state, ' '.join(args.city)])
        else:
            check_func = check_request
            site = site_alamo
        while True:
            outcome = check_func(driver)
            if not outcome:
                # Detected change in registration status
                print("Sending alerts, {}...".format(datetime.datetime.now()))
                message = "Possible change in vaccine registration availability. Check {}".format(site)
                for cell in numbers:
                    print(message)
                    send_sms(cell, message)
                    # if driver:
                    #     print(driver.page_source)
                break
                time.sleep(300)
            else:
                time.sleep(args.wait + uniform(0, 5))
    except KeyboardInterrupt:
        print("\rInterrupted, {}...".format(datetime.datetime.now()))
    except Exception as e:
        print(type(e), e)
        print("Error occurred, {}".format(datetime.datetime.now()))
        send_sms(me, "Error occurred.")
        if driver:
            driver.quit()
        raise
    if driver:
        print("Exiting normally...")
        driver.quit()
