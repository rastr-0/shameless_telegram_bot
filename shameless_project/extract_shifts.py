# this files stands for web-scraping shifts
# extract_shifts returns a two-dimensional list

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from datetime import datetime as dt
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

# load password from .env file
load_dotenv('.env')
shameless_user = os.getenv('SHAMELESS_USER')
shameless_password = os.getenv('SHAMELESS_PASSWORD')

def extract_shifts():
    # initial settings for selenium
    driver_location = '/usr/local/bin/chromedriver'
    binary_location = '/usr/bin/google-chrome'

    #options = webdriver.ChromeOptions()
    options = Options()
    options.binary_location = binary_location
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--headless')

    service = Service(driver_location)
    driver = webdriver.Chrome(service=service, options=options)
    driver.get('https://shameless.sinch.cz/')

    # input e-mail and password
    driver.find_element(By.ID, 'UserEmail').clear()
    driver.find_element(By.ID, 'UserPassword').clear()
    driver.find_element(By.ID, 'UserEmail').send_keys(shameless_user)
    driver.find_element(By.ID, 'UserPassword').send_keys(shameless_password)
    # click login button
    driver.find_element(By.CLASS_NAME, 'theme-main-button.big-btn.full-btn').click()
    # getting main page
    driver.get('https://shameless.sinch.cz/react/dashboard/incoming')
    # going to page with shifts and getting html code
    driver.get('https://shameless.sinch.cz/react/position?ignoreRating=true&ignoreCapacity=false')
    time.sleep(10)
    html_shifts = driver.page_source
    driver.quit()

    # get all tr tags from tbody part
    soup = BeautifulSoup(html_shifts, 'html.parser')
    tbody = soup.find('tbody')
    free_shifts = tbody.find_all('tr')
    # complete shift_list with right tr tags
    shift_list = []
    for free_shift in free_shifts:
        shift = free_shift.get_text('|').split('|')
        # add only right tr tags to shift_list
        if len(shift) == 6:
            # convert date to SQL format
            date_str = shift[1]
            date_str = re.sub(r"\s", "", date_str)
            date_obj = dt.strptime(date_str, '%d.%m.%Y')
            formatted_date = date_obj.strftime('%Y-%m-%d')
            shift[1] = formatted_date
            # add only shifts without full capacity
            shift_capacity = shift[5]
            if shift_capacity[0] != shift_capacity[2]:
                shift_list.append(shift)
            else:
                pass

    print(len(shift_list))
    return shift_list
