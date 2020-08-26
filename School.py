from typing import List
from assignment import Assignment


class School:

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