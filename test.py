import time
import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
# from selenium.webdriver.firefox.options import Options
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

from covid import check_uth

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36")
driver = webdriver.Chrome(options=options)
# driver = webdriver.Firefox(options=options)

def test_alamo(driver):
    driver.get("https://emrinventory.cdpehs.com/ezEMRxPHR/html/login/newPortalReg.jsp")
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
    site_alamo_new = "https://covid19.sanantonio.gov/Services/Vaccination-for-COVID-19"
    driver.get(site_alamo_new)
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
        driver.get("https://secure.kinneydrugs.com/pharmacy/covid-19/vaccination-scheduling/ny/")
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
        driver.get("https://apps3.health.ny.gov/doh2/applinks/cdmspr/2/counties?OpID=50501047")
        time.sleep(2)
        text = "No Appointments Available"
        element = driver.find_element(By.ID, "notfound")
        outcome = text in element.text
        print(outcome)
    except Exception as e:
        print(e)

if __name__ == "__main__":
    try:
        test_uth(driver)
    except Exception as e:
        print(e)
        driver.quit()
        raise
if driver:
    driver.quit()
