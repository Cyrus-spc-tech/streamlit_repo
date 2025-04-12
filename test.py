import pandas as pd
csv=pd.read_csv("data.csv",sep=";")
df=pd.DataFrame(csv)
print(df.head(5))
# s=pd.Series(csv)
# print(s)