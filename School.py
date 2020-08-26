class PreAssignSchool:
    def __init__(self, capacity, n_ind_capacity, ind_capacity, preferences):

        self.n_ind_capacity = n_ind_capacity
        self.ind_capacity = ind_capacity
        self.capacity = capacity
        self.preferences = preferences

        self.ind_students = []
        self.n_ind_students = []
        