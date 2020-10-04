import pandas as pd
from gramex.pptgen2 import pptgen

for index, row in pd.read_csv('people.csv').iterrows():
    target = pptgen(
      source='template.pptx',
      rules=[
        {'Name': {'text': row.Name}},
        {'Course': {'text': row.Course}},
        {'Date': {'text': row.Date}},
      ]
    )
    target.save(f'Certificate - {row.Name}.pptx')
    print('Created', f'Certificate - {row.Name}.pptx')
