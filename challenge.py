# Welcome!
#
# Your task is to use the NIH ICD-10 API to create a function that transforms raw patient data into a more human readable format.
# You will do this by filling out the TODO stub in the function description. the filled out solution function, when given patient_data, should
# return an output identical to expected_output (non-trivially, that is, through a series of transformations using the api and the provided
# priority diagnosis substrings)

#   In brief, the motivation is that you will:
#  1) make the patient data human readable by including each code's description using the API
#  2) identify malformed codes (codes that are not valid ICD-10)
#  3) flag patients that have codes where the description contains "covid" or "respiratory failure" as priority_diagnoses
#
# output:
# The expected output is a list containing elements of the following format.
# It should be sorted in descending order based on the number of 'priority_diagnoses'.
#
# {'id': 0,
#  'diagnoses': [
#      ('U07.1', 'COVID-19'),
#      ('N18.30', 'Chronic kidney disease, stage 3 unspecified')],
#  'priority_diagnoses': ['COVID-19'],
#  'malformed_diagnoses': []
#
# API docs: https://clinicaltables.nlm.nih.gov/apidoc/icd10cm/v3/doc.html

import requests

base_url = "https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search"
patient_data = [
    {"patient_id": 0, "diagnoses": ["I10", "K21.9"]},
    {"patient_id": 1, "diagnoses": ["E78.5", "ABC.123", "U07.1", "J96.00"]},
    {"patient_id": 2, "diagnoses": []},
    {"patient_id": 3, "diagnoses": ["U07.1", "N18.30"]},
    {"patient_id": 4, "diagnoses": ["I10", "E66.9", "745.902"]},
    {"patient_id": 5, "diagnoses": ["G47.33", "I73.9", "N18.30", 1]},
]


def api_call(code):
    url = base_url
    params = {"sf": "code", "terms": code, "maxList": 2}

    response = requests.get(url, params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")


def solution(data):
    result = []

    for patient in data:
        patient_result = {
            "patient_id": patient["patient_id"],
            "diagnoses": [],
            "priority_diagnoses": [],
            "malformed_diagnoses": [],
        }
        for diagnosis_code in patient["diagnoses"]:
            response = api_call(diagnosis_code)
            if response[0] == 0:
                patient_result["malformed_diagnoses"].append(diagnosis_code)
            else:
                diagnosis_name = response[3][0][1]
                patient_result["diagnoses"].append(
                    (diagnosis_code, diagnosis_name))

                if (
                    "covid" in diagnosis_name.lower()
                    or "respiratory failure" in diagnosis_name.lower()
                ):
                    patient_result["priority_diagnoses"].append(diagnosis_name)

        result.append(patient_result)

    result = sorted(result, key =lambda d : len(d["priority_diagnoses"]), reverse=True)

    return result


output = solution(patient_data)

expected_output = [
    {
        "patient_id": 1,
        "diagnoses": [
            ("E78.5", "Hyperlipidemia, unspecified"),
            ("U07.1", "COVID-19"),
            (
                "J96.00",
                "Acute respiratory failure, unspecified whether with hypoxia or hypercapnia",
            ),
        ],
        "priority_diagnoses": [
            "COVID-19",
            "Acute respiratory failure, unspecified whether with hypoxia or hypercapnia",
        ],
        "malformed_diagnoses": ["ABC.123"],
    },
    {
        "patient_id": 3,
        "diagnoses": [
            ("U07.1", "COVID-19"),
            ("N18.30", "Chronic kidney disease, stage 3 unspecified"),
        ],
        "priority_diagnoses": ["COVID-19"],
        "malformed_diagnoses": [],
    },
    {
        "patient_id": 0,
        "diagnoses": [
            ("I10", "Essential (primary) hypertension"),
            ("K21.9", "Gastro-esophageal reflux disease without esophagitis"),
        ],
        "priority_diagnoses": [],
        "malformed_diagnoses": [],
    },
    {
        "patient_id": 2,
        "diagnoses": [],
        "priority_diagnoses": [],
        "malformed_diagnoses": [],
    },
    {
        "patient_id": 4,
        "diagnoses": [
            ("I10", "Essential (primary) hypertension"),
            ("E66.9", "Obesity, unspecified"),
        ],
        "priority_diagnoses": [],
        "malformed_diagnoses": ["745.902"],
    },
    {
        "patient_id": 5,
        "diagnoses": [
            ("G47.33", "Obstructive sleep apnea (adult) (pediatric)"),
            ("I73.9", "Peripheral vascular disease, unspecified"),
            ("N18.30", "Chronic kidney disease, stage 3 unspecified"),
        ],
        "priority_diagnoses": [],
        "malformed_diagnoses": [1],
    },
]
try:
    # installed new library to compare the output and expected output correctly
    assert output == expected_output
except AssertionError:
    print("error: your output does not match the expected output")
else:
    print("success!")
