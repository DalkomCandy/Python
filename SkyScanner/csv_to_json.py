import json
import pandas as pd

def csv_to_json(today):
    df_csv = pd.read_csv(f'csv_data\{today}.csv', encoding="utf-8")
    df_dict = df_csv.to_dict(orient = 'records')

    data = {}
    data[today] = {}
    Departure_Date = list(set(df_csv['Departure_Date']))

    for i in Departure_Date:
        data[today][i] = []
        for j in df_dict:
            if j['Departure_Date'] == i:
                data[today][i].append(j)
        

    with open('json\data.json', 'a', encoding="utf-8") as outfile:
        json.dump(data, outfile, ensure_ascii=False)

