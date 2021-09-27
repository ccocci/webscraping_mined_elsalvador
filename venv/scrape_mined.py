from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time
import csv
import pandas as pd



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

sel_field= browser.find_element_by_xpath("//*[@id='form:b_departamento']")
#deps= [str(x) for x in range(1,15)]
deps=["12"]

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



rows_list = []

## loop over each school!

data_rows=[]


test_link="https://portal.siges.sv/pp/sede?sede=2083"
browser.get(test_link)
browser.implicitly_wait(10)

dict={}

# school info
dict["code"]=browser.find_element_by_xpath('//*[@id="form:input_codigo"]').text
dict["website"]=browser.find_element_by_xpath('//*[@id="form:j_idt31"]/div[3]/a').get_attribute("href")
dict["name"]=browser.find_element_by_xpath('//*[@id="form:input_nombre"]').text
dict["type"]=browser.find_element_by_xpath('//*[@id="form:output_tipo_sede"]').text
dict["address"]=browser.find_element_by_xpath('//*[@id="form:j_idt31"]/div[5]').text
dict["tel"]=browser.find_element_by_xpath('//*[@id="form:input_telefono"]').text
dict["shift"]=browser.find_element_by_xpath('//*[@id="form:opt_jornada"]').text
dict["email"]=browser.find_element_by_xpath('//*[@id="form:j_idt31"]/div[10]/a').text

sel_grade=Select(browser.find_element_by_xpath("//*[@id='form:b_nivel']"))
sel_grade.select_by_visible_text("Educación Básica")
search = browser.find_element_by_xpath('//*[@id="form:btnBuscar"]')
search.click()


tbl = browser.find_element_by_xpath('//*[@id="form:basicDT"]/div/table').get_attribute('outerHTML')
df  = pd.DataFrame(pd.read_html(tbl)[0])
# select rows we need
df=df[["Nombre grado","2019","2020","2021"]]
# cut the first 4 number b/c they are repetition of year
df[["2019","2020","2021"]]= df[["2019","2020","2021"]].applymap(lambda x: int(str(x)[4:]))

grades = {"Primer": "1","Segundo": "2","Tercer": "3","Quarto": "4", "Quinto": "5","Sexto": "6"}

for grade in grades:
    students=df[df["Nombre grado"]==("Nombre grado"+grade+" Grado")].loc[:,["2019","2020","2021"]]
    students=list(students.values.flatten())
    grade_number=grades.get(grade)
    var_name="students_grade"+grade_number
    dict[var_name]=students


#data_rows.append(dict)

##data = pd.DataFrame(data_rows)  --> if not working add attribute columns=['A','B','C','D','E']