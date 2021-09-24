from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time
import csv



# san_miguel="12"
deps=["12"]

browser=webdriver.Chrome()

browser.get("https://portal.siges.sv/pp/sedes")

browser.implicitly_wait(10)

school_links=[]

# get all the links to the listed schools
def get_school_links():
    # sleep for two seconds otherwise it throws error
    time.sleep(2)
    container = browser.find_element_by_xpath("//*[@id='form:basicDT_list']")
    browser.implicitly_wait(10)
    elems = container.find_elements_by_tag_name("a")
    browser.implicitly_wait(10)
    links = [elem.get_attribute('href') for elem in elems]
    return links

# go through all departments
for dep in deps:

    #select and choose department
    sel = Select(browser.find_element_by_xpath("//*[@id='form:b_departamento']"))
    sel.select_by_value(dep)
    search = browser.find_element_by_xpath("//*[@id='form:btnBuscar']")
    search.click()

    # get first page
    links = []
    links.extend(get_school_links())

    # get pages
    pager = browser.find_element_by_xpath("//*[@id='form:basicDT_paginator_bottom']/span[2]")
    pages = pager.find_elements_by_tag_name("a")

    # iterate through pages and append links
    for page in range(1, len(pages)):
        pager = browser.find_element_by_xpath("//*[@id='form:basicDT_paginator_bottom']/span[2]")
        pages = pager.find_elements_by_tag_name("a")
        pages[page].click()
        page_links = get_school_links()
        links.extend(page_links)

    school_links.extend(links)
