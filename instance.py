import json
from typing import Dict, List
from student import Student
from school import School
from application import Application
from assignment import Assignment

class Instance:
    
    def __init__(self, path_kinderen: str, path_schools: str):

        self.schools_ids = []
        self.student_ids = []

        self.schools = {}

        self.kinderen = {}
        self.school_capacities = {}

        self.__read_instance__(path_kinderen=path_kinderen, path_schools=path_schools)
 
    def __read_instance__(self, path_kinderen, path_schools):
        
        with open(path_schools, "r") as file:
            schools_content = json.load(file)

        with open(path_kinderen, 'r') as file:
            kinderen_content = json.load(file)

        self.school_ids_uniek = list(schools_content.keys())
        self.student_ids = list(kinderen_content.keys())

        # initialize schools
        for school_id, school_info in schools_content.items():
            
            preferences = school_info.get("applicaties")
            preferences = [(kind_id, preferences.get(kind_id).get('toeval')) for kind_id in preferences.keys()]
            preferences.sort(key=lambda x: x[1])
            preferences = [i[0] for i in preferences]  # drop toeval, enkel rangorde in lijst telt nu

            school = School(
                unique_id=school_info.get("school_id_uniek"),
                school_id=school_info.get("school_id"),
                ind_capacity=school_info.get('INDCapaciteit'),
                n_ind_capacity=school_info.get('nINDCapaciteit'),
                preferences=preferences
                )
            self.schools.update({
                school_id: school
            })
        
        # initialize alle kinderen
        for kind_id, kind_info in kinderen_content.items():

            preferences = kind_info.get('applicaties')
            preferences = [(school_id, preferences.get(school_id).get('voorkeur')) for school_id in preferences.keys()]
            preferences.sort(key=lambda x: x[1])
            preferences = [i[0] for i in preferences]

            applicaties = [Application(
                periode = item.get("periode"),
                student_id = kind_id,
                school_id = key,
                voorkeur_student = item.get("voorkeur"),
                toeval = item.get('toeval')
            ) for key, item in kind_info.get('applicaties').items()]

            kind = Student(id=kind_id, school_preferences=preferences, indicator_status=kind_info.get("indicator_status"), applicaties = applicaties)
            
            self.kinderen.update({
                kind_id: kind
            }) 

    def filter_kinderen_voorrang(self):
        """
            filter kinderen met applicaties in periode 1
        """
        kinderen_voorrang = {}
        for kind_id, kind in self.kinderen.items():
            
            applications = kind.get_applications_from_period(period=1)
            if len(applications) > 0:
                kind.voorrangs_applicaties = applications
                kinderen_voorrang.update({kind_id: kind})
        return kinderen_voorrang

    def filter_kinderen_not_assigned(self):
        not_assigned = dict(filter(lambda kind: not kind[1].is_assigned, self.kinderen.items()))
        return not_assigned

    def make_all_students_assignable(self):
        for student_id, student in self.kinderen.items():
            student.is_assignable = True
