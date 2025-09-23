
import requests
import json 
from rich import print


print("Recipe Finder and Meal Planner")


ingre=input("Enter the ingredients you have (separated by commas ) : ")

url="https://www.themealdb.com/api/json/v1/1/search.php?s={}".format(ingre)
res=requests.get(url)
data=res.json()
if "Find Recipes":
    # print(data["meals"])
    print("Image  "    + data["meals"][0]["strMealThumb"])
    print("Name   "    + data["meals"][0]["strMeal"])
    print("Origin "    + data["meals"][0]["strCategory"])
    print("Place  "    + data["meals"][0]["strArea"])
    print("__" *40)
    print("Instructions "    + data["meals"][0]["strInstructions"])


    

