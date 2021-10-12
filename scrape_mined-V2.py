



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
#browser=webdriver.Chrome("C:/Users/jakob/chromedriver/chromedriver.exe")

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
number_of_pages = 1 #51

# iterate through pages and append links
for page in range(1, number_of_pages + 1):
    pager = browser.find_element_by_xpath("//*[@id='form:basicDT_paginator_bottom']/span[2]")
    # pages = pager.find_elements_by_tag_name("a")
    page_string = str(page)
    page_elem = pager.find_element_by_xpath("//a[contains(text(), '" + page_string + "')]")
    # pages[page].click()
    try:
        click_elem(page_elem)
    except StaleElementReferenceException:
        page_elem = pager.find_element_by_xpath("//a[contains(text(), '" + page_string + "')]")
        click_elem(page_elem)
    page_links = get_school_links()
    school_links.extend(page_links)



data_rows=[]
browser.implicitly_wait(2)
count=0
for link in school_links:
    #test_link="https://portal.siges.sv/pp/sede?sede=396"
    browser.get(link)
    start_time = time.time()
    school_dict = {}

    # school info
    school_dict["code"] = browser.find_element_by_xpath('//*[@id="form:input_codigo"]').text
    school_dict["address"] = browser.find_element_by_xpath('//*[@id="form:j_idt31"]/div[5]').text
    regex = re.findall(",[^,]*,[^,]*\.$", school_dict["address"])[0]
    school_dict["department"] = re.findall(",[^,]*\.$", regex)[0][2:-1]
    school_dict["municipality"] = re.findall(",[^,]*,", regex)[0][2:-1]
    school_dict["website"] = browser.find_element_by_xpath('//*[@id="form:j_idt31"]/div[3]/a').get_attribute("href")
    school_dict["name"] = browser.find_element_by_xpath('//*[@id="form:input_nombre"]').text
    school_dict["type"] = browser.find_element_by_xpath('//*[@id="form:output_tipo_sede"]').text
    school_dict["tel"] = browser.find_element_by_xpath('//*[@id="form:input_telefono"]').text
    school_dict["shift"] = browser.find_element_by_xpath('//*[@id="form:opt_jornada"]').text
    school_dict["email"] = browser.find_element_by_xpath('//*[@id="form:j_idt31"]/div[10]/a').text
    coords = browser.find_element_by_xpath('/html/body/div[2]/div[1]/div[2]/div/form/div[1]/div[2]/div[3]/div/iframe').get_attribute('src')
    school_dict["coords"] = re.findall('.*lat=([-0-9.]*)&lon=([-0-9.]*)', coords)[0]
    school_dict["url"] = link


    # sel_grade=Select(browser.find_element_by_xpath("//*[@id='form:b_nivel']"))
    # sel_grade.select_by_visible_text("Educación Básica")
    # search = browser.find_element_by_xpath('//*[@id="form:btnBuscar"]')
    # search.click()

    tbl = browser.find_element_by_xpath('//*[@id="form:basicDT"]/div/table').get_attribute('outerHTML')
    df = pd.DataFrame(pd.read_html(tbl)[0])
    # select rows we need
    df[["Nivel educativo"]] = df[["Nivel educativo"]].applymap(lambda x: x[15:])
    df[["Mod. Aten."]] = df[["Mod. Aten."]].applymap(lambda x: x[10:])
    # select basic education or preschool
    df=df.loc[df["Nivel educativo"].isin(["Educación Básica","Educación Parvularia"])]
    df=df[df["Mod. Aten."]=="Regular"]
    df = df[["Nombre grado", "2019", "2020", "2021"]]
    # cut the first 4 number b/c they are repetition of year
    df[["2019", "2020", "2021"]] = df[["2019", "2020", "2021"]].applymap(lambda x: int(str(x)[4:]))
    ## cut "nombre grado"
    df[["Nombre grado"]] = df[["Nombre grado"]].applymap(lambda x: x[12:])
    if (df.shape[0] > 12):
        df = df[:12]

    # grades = {"Primer": "1","Segundo": "2","Tercer": "3","Cuarto": "4", "Quinto": "5","Sexto": "6"}
    grades = {"Parvularia 4": "pre_1", "Parvularia 5": "pre_2", "Parvularia 6": "pre_3", "Primer Grado": "1",
              "Segundo Grado": "2", "Tercer Grado": "3", "Cuarto Grado": "4", "Quinto Grado": "5", "Sexto Grado": "6",
              "Séptimo Grado": "7", "Octavo Grado": "8", "Noveno Grado": "9"}

    for i in range(df.shape[0]):
        df=df.set_index(pd.Index(range(df.shape[0])))
        students = df.loc[i, ["2019", "2020", "2021"]]
        students = list(students.values.flatten())
        grade = df.loc[i, "Nombre grado"]
        grade_number = grades.get(grade)
        var_name = "students_grade_" + grade_number
        school_dict[var_name] = students

    print("school data successful")

    # this function tries to find an element (default by xpath, if by_class is set to true, then by class name)
    # if it finds it the function returns 1, otherwise 0
    def elem_exists(parent, elem_string, by_class=False):
        browser.implicitly_wait(0)
        try:
            if by_class:
                parent.find_element_by_class_name(elem_string)
                return True
            else:
                parent.find_element_by_xpath(elem_string)
                return True
        except NoSuchElementException: # CHANGED!!!!
            return False
        finally:
            browser.implicitly_wait(2)


    parent_edu_reg_li = browser.find_element_by_xpath("//span[contains(text(), 'Educación Regular')]/parent::span/parent::li").get_attribute("id")

    cont = True

    while cont:
        parent_edu_reg = browser.find_element_by_xpath("//span[contains(text(), 'Educación Regular')]/parent::span/parent::li")
        #arrow = browser.find_element_by_css_selector('#form\:j_idt132\:3')
        if elem_exists(parent_edu_reg, "ui-icon-triangle-1-e", by_class=True) == 0:
            cont = False
            break
        try:
            arrows = parent_edu_reg.find_elements_by_class_name("ui-icon-triangle-1-e")
            [click_elem(arrow) for arrow in arrows]
        except StaleElementReferenceException or ElementNotVisibleException:
            time.sleep(0.4)
            parent_edu_reg = browser.find_element_by_xpath("//span[contains(text(), 'Educación Regular')]/parent::span/parent::li")
            arrows = parent_edu_reg.find_elements_by_class_name("ui-icon-triangle-1-e")
            [click_elem(arrow) for arrow in arrows]
    print("menu succesfully opened")

    class_codes = ["_0_0_0_0_0", "_0_0_0_0_1", "_0_0_0_0_2", "_1_0_0_0_0", "_1_0_0_0_1", "_1_0_0_0_2"
        , "_1_1_0_0_0", "_1_1_0_0_1", "_1_1_0_0_2", "_1_2_0_0_0", "_1_2_0_0_1", "_1_2_0_0_2"]

    part1 = '//*[@id="' + parent_edu_reg_li # CHANGED HERE
    part2 = '"]/span/span[3]'

    ## iterate through all the grades
    for i in range(len(class_codes)):

        # construct xpath to grade
        xpath = part1 + class_codes[i] + part2
        # check if grade exists
        if elem_exists(browser, xpath):
            # find grade elem and click on it
            grade = browser.find_element_by_xpath(xpath)
            grade_text = grade.text
            grade_code = grades.get(grade_text)
            click_elem(grade)
            print("clicked on grade")
            browser.implicitly_wait(2) #CHANGED HERE
            graph = browser.find_element_by_tag_name('svg')
            # if element does not contain any g elements, then it is empty-> continue
            if elem_exists(graph, "bar", by_class=True) == False: # CHANGED HERE
                continue

            subject_elems = graph.find_elements_by_css_selector("#form\:grafico > svg > g")

            # check if svg has height (if not, it's empty) (this is the quickest way)

            # remove last 4 elements since they have nothing to do with the subjects
            subject_elems = subject_elems[:-4 or None]
            ## keep only every other element, starting from the first
            subject_elems = subject_elems[::2 or None]

            # get nested list of subjects (number and subject)
            subject_list = [sub.find_elements_by_tag_name("text") for sub in subject_elems]
            for i in range(len(subject_list)):
                # each subject element has to text elements
                for j in range(2):
                    subject_list[i][j] = subject_list[i][j].text

            subject_names = {"CIENCIA, SALUD Y MEDIO AMBIENTE": "science", "EDUCACIÓN ARTÍSTICA": "arts",
                             "EDUCACIÓN FÍSICA": "sports", "ESTUDIOS SOCIALES": "social_science",
                             "LENGUAJE": "language", "MATEMÁTICA": "maths", "INGLÉS": "enlgish",
                             "LENGUAJE Y LITERATURA": "language_and_literature"}

            data = pd.DataFrame([[el[0] for el in subject_list]], columns=[el[1] for el in subject_list])
            data = data.rename(columns=subject_names)
            print("test scores added")
            for col in data.columns.values:
                # construct var name
                var_name = col + "_" + grade_code
                # if mean is 0, that means test was not taken-> set to na
                if data[col][0] == "0":
                    data[col][0] = np.nan
                # save the value of the first (only) row per column
                school_dict[var_name] = data[col][0]

    data_rows.append(school_dict)
    count=count+1
    print("School "+str(count)+" out of 5024 -> aprox. "+str(round(count/5024*100,2))+" % done")

data = pd.DataFrame(data_rows)

data.to_csv(r"H:\webscraping_mined_elsalvador\webscraping_mined.csv",index=False)
















