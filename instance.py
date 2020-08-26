import json
from typing import Dict, List


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

            school = AntwerpSchool(
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

    def get_assignments(self):
        """
        Returns a map of student-school pairs.
        """
        assignments = {}

        for student in self.kinderen.values():
            if student.is_assigned:
                assignments.update({
                    student.id : student.assignments
                })

        return assignments
    
    def get_school_info(self):

        school_info = {}

        for school_id, school in self.schools.items():
            school_info.update({
                school_id: {
                    "unique_id": school_id,
                    "school_id": school.school_id,
                    "nINDCapacity": school.n_ind_capacity,
                    "numnINDStudents": len(school.n_ind_students),
                    "nINDStudents": [student.id for student in school.n_ind_students],
                    "INDCapacity": school.ind_capacity,
                    "numINDStudents": len(school.ind_students),
                    "INDStudents": [student.id for student in school.ind_students]
                }
            })
        return school_info


class Assignment:
    def __init__(self, student_id, school_id, unique_school_id, order_of_preference: int, voorkeur: int, assigned_by: str, ind_status: str):
        
        self.student_id = student_id
        self.school_id = school_id
        self.unique_school_id = unique_school_id
        self.groep = unique_school_id.split("_")[1]
        self.order_of_preference = order_of_preference
        self.voorkeur = voorkeur
        self.assigned_by = assigned_by
        self.ind_status = ind_status
    
    def as_dict(self):
        repr = {
            "kind_id": self.student_id,
            "school_id": self.school_id,
            "unique_school_id": self.unique_school_id,
            "groep": self.groep,
            "order_of_preference": self.order_of_preference,
            "voorkeur": self.voorkeur,
            "assigned_by": self.assigned_by,
            "ind_status": self.ind_status
            }
        return repr


class AntwerpSchool:

    def __init__(self, unique_id: str, school_id: str, preferences: List[str], n_ind_capacity: int, ind_capacity: int):
        
        self.unique_id = unique_id
        self.school_id = school_id

        self.preferences = preferences
        
        self.n_ind_capacity = n_ind_capacity
        self.ind_capacity = ind_capacity
        self.total_capacity = n_ind_capacity + ind_capacity
        
        self.ind_students = []
        self.n_ind_students = []
        self.assignments = []

    def assign(self, student, by) -> Assignment:

        """
        assigns student to school, if student is indicator -> assign to indicator students. If no capacity in indicator students, assign to non indicators
        """

        if student.indicator_status == "IND":
            assignment = self.__assign_student__(student, "IND", by)
            if not assignment:
                assignment = self.__assign_student__(student, "nIND", by)
            return assignment

        elif student.indicator_status == "nIND":
            assignment = self.__assign_student__(student, "nIND", by)
            if not assignment:
                assignment = self.__assign_student__(student, "IND", by)
            return assignment

    def __assign_student__(self, student, status, by) -> Assignment:

        if status == "IND":
            if len(self.ind_students) < self.ind_capacity:
                self.ind_students.append(student)
                assignment = self.__make_assignment__(student, status, by)
                return assignment
            return None

        elif status == "nIND":
            if len(self.n_ind_students) < self.n_ind_capacity:
                self.n_ind_students.append(student)
                assignment = self.__make_assignment__(student, status, by)
                return assignment
            return None
    
    def __make_assignment__(self, student, ind_status, by):
        assignment = Assignment(
            student_id=student.id,
            school_id=self.school_id,
            unique_school_id=self.unique_id,
            order_of_preference=student.get_preference_order_for_school(self.unique_id),
            voorkeur=student.get_preference_for_school(self.unique_id),
            assigned_by=by,
            ind_status=ind_status
        )
        return assignment

    def can_accept(self):
        return len(self.ind_students) + len(self.n_ind_students) < self.total_capacity


class Student:
    
    def __init__(self, id: str, school_preferences: List[str], applicaties, indicator_status: str = None):

        self.id = id
        self.indicator_status = indicator_status
        self.school_preferences = school_preferences
        self.applicaties = applicaties
        
        self.is_assigned = False  # student has at least one school
        self.is_assignable = True  # student is assignable in current round of assignments

        self.assigned_schools = []
        self.assignments = []  # lijst met tickets voor scholen

        self.voorrangs_applicaties = []

    def get_ith_preference(self, i: int):
        
        try:
            preference = self.school_preferences[i]
        except IndexError:
            # print("index out of range")
            preference = "VAC"
        return preference

    def assign(self, school, assignment):
        
        self.assigned_schools.append(school)
        self.is_assigned = True
        self.is_assignable = False
        self.assignments.append(assignment)
    
    def get_applications_from_period(self, period):
        return list(filter(lambda applicatie: applicatie.periode == period, self.applicaties))
    
    def __get_application__(self, school_id):
        application = list(filter(lambda application: application.school_id == school_id, self.applicaties))  # get first
        return application[0]

    def get_priority_at_school(self, school_id):
        application = self.__get_application__(school_id)
        return application.toeval

    def get_preference_for_school(self, school_id):
        application = self.__get_application__(school_id)
        return application.voorkeur_student
    
    def get_preference_order_for_school(self, unique_school_id):
        return self.school_preferences.index(unique_school_id) + 1


class Application:

    def __init__(self, periode, student_id, school_id, voorkeur_student, toeval, id=None):

        self.periode = periode
        self.student_id = student_id
        self.voorkeur_student = voorkeur_student
        self.toeval = toeval
        self.school_id = school_id
        self.id = id

