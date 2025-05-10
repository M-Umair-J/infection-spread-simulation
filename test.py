import random

immunity = 0.1
immunity = immunity + random.uniform(0.02,0.2)
recovery_time = int(immunity * random.randint(10,40))
print(recovery_time)