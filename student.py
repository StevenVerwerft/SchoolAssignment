from typing import List


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