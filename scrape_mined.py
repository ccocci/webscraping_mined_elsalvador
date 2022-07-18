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



browser=webdriver.Firefox()
browser.maximize_window()
#browser=webdriver.Chrome("C:/Users/jakob/chromedriver/chromedriver.exe")
id_nr=1
not_working=[]
# this function tries to click on element, if it is not clickable yet, it waits one more second
def click_elem(elem):
    #start=time.time()
    #cont_bool=True
    #is_clicked=False
    #while cont_bool and time.time()-start<5:
    global id_nr
    id_nr=id_nr+1
    try:
        WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.ID,elem.get_attribute("id"))))
        elem.click()
        #is_clicked=True
        #cont_bool=False
    except StaleElementReferenceException:
        elem=browser.find_element_by_id(elem.get_attribute("id"))
        elem.click()
    except WebDriverException or ElementNotVisibleException:
        time.sleep(1)
        elem.click()
    finally:time.sleep(0.2)
    #if is_clicked:
        #raise RuntimeError("clicking took more than 5 seconds!")

def click_arrow(arrow2):
    global id_nr
    id_nr=id_nr+1
    try:
        clickable_arrow =WebDriverWait(browser, 20).until(
            EC.element_to_be_clickable((By.ID, arrow2.get_attribute("id"))))
        print(arrow2.get_attribute("id")+"waited successfully")
        clickable_arrow.click()
        not_asserted1 = True
        start1=time.time()
        while not_asserted1 and time.time()-start1<5 :
            try:
                assert arrow1.get_attribute("class") == "ui-tree-toggler ui-icon ui-icon-triangle-1-s"
                not_asserted1 = False
            except AssertionError:
                time.sleep(0.3)
        if not_asserted1:
            raise RuntimeError("The triangle has not changed its class after clicking and waiting 5 seconds!")

    except StaleElementReferenceException or WebDriverException or ElementNotVisibleException:
        time.sleep(1)
        clickable_arrow.click()

# this function tries to find an element (default by xpath, if by_class is set to true, then by class name)
# if it finds it the function returns 1, otherwise 0
def elem_exists(parent, elem_string, by_class=False, by_tag_name=False):
    browser.implicitly_wait(0)
    try:
        if by_class:
            parent.find_element_by_class_name(elem_string)
            return True
        elif by_tag_name:
            parent.find_element_by_tag_name(elem_string)
            return True
        else:
            parent.find_element_by_xpath(elem_string)
            return True
    except NoSuchElementException:
        return False
    finally:
        browser.implicitly_wait(2)

# get school links from csv
school_links=pd. read_csv("temp/school_links.csv")
school_links=school_links.iloc[:,0].to_list()


data_rows=[]
browser.implicitly_wait(2)
count=0

for link in school_links:
    scraping_tries=0
    while scraping_tries<2:
        try:
            # link="https://portal.siges.sv/pp/sede?sede=90"
            browser.get(link)
            start_time = time.time()
            school_dict = {}


            def ignore_exception(selector, exception=NoSuchElementException):
                try:
                    return browser.find_element_by_css_selector(selector)
                except exception:
                    pass



            # school info
            school_dict["code"] = ignore_exception('#form\:input_codigo').text
            school_dict["address"] = ignore_exception('div.space:nth-child(5)').text
            regex = re.findall(",[^,]*,[^,]*\.$", school_dict["address"])[0]
            school_dict["department"] = re.findall(",[^,]*\.$", regex)[0][2:-1]
            school_dict["municipality"] = re.findall(",[^,]*,", regex)[0][2:-1]
            school_dict["website"] = ignore_exception('div.space:nth-child(3) > a:nth-child(2)').get_attribute("href")
            school_dict["name"] = ignore_exception('#form\:input_nombre').text
            school_dict["type"] = ignore_exception('#form\:output_tipo_sede').text
            school_dict["tel"] = ignore_exception('#form\:input_telefono').text
            school_dict["shift"] = ignore_exception('#form\:opt_jornada').text
            school_dict["email"] = ignore_exception('div.space:nth-child(10) > a:nth-child(2)').text
            coords = ignore_exception('.iframeMapa').get_attribute('src')
            school_dict["coords"] = re.findall('.*lat=([-0-9.]*)&lon=([-0-9.]*)', coords)[0]
            school_dict["url"] = link


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

            no_basic_edu=False
            # if Educacion Regular arrow exists click on it (without throwing exception
            if elem_exists(browser, "//span[contains(text(), 'Educación Regular')]/parent::span/parent::li"):
                parent_edu_reg = browser.find_element_by_xpath(
                    "//span[contains(text(), 'Educación Regular')]/parent::span/parent::li")
                arrow1 = parent_edu_reg.find_element_by_class_name("ui-icon-triangle-1-e")
                browser.execute_script("arguments[0].setAttribute('id','made_up" + str(id_nr) + "')", arrow1)
                click_arrow(arrow1)
                elem_stale = False
            else:
                no_basic_edu = True

            print("first arrow clicked")
            # if educacion basica arrow exists open all other arrows
            if elem_exists(browser, "//span[contains(text(), 'Educación Básica')]/parent::span/parent::li"):
                parent_edu_base = browser.find_element_by_xpath(
                    "//span[contains(text(), 'Educación Básica')]/parent::span/parent::li")
            else:
                no_basic_edu = True

            # if there is no basic education, continue to next school
            if no_basic_edu:
                data_rows.append(school_dict)
                count = count + 1
                print("School " + str(count) + " out of 5024 -> aprox. " + str(round(count / 5024 * 100, 2)) + " % done")
                scraping_tries=3
                break

            cont = True
            while cont:

                # if there is no more arrow to click on, stop
                if not elem_exists(parent_edu_base, "ui-icon-triangle-1-e", by_class=True):
                    cont = False
                    break

                try:
                    arrows = parent_edu_base.find_elements_by_class_name("ui-icon-triangle-1-e")
                    for arrow in arrows:
                        browser.execute_script("arguments[0].setAttribute('id','made_up"+str(id_nr)+"')", arrow)
                        click_arrow(arrow)

                except StaleElementReferenceException or ElementNotVisibleException:
                    time.sleep(0.2)
                    parent_edu_base = browser.find_element_by_xpath(
                        "//span[contains(text(), 'Educación Básica')]/parent::span/parent::li")

            print("menu succesfully opened")

            ## iterate through all the grades using the name of the grade (attention : case sensitive!)
            for grade_text in list(grades.keys())[3:len(grades.keys())]:

                # construct xpath to grade
                xpath="//span[contains(text(), '"+grade_text+"')]"
                # check if grade exists
                if elem_exists(browser, xpath):
                    # find grade elem and click on it
                    try:
                        grade = browser.find_element_by_xpath(xpath)
                        grade_code = grades.get(grade_text)
                        browser.execute_script("arguments[0].setAttribute('id','made_up" + str(id_nr) + "')", grade)
                        click_elem(grade)
                    except StaleElementReferenceException:
                        time.sleep(1)
                        grade = browser.find_element_by_xpath(xpath)
                        grade_code = grades.get(grade_text)
                        click_elem(grade)

                    # I don't like this, but it is needed bc otherwise sometimes
                    # it saves the values from the previous grade -> how can we improve?
                    time.sleep(0.5)
                    graph = browser.find_element_by_tag_name('svg')

                    # if element does not contain any g elements, then it is empty-> continue
                    if not elem_exists(graph, "g", by_tag_name=True):
                        continue

                    elem_stale = True
                    # doing this while statement catches staleElement exception, sleeps one second,
                    # reloads the parent element and tries again (until it works)
                    while(elem_stale):
                        try:
                            subject_elems = graph.find_elements_by_css_selector("#form\:grafico > svg > g")
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
                            elem_stale=False
                        except StaleElementReferenceException:
                            time.sleep(1)
                            graph = browser.find_element_by_tag_name('svg')

                    print("check in between")
                    subject_names = {"CIENCIA, SALUD Y MEDIO AMBIENTE": "science", "EDUCACIÓN ARTÍSTICA": "arts",
                                     "EDUCACIÓN FÍSICA": "sports", "ESTUDIOS SOCIALES": "social_science",
                                     "LENGUAJE": "language", "MATEMÁTICA": "maths", "INGLÉS": "english",
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
            print(time.time()-start_time)
            scraping_tries=3
        except:
            scraping_tries=scraping_tries+1
    if scraping_tries<3:
        not_working.append(link)


data = pd.DataFrame(data_rows)

data.to_csv(r"out/webscraping_mined.csv",index=False)















