import pandas as pd
from time import time

times = 10

total = 0
for i in range(times):
    t1 = time()
    df = pd.read_csv('data.csv')
    t2 = time()
    total += (t2 - t1)

print(total / times)
