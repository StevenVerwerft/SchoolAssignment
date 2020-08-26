from algorithms import boston, preassign, assign_onbepaald
from post_processing import generate_report
from pre_processing import generate_input_json, generate_df_from_excel
from instance import Instance
import json

print("Start simulation")
GENERATE_INPUT_JSON = False  # json hoeft niet steeds gegenereerd te worden 
GENERATE_OUTPUT_JSON = False

# preprocessing van excel file
print("Preprocessing data excel...")
excel_df = generate_df_from_excel("data/Anonieme_export_voor_simulaties_20200820.xlsx", "Export (32)")

if GENERATE_INPUT_JSON:
    print("Generating input json...")
    generate_input_json("data/Anonieme_export_voor_simulaties_20200820.xlsx", "Export (32)")

# initialiseer alle info over scholen, lln, applicaties, ...
instance = Instance(path_kinderen="data/alle_kinderen.json", path_schools="data/scholen.json")

# ken prioriteitsplaatsen uit periode 1 toe
# overschot meenemen naar volgende fase
print("fase: pre-assign")
not_accepted = preassign(instance)

# status onbepaald => toekennen aan resterende plaatsen (eerst als niet indicator)
# zou nu leeg moeten zijn
not_accepted = assign_onbepaald(instance, not_accepted)

# fase 2: ken plaatsen toe volgens boston algoritme
# lln met ticket uit preassign kunnen opnieuw ticket krijgen indien aangemeld in periode 2
instance.make_all_students_assignable()
print("fase: boston")
boston(instance)

# POST PROCESSING
print("Generating report...")
generate_report(instance, excel_df)

if GENERATE_OUTPUT_JSON:
    # informatie over assignments
    assignments = instance.get_assignments()
    assignments_json = {key: [assignment.as_dict() for assignment in value] for key, value in assignments.items()}
    with open("assignments.json", "w") as file:
        json.dump(assignments_json, file, indent=4)

    # informatie over leerlingen zonder school
    not_assigned = instance.filter_kinderen_not_assigned()
    not_assigned_json = {kind.id: kind.is_assigned for kind in not_assigned.values()}
    with open("not_assigned.json", "w") as file:
        json.dump(not_assigned_json, file, indent=4)

    # informatie over de scholen
    school_info = instance.get_school_info()
    with open("school_info.json", "w") as file:
        json.dump(school_info, file, indent=4)
