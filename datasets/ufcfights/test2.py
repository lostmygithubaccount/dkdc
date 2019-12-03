import pyspark
from time import time

sc = pyspark.SparkContext()
sql = pyspark.SQLContext(sc)

times = 10
total = 0

for i in range(times):
    t1 = time()
    df = sql.read.csv('data.csv', header=True)
    t2 = time()

    total += (t2 - t1)

print(total / times)
