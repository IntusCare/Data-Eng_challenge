# Welcome!
#
# Your task is to use the NIH ICD-10 API to create a function that transforms raw patient data into a more human readable format. 
# You will do this by filling out the TODO stub in the function description. The filled out solution function, when given patient_data, should 
# return an output identical to expected_output (non-trivially, that is, through a series of transformations using the api and the provided 
# priority diagnosis substrings)

#   In brief, the motivation is that you will:s
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

base_url = ("https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search"
            "?sf={search_fields}&terms={search_term}&maxList={max_list}")
patient_data = [
    {"patient_id": 0,
     "diagnoses": ["I10", "K21.9"]},
    {"patient_id": 1,
     "diagnoses": ["E78.5", "ABC.123", "U07.1", "J96.00"]},
    {"patient_id": 2,
     "diagnoses": []},
    {"patient_id": 3,
     "diagnoses": ["U07.1", "N18.30"]},
    {"patient_id": 4,
     "diagnoses": ["I10", "E66.9", "745.902"]},
    {"patient_id": 5,
     "diagnoses": ["G47.33", "I73.9", "N18.30", 1]}
]

"""
    Takes in patient data and uses the NIH ICD-10 API to transform it into a more human-readable format

    Params:
        data: list of { 'patient_id': number, 'diagnoses': list of diagnosis code strings }

    Returns:
        List of { 
            'patient_id': number, 
            'diagnoses': list of (code string, description string),
            'priority_diagnoses': list of description strings,
            'malformed_diagnoses': list of code strings
        }
"""
def solution(data):
    MAX_LIST_RETURNED = 2
    priority_diagnosis_flags = ["covid", "respiratory failure"] # diagnoses containing these words will be flagged as priority diagnoses

    # helper function that checks whether description string contains any string in flags
    def description_contains_flag(description, flags):
        for flag in flags:
            if flag.lower() in description.lower():
                return True
        return False

    # aggregate diagnoses to be fetched (so only one API call is needed per code)
    codes = []
    for patient_data in data:
        codes += patient_data["diagnoses"]

    # perform the API call for each code and create a map from code to description
    code_to_description = {}
    for code in codes:
        query_url = base_url.format(search_fields="code",search_term=code,max_list=MAX_LIST_RETURNED)
        response = requests.get(query_url)

        if response.status_code != 200:
            raise Exception("Error! NIH ICD-10 API call returned a non-200 status code.")
        
        code_description_pairs = response.json()[3]

        if len(code_description_pairs) == 1:
            description = code_description_pairs[0][1]
            code_to_description[code] = description
        elif len(code_description_pairs) > 1:
            raise Exception(f"Error! NIH ICD-10 API call returned multiple entries for code {code}. Code-to-diagnosis mapping is ambiguous.")

    # iterate through patients, using code_to_description to populate 'diagnoses', 'priority_diagnoses', and 'malformed_diagnoses'
    transformed_data = []
    for patient_data in data:
        patient_id, codes = patient_data["patient_id"], patient_data["diagnoses"]
        diagnoses, priority_diagnoses, malformed_diagnoses = [], [], []
        for code in codes:
            if code in code_to_description:
                code_description_tuple = (code, code_to_description[code])
                diagnoses.append(code_description_tuple)

                if description_contains_flag(description=code_to_description[code], flags=priority_diagnosis_flags):
                    priority_diagnoses.append(code_to_description[code])
            else:
                malformed_diagnoses.append(code)

        patient = { 
            "patient_id": patient_id, 
            "diagnoses": diagnoses, 
            "priority_diagnoses": priority_diagnoses, 
            "malformed_diagnoses": malformed_diagnoses 
        }
        transformed_data.append(patient)

    # sort list based on length of 'priority_diagnoses'
    sorted_transformed_data = sorted(transformed_data, key=lambda d: len(d["priority_diagnoses"]), reverse=True)

    return sorted_transformed_data

output = solution(patient_data)

expected_output = [
        {'patient_id': 1,
         'diagnoses': [
             ('E78.5', 'Hyperlipidemia, unspecified'),
             ('U07.1', 'COVID-19'),
             ('J96.00', 'Acute respiratory failure, unspecified whether with hypoxia or hypercapnia')],
         'priority_diagnoses': [
             'COVID-19', 'Acute respiratory failure, unspecified whether with hypoxia or hypercapnia'],
         'malformed_diagnoses': ['ABC.123']
        },
        {'patient_id': 3,
         'diagnoses': [
             ('U07.1', 'COVID-19'),
             ('N18.30', 'Chronic kidney disease, stage 3 unspecified')],
         'priority_diagnoses': ['COVID-19'],
         'malformed_diagnoses': []
        },
        {'patient_id': 0,
         'diagnoses': [
             ('I10', 'Essential (primary) hypertension'),
             ('K21.9', 'Gastro-esophageal reflux disease without esophagitis')],
         'priority_diagnoses': [],
         'malformed_diagnoses': []
        },
        {'patient_id': 2, 'diagnoses': [],
         'priority_diagnoses': [],
         'malformed_diagnoses': []
        },
        {'patient_id': 4,
         'diagnoses': [
             ('I10', 'Essential (primary) hypertension'),
             ('E66.9', 'Obesity, unspecified')],
         'priority_diagnoses': [],
         'malformed_diagnoses': ['745.902']
        },
        {'patient_id': 5,
         'diagnoses': [
             ('G47.33', 'Obstructive sleep apnea (adult) (pediatric)'),
             ('I73.9', 'Peripheral vascular disease, unspecified'),
             ('N18.30', 'Chronic kidney disease, stage 3 unspecified')],
         'priority_diagnoses': [],
         'malformed_diagnoses': [1]
        }
    ]

try:
    assert(output == expected_output)
except AssertionError:
    print('error: your output does not match the expected output')
else:
    print('success!')
