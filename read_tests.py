import pandas as pd 

data = pd.read_csv("tests.csv") 
print(data['questions'])
print()
print()
print()
print(type(data['options']))
print(list(map(str, data['options'][0].split(","))))
print()
print()
print(data['right'])