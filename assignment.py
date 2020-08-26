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