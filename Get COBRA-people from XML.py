# Script to extract COBRA-people from an XML-file into a new CSV-file
# COBRA-people = people who left the company but should preserve insurance coverage


import xml.etree.ElementTree as ET
import csv

xml_file = "./**_Data_File_20251212_024918_968654_**.xml"

tree = ET.parse(xml_file)
root = tree.getroot()
employees = root.findall(".//Employee")

base_columns = [
    "Employee ID",
    "Employment Status",
    "COBRA Start Date",
    "COBRA Termination Date",
    "Termination Date",
    "First Name",
    "Middle Name",
    "Last Name",
    "Relationship",
    "DOB",
    "Email",
    "Phone",
    "Gender",
    "Address 1",
    "Address 2",
    "City",
    "State",
    "Zip"
]

dynamic_columns = []
all_rows = []

for emp in employees:
    cobra_enrollments = emp.findall(".//CobraEnrollment")

    if not cobra_enrollments:
        continue

    plan_data = {}
    for enrollment in cobra_enrollments:
        benefit = enrollment.findtext("Benefit")
        if not benefit:
            continue
        plan_name_col = f"{benefit} Plan Name"
        effective_col = f"{benefit} Effective Date"
        term_col = f"{benefit} Termination Date"

        plan_data[plan_name_col] = enrollment.findtext("Plan")
        plan_data[effective_col] = enrollment.findtext("EligibleFrom")
        plan_data[term_col] = enrollment.findtext("EligibleUntil")

        for col in [plan_name_col, effective_col, term_col]:
            if col not in dynamic_columns:
                dynamic_columns.append(col)

    def extract_common_fields(node, is_employee = True):
        return {
            "Employee ID": emp.findtext("ExternalEmployeeId"),
            "Employment Status": "C" if is_employee else "",
            "COBRA Start Date": "",
            "COBRA Termination Date": "",
            "Termination Date": emp.findtext("TerminationDate"),
            "First Name": node.findtext("FirstName"),
            "Middle Name": node.findtext("MiddleName"),
            "Last Name": node.findtext("LastName"),
            "Relationship": "Employee" if is_employee else node.findtext("Relationship"),
            "DOB": node.findtext("DOB"),
            "Email": emp.findtext("Email") if is_employee else "",
            "Phone": emp.findtext("Phone") if is_employee else "",
            "Gender": node.findtext("Gender"),
            "Address 1": node.findtext("Address1"),
            "Address 2": node.findtext("Address2"),
            "City": node.findtext("City"),
            "State": node.findtext("State"),
            "Zip": node.findtext("ZIP")
        }

    employee_row = extract_common_fields(emp, is_employee = True)
    employee_row.update(plan_data)
    all_rows.append(employee_row)

    for dep in emp.findall(".//Dependent"):
        dependent_row = extract_common_fields(dep, is_employee = False)
        all_rows.append(dependent_row)

final_headers = base_columns + dynamic_columns

with open("csv_output.csv", "w", newline = "", encoding = "utf-8") as f:
    writer = csv.DictWriter(f, fieldnames = final_headers)
    writer.writeheader()
    for row in all_rows:
        writer.writerow(row)
