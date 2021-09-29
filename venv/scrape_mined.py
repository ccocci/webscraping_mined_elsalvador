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

#sel_grade=Select(browser.find_element_by_xpath("//*[@id='form:b_nivel']"))
#sel_grade.select_by_visible_text("Educación Básica")
#search = browser.find_element_by_xpath('//*[@id="form:btnBuscar"]')
#search.click()


tbl = browser.find_element_by_xpath('//*[@id="form:basicDT"]/div/table').get_attribute('outerHTML')
df  = pd.DataFrame(pd.read_html(tbl)[0])
# select rows we need
df=df[["Nombre grado","2019","2020","2021"]]
# cut the first 4 number b/c they are repetition of year
df[["2019","2020","2021"]]= df[["2019","2020","2021"]].applymap(lambda x: int(str(x)[4:]))
## cut "nombre grado"
df[["Nombre grado"]]=df[["Nombre grado"]].applymap(lambda x: x[12:])
if(df.shape[0]>12):
    df=df[:12]

#grades = {"Primer": "1","Segundo": "2","Tercer": "3","Cuarto": "4", "Quinto": "5","Sexto": "6"}
grades = {"Parvularia 4":"pre_1","Parvularia 5":"pre_2","Parvularia 6":"pre_3", "Primer Grado": "1","Segundo Grado": "2","Tercer Grado": "3","Cuarto Grado": "4", "Quinto Grado": "5","Sexto Grado": "6", "Séptimo Grado":"7","Octavo Grado":"8","Noveno Grado":"9"}

for i in range(df.shape[0]):
    students =df.loc[i,["2019","2020","2021"]]
    students = list(students.values.flatten())
    grade=df.loc[i,"Nombre grado"]
    grade_number = grades.get(grade)
    var_name = "students_grade" + grade_number
    dict[var_name] = students


cont=True

while cont:
    time.sleep(1)
    arrow=browser.find_element_by_xpath('//*[@id="form:j_idt132"]/ul')
    arrows=arrow.find_elements_by_class_name("ui-icon-triangle-1-e")
    ## this takes a long time!
    if len(arrows)<=0:
        cont= False
        break
    [arrow.click() for arrow in arrows]


class_codes=["0_0_0_0_0_0","0_0_0_0_0_1","0_0_0_0_0_2","0_1_0_0_0_0","0_1_0_0_0_1","0_1_0_0_0_2"
    , "0_1_1_0_0_0", "0_1_1_0_0_1", "0_1_1_0_0_2", "0_1_2_0_0_0", "0_1_2_0_0_1", "0_1_2_0_0_2"]

part1='//*[@id="form:j_idt132:'
part2= '"]/span/span[3]'



## iterate through all the grades
for i in range(len(class_codes)):
    # construct xpath to grade
    xpath=part1+class_codes[i]+part2
    #check if grade exists
    if len(browser.find_elements_by_xpath(xpath))>0 :
        # find grade elem and click on it
        grade= browser.find_element_by_xpath(xpath)
        grade_text=grade.text
        grade_code=grades.get(grade_text)
        time.sleep(0.5)
        grade.click()
        time.sleep(0.5)

        graph=browser.find_element_by_tag_name('svg')
        if graph.get_attribute("height")== None:
            continue
        subject_elems=graph.find_elements_by_css_selector("#form\:grafico > svg > g")
        # check if svg has height (if not, it's empty) (this is the quickest way)

        # remove last 4 elements since they have nothing to do with the subjects
        subject_elems=subject_elems[:-4 or None]
        ## keep only every other element, starting from the firs
        subject_elems=subject_elems[::2 or None]

        # get nested list of subjects (number and subject)
        subject_list=[sub.find_elements_by_tag_name("text") for sub in subject_elems]
        for i in range(len(subject_list)):
            # each subject element has to text elements
            for j in range(2):
                subject_list[i][j]=subject_list[i][j].text

        subject_names = {"CIENCIA, SALUD Y MEDIO AMBIENTE": "science", "EDUCACIÓN ARTÍSTICA": "arts", "EDUCACIÓN FÍSICA": "sports", "ESTUDIOS SOCIALES": "social_science", "LENGUAJE": "language", "MATEMÁTICA": "maths","INGLÉS": "enlgish", "LENGUAJE Y LITERATURA": "language_and_literature"}

        data=pd.DataFrame([[el[0] for el in subject_list]],columns=[el[1] for el in subject_list])
        data=data.rename(columns=subject_names)

        for col in data.columns.values:
            # construct var name
            var_name= col+"_"+grade_code
            # save the value of the first (only) row per column
            dict[var_name]=data[col][0]




#data_rows.append(dict)

##data = pd.DataFrame(data_rows)  --> if not working add attribute columns=['A','B','C','D','E']



