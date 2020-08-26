import pandas as pd
from instance import Instance

def generate_report(instance: Instance, excel_df):
    
    unassigned_students = instance.filter_kinderen_not_assigned()
    i = 0
    data = {}
    for student_id, student in unassigned_students.items():
        data.update({
            i: {
                "kind_id": student_id,
                "Gok_status": student.indicator_status,
                "num_school_applicaties": len(student.school_preferences)
            }
        })
        i += 1
    unassigned_df = pd.DataFrame(data).T

    i = 0
    data = {}
    for student_id, student in instance.kinderen.items():
        for assignment in student.assignments:
            assignment_dict = assignment.as_dict()
            assignment_dict.update({"GokStatus": student.indicator_status})
            data.update({i: assignment_dict})
            i += 1
    assignment_df = pd.DataFrame(data).T
    data = {}
    i = 0
    for school_id, school in instance.schools.items():
        data.update(
            {i: {
                "schoolid": school.school_id,
                "unique_id": school.unique_id,
                "ind_capacity": school.ind_capacity,
                "n_ind_capacity": school.n_ind_capacity,
                "total_capacity": school.total_capacity,
                "num_n_ind_students": len(school.n_ind_students),
                "num_ind_students": len(school.ind_students),
                "num_students": len(school.n_ind_students) + len(school.ind_students)
            }}
        ) 
        i += 1

    school_df = pd.DataFrame(data).T
        
    report_df = assignment_df.merge(school_df, left_on="unique_school_id", right_on="unique_id")
    report_df = report_df[["kind_id", "assigned_by", "ind_status", "GokStatus", "voorkeur",
    "order_of_preference", "ind_capacity", "num_ind_students", "n_ind_capacity", "num_n_ind_students", 
    "total_capacity", "num_students", "groep", "school_id", "unique_school_id"]]

    report_df = report_df.merge(excel_df[["Id", "KindId", "AanmelderId", "UniqueSchoolId"]], left_on=["kind_id", "unique_school_id"], right_on=["KindId", "UniqueSchoolId"])

    applications_df = excel_df[["Id", "KindId", "AanmelderId", "UniqueSchoolId", "SchoolId", "Groep", "PeriodeTypeId"]].merge(
        report_df[["Id", "assigned_by"]], left_on="Id", right_on="Id", how="outer"
    )
    applications_df["assigned_by"] = applications_df["assigned_by"].fillna("rejected")

    with pd.ExcelWriter("export_simulatie.xlsx") as writer:
        report_df.to_excel(writer, sheet_name="overzicht")
        school_df.to_excel(writer, sheet_name="scholen")
        assignment_df.to_excel(writer, sheet_name="toekenningen")
        unassigned_df.to_excel(writer, sheet_name="zonder school")
        applications_df.to_excel(writer, sheet_name="applicaties")