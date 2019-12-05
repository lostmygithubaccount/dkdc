import subprocess
import pandas as pd

whitelist = [
            'copetersRG',
]

df = pd.read_csv('data/Azureresourcegroups.csv')
names = df['NAME'].values

for name in names:
    if name not in whitelist:
        print('Deleting: {}'.format(name))
        #subprocess.run(['az', 'group', 'delete', '-n', name, '--no-wait', '-y'])

#subprocess.run(['az', 'group', 'delete', '-n', 'rajeshn-AML-rg', '--no-wait', '-y'])
#os.system('az group delete -n rajeshndriftrg --no-wait -y')
