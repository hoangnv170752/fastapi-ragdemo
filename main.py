from typing import Union
import pandas as pd
from fastapi import FastAPI

df=pd.read_csv(r"/Users/akashi/Desktop/fastapi-ragdemo/uszips.csv")
app = FastAPI()


@app.get("/getzip/{name}")
def getZip(name):
    df1=df[df["city"]==name]
    data=str(df1["zip"].values[0])
    print(df1)
    return {"Zipcode": "00"+data}