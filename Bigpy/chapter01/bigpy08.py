import pandas as pd

temperatures = [[3.3,34.5,14.2,-10],[7.1,32.1,10.7,2]]
seasons = ['Sprint','Summer','Fall','Winter']
regions = ['Seoul','Pusan']

data = pd.DataFrame(temperatures,index=regions,columns=seasons)

print(data)
print('-'*20)
print(data.index)
print(data.columns)
print(data.values)