from instance import Instance

def preassign(instance: Instance):

    kinderen_voorrang = instance.filter_kinderen_voorrang()
    not_accepted = []
    
    for kind_id, kind in kinderen_voorrang.items():
    
        # elk kind in voorrangsperiode zou school van keuze moeten krijgen
        kind.voorrangs_applicaties.sort(key=lambda applicatie: applicatie.voorkeur_student)
        assignment = None

        for applicatie in kind.voorrangs_applicaties:
            # zal meestal maar 1 applicatie zijn??
            school_id = applicatie.school_id
            school = instance.schools.get(school_id)

            assignment = school.assign(kind, by="preassign")
            if assignment:
                kind.assign(school, assignment)
                break
            
        if not assignment:
            not_accepted.append(kind)
    return not_accepted

def assign_onbepaald(instance: Instance, onbepaald):
    
    not_assigned = []

    for kind in onbepaald:
        # zet status naar IND ipv 'onbepaald'
        kind.indicator_status = "IND"
        assignment = None
        for applicatie in kind.voorrangs_applicaties:
            school = instance.schools.get(applicatie.school_id)
            assignment = school.assign(kind, by="preassign")
            if assignment:
                kind.assign(school, assignment)
                break
        if not assignment:
            not_assigned.append(kind)
    return not_assigned
        
            
def boston(instance):

    kinderen = instance.filter_kinderen_not_assigned()
    for i in range(len(instance.schools)):
        print(f"choice: {i}")
        # max iterations is number of schools (listing per student)
        for school_id, school in instance.schools.items():
            if not school.can_accept():
                continue
            
            # find students with school as top i choice
            kandidaten = []
            for _, kind in kinderen.items():
                if kind.is_assignable and kind.get_ith_preference(i) == school_id:
                    student_priority = kind.get_priority_at_school(school_id)
                    kandidaten.append((kind, student_priority))
            
            # assign student to school in decreasing priority
            kandidaten.sort(key=lambda x: x[1])  # lower index is higher priority

            for candidate, _ in kandidaten:
                if not school.can_accept():
                    break
                assignment = school.assign(candidate, by="boston")  # todo: test of hier altijd assignment uitkomt
                candidate.assign(school, assignment)