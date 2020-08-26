from School import PreAssignSchool
import json

def preassign(path_kinderen, path_schools):
    
    with open(path_kinderen, 'r') as file:
        kinderen_voorrang = json.load(file)
    
    with open(path_schools, 'r') as file:
        schools = json.load(file)

    for kind_id, kind in kinderen_voorrang

    
    
if __name__ == "__main__":
    preassign("data/kinderen_voorrang.json", "data/scholen.json")