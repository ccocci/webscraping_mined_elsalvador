import numpy as np
import pandas as pd
import ast


out_path = r"H:\sv_scraping_mined\webscraping_mined_elsalvador\out"

df = pd.read_csv(out_path + r"\webscraping_mined.csv")


# Keep only schools in oriental zone
print(df["department"].value_counts())
quest_depts = ["SAN MIGUEL", "LA UNIÓN", "USULUTAN"] #, "MORAZAN"
df = df[df["department"].isin(quest_depts)].reset_index()

# Keep only relevant variables
print(df.columns)
quest_vars = ["code", "name", "department", "municipality", "address", "tel", "email", "coords", "url",
              "students_grade_3", "students_grade_4", "students_grade_5",
               "maths_3", "maths_4", "maths_5"]

df = df[quest_vars]

# Extract 2021 student data
for var in ["students_grade_3", "students_grade_4", "students_grade_5"]:
    df[var] = df[var].apply(lambda x: ast.literal_eval(x)[2] if type(x) == str else None)


# Drop schools with less than 10 students in grades 3 and 4
df["size_ok"] = df["students_grade_3"] + df["students_grade_4"] > 10
df.loc[np.isnan(df["students_grade_3"] + df["students_grade_4"]), "size_ok"] = np.nan
print("School size ok:\n", df["size_ok"].value_counts(dropna=False), sep="")

df = df[df["size_ok"]==True]
df.drop("size_ok", axis=1, inplace=True)

# Translate to Spanish

trans_dict = {'code': 'codigo',
              'name': 'nombre',
              'department': 'departamento',
              'municipality': 'municipio',
              'address': 'direccion',
              'students_grade_3': 'estudiantes_grado_3',
              'students_grade_4': 'estudiantes_grado_4',
              'students_grade_5': 'estudiantes_grado_5',
       'students_grade_5', 'maths_3', 'maths_4', 'maths_5'}

df.columns
