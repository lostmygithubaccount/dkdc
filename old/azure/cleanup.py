import os
import subprocess
import pandas as pd

whitelist = [
]

df = pd.read_csv('data/Azureresourcegroups.csv')
names = df['NAME'].values

for name in names:
    if 'cody' in name or 'copeters' in name:
        print('Deleting: {}'.format(name))
        os.system(f'az group delete -n {name} --no-wait -y')
