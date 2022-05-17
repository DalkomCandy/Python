import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

arabia =  pd.read_csv(r'arabica_data_cleaned.csv', encoding='')
robusta = pd.read_csv(r'robusta_data_cleaned.csv')
merge = pd.read_csv(r'merged_data_cleaned.csv')

print(arabia)

Origin = list(arabia['Origin'])

