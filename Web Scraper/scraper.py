import requests
from bs4 import BeautifulSoup as BS
import pandas as pd
import os

CSV_FILENAME = "BSSEBData.csv" # Add your own roll no dataset file path here and make sure to create a source_csv folder in which it exists
RESULT_URL = "https://portals.au.edu.pk/auresult/"

source_filepath = os.path.join("source_csv", CSV_FILENAME)

student_data = pd.read_csv(source_filepath)
#the dataset columns must match the column names of dataframe
roll_numbers = student_data["Roll_No"].values
student_names = student_data["Names"].values

headers = {
    "Host": "portals.au.edu.pk",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0"
}


def fetch_student_results(roll_no):
    payload = {
        "__EVENTTARGET": "",
        "__EVENTARGUMENT": "",
        "__VIEWSTATE": "",
        "__VIEWSTATEGENERATOR": "",
        "ctl00$AUContent$txt_regid": str(roll_no),
        "__ASYNCPOST": "true",
        "ctl00$AUContent$btnShow": "Search Result"
    }

    response = requests.post(RESULT_URL, headers=headers, data=payload)
    soup = BS(response.text, 'lxml')
    return soup.find_all('table')

student_results = []

for index, roll in enumerate(roll_numbers):
    student_record = {"Name": student_names[index], "Roll_Number": roll}
    tables = fetch_student_results(roll)

    if len(tables) > 2:
        for row in tables[2].find_all('tr')[2:]:  
            columns = [cell.text.strip() for cell in row.find_all('td')]
            if len(columns) > 1:
                student_record[columns[0]] = columns[-1]

        gpa_row = tables[2].find_all('tr')[-1]
        gpa_columns = [cell.text.strip() for cell in gpa_row.find_all('td')]
        if len(gpa_columns) > 1:
            student_record["GPA"] = gpa_columns[-1]

    student_results.append(student_record)

results_df = pd.DataFrame(student_results)
#make sure to update the end course codes like 2311 and 2214
columns_to_drop = ["S-24-Quranic Studies-2311", "S-24-Sirat Ul Nabi-2214"]
results_df.drop(columns=[col for col in columns_to_drop if col in results_df.columns], inplace=True)

output_filename = f"{os.path.splitext(CSV_FILENAME)[0]}-result.csv"
results_df.to_csv(output_filename, index=False)
