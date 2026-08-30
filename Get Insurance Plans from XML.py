# Script to exctract info on the insurance coverage from an XML file into a separate CSV-file

import pandas as pd
import xml.etree.ElementTree as ET

xml_file = "./**_Data_File_20260720_040132_1102975_**.xml"

tree = ET.parse(xml_file)
root = tree.getroot()
employees = root.findall(".//Employee")

all_rows = []

allowed_types = {"Open", "Current"}

for emp in employees:
    enrollments = emp.findall(".//Enrollment")

    if not enrollments:
        continue

    valid_enrollments = [e for e in enrollments if e.findtext("EnrollmentType") in allowed_types]

    if not valid_enrollments:
        continue

    for enrollment in valid_enrollments:
        row = {
            "Enrollment Type": enrollment.findtext("EnrollmentType"),
            "Plan Name": enrollment.findtext("Plan"),
            "Benefit": enrollment.findtext("Benefit"),
            "Plan Start Date": enrollment.findtext("PlanStarts"),
            "Plan End Date": enrollment.findtext("PlanEnds"),
            "Plan ID": enrollment.findtext("PlanIdentifier")
            }

        all_rows.append(row)

unique = []
seen = set()

for i in all_rows:
    key = tuple(sorted(i.items()))
    if key not in seen:
        seen.add(key)
        unique.append(i)

df = pd.DataFrame(unique)
file_name = xml_file.replace('.xml', '.csv')

df.to_csv(file_name, index = False)
