from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotVisibleException
from selenium.common.exceptions import StaleElementReferenceException
import time
import csv
import pandas as pd
import numpy as np
import re



browser=webdriver.Chrome()

browser.get("https://portal.siges.sv/pp/sedes")


school_links=[]

# get all the links to the listed schools
def get_school_links():
    # sleep for two seconds otherwise it throws error
    time.sleep(0.7)
    container = browser.find_element_by_xpath("//*[@id='form:basicDT_list']")
    elems = container.find_elements_by_tag_name("a")
    links = [elem.get_attribute('href') for elem in elems]
    return links

# this function tries to click on element, if it is not clickable yet, it waits one more second
def click_elem(elem):
    try:
        WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"."+elem.get_attribute("class").replace(" ","."))))
        elem.click()
    except StaleElementReferenceException:
        elem=browser.find_element_by_css_selector("."+elem.get_attribute("class").replace(" ","."))
        elem.click()
    except WebDriverException or ElementNotVisibleException:
        time.sleep(1)
        try:
            elem.click()
        except WebDriverException or ElementNotVisibleException:
            time.sleep(0.8)
            elem.click()
        finally:time.sleep(0.2)



# get pages
number_of_pages = 51

# iterate through pages and append links
for page in range(1, number_of_pages + 1):
    try:
        pager = browser.find_element_by_xpath("//*[@id='form:basicDT_paginator_bottom']/span[2]")
        page_string = str(page)
        page_elem = pager.find_element_by_xpath("//a[contains(text(), '" + page_string + "')]")
        click_elem(page_elem)
    except StaleElementReferenceException:
        time.sleep(1)
        pager = browser.find_element_by_xpath("//*[@id='form:basicDT_paginator_bottom']/span[2]")
        page_string = str(page)
        page_elem = pager.find_element_by_xpath("//a[contains(text(), '" + page_string + "')]")
        click_elem(page_elem)
    page_links = get_school_links()
    school_links.extend(page_links)

np.savetxt("temp/school_links.csv", school_links, delimiter=",", fmt='%s')