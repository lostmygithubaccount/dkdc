import os
import subprocess
import pandas as pd

to_delete = ['cody-azureml-rg']

for rg in to_delete:
    print('Deleting: {}'.format(rg))
    os.system(f'az group delete -n {rg} --no-wait -y')
