import pandas as pd

numbers = pd.Series([100,200,300])
print(numbers)

score = pd.Series([90,88,40], index=['혁환','명현','효근'])
print(score)
print(score.index)
print(score.values)

print(score.index[2],score.values[2])