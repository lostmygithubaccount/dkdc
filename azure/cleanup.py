import subprocess
import pandas as pd

whitelist = [
            'copetersRG',
            'balapv-rg',
            'balapv-adb-rg',
            'balapv-synapse-rg'
]

df = pd.read_csv('data/Azureresourcegroups.csv')
names = df['NAME'].values

for name in names:
    if name not in whitelist:
        print('Deleting: {}'.format(name))
        subprocess.run(['az', 'group', 'delete', '-n', name, '--no-wait', '-y'])
