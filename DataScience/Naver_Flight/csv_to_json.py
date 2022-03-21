import json
import pandas as pd

def csv_to_json(DATE):
    data = {}
    data[DATE] = {}
    
    df_csv = pd.read_csv(f'{DATE}.csv', encoding="utf-8")
    Departure_Date = list(set(df_csv['Departure_Date']))
    df_dict = df_csv.to_dict(orient = 'records')

    for i in Departure_Date:
        data[DATE][i] = []
        for j in df_dict:
            if j['Departure_Date'] == i:
                data[DATE][i].append(j)        

    with open('json\data.json', 'a', encoding="utf-8") as outfile:
        json.dump(data, outfile, ensure_ascii=False)