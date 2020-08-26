import pandas as pd
import json
from decimal import Decimal, ROUND_HALF_DOWN

# nodig om ind - n_ind capaciteiten consistent te berekenen
def round_half_down(x):
    return int(Decimal(x).quantize(0, ROUND_HALF_DOWN))


def generate_df_from_excel(excel_path, sheet_name):
    df = pd.read_excel(excel_path, sheet_name)
    df = df[df["PeriodeTypeId"] != 3]
    # geef dataset ook nieuwe ID voor scholen
    df["UniqueSchoolId"] = df["SchoolId"]+"_"+df["Groep"]
    return df

def generate_input_json(excel_path, sheet_name):
    
    df = generate_df_from_excel(excel_path, sheet_name)

    # filter scholen
    scholen = df.groupby(["SchoolId", "Groep"]).agg({"Id": "nunique", "Capaciteit": "max", "NaTeStrevenINDPercentage": "max", "SchoolId": "max", "Groep": "max"})

    scholen["INDCapaciteit"] = (scholen["Capaciteit"] * scholen["NaTeStrevenINDPercentage"]/100).apply(lambda x: round_half_down(x))
    scholen["nINDCapaciteit"] = (scholen["Capaciteit"] * (100 - scholen["NaTeStrevenINDPercentage"])/100).apply(lambda x: round_half_down(x))

    # afrondingsprobleem in gevallen waar capaciteit .5 is. Worden beide naar onder afgerond waardoor plaats verloren gaat
    # In deze gevallen extra plaats toekennen aan niet indicator plaatsen (aangezien na te streven IND percentage zo wordt behouden)
    mask = scholen[scholen["Capaciteit"] != scholen["INDCapaciteit"] + scholen["nINDCapaciteit"]]
    levels = mask.index.levels  # omslachtige code, maar vervangen van waarden obv masks is niet geïmplementeerd voor multiindexes ;(
    codes = mask.index.codes
    multi_indexes = [(levels[0][i], levels[1][j]) for i, j in zip(codes[0], codes[1])]
    scholen.loc[multi_indexes, "nINDCapaciteit"] = scholen.loc[multi_indexes]["nINDCapaciteit"] + 1

    # maak van iedere school - stroom combo nieuwe ID
    new_index = scholen.index.map('{0[0]}_{0[1]}'.format)
    scholen = scholen.set_index(new_index)

    # genereer json scholen
    scholen_json = {}
    for index, school in scholen.iterrows():
        kinderen = df[df["UniqueSchoolId"] == index]
        kind_ids = kinderen["KindId"].tolist()
        applicaties = {}
        for kind_index, kind in kinderen.iterrows():
            applicaties.update({
                kind["KindId"]: {
                    "toeval": kind['Toeval']
                } 
            })
            
        scholen_json.update(
            {index: {
                "school_id_uniek": index,
                "school_id": school["SchoolId"],
                "n_applicaties": len(applicaties),
                "groep": school["Groep"],
                "applicaties": applicaties,
                "kind_ids": kind_ids,
                "capaciteit": school["Capaciteit"],
                "nINDCapaciteit": school["nINDCapaciteit"],
                "INDCapaciteit": school["INDCapaciteit"]
        }})


    # genereer json kinderen
    kinderen = df["KindId"].unique()
    alle_kinderen_json = {}

    for kind_id in kinderen:
        
        records_kind = df[df["KindId"] == kind_id]
        scholen_kind_uniek = records_kind["UniqueSchoolId"].tolist()
        scholen_kind = records_kind["SchoolId"].tolist()
        indicator_status = records_kind["GokStatus"].tolist()[0]
        applicaties = {}
        for index, record in records_kind.iterrows():
            applicaties.update({
                record["UniqueSchoolId"] : {
                    "school_id": record["SchoolId"],
                    "voorkeur": record["Voorkeur"],
                    "periode": record["PeriodeTypeId"],
                    "toeval": record["Toeval"],
                    "naam": record["Naam"]
                }
            })
            
        alle_kinderen_json.update({kind_id: {
            "unieke_school_ids": scholen_kind_uniek,
            "school_ids": scholen_kind,
            "indicator_status": indicator_status,
            "applicaties": applicaties
        }})

    # dump json to files

    with open("data/scholen.json", "w") as file:
        json.dump(scholen_json, file)
    with open("data/alle_kinderen.json", "w") as file:
        json.dump(alle_kinderen_json, file)
        
