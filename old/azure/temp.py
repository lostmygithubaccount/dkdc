import subprocess
import pandas as pd

blacklist = [
            'copetersRG',
            'cody-benchmark-rg',
            'cody-daskv2-rg',
            'copeters-dask-rg',
            'copeters-rg', 
            'copetersRG'
]

for name in blacklist:
    print('Deleting: {}'.format(name))
    subprocess.run(['az', 'group', 'delete', '-n', name, '--no-wait', '-y'])
