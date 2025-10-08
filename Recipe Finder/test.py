
import requests
import json 
from rich import print


print("Recipe Finder and Meal Planner")


ingre=input("Enter the ingredients you have (separated by commas ) : ")
# num=int(input("Enter the number of recipes you want to find : "))

url="https://www.themealdb.com/api/json/v1/1/search.php?s={}".format(ingre)
res=requests.get(url)
data=res.json()
if "Find Recipes":
    print(data["meals"])
    print("[bright_red]Image[/bright_red]  "    + data["meals"][0]["strMealThumb"])
    print("[bright_blue]Name [/bright_blue]  "    + data["meals"][0]["strMeal"])
    print("[blue]Origin[/blue] "    + data["meals"][0]["strCategory"])
    print("[green]Place[/green]  "    + data["meals"][0]["strArea"])
    print("[red]Youtube[/red] " + data["meals"][0]["strYoutube"])
    
    print("__" *40)
    print("[bright_green]Instructions[/bright_green] "   +"\n" + data["meals"][0]["strInstructions"])
    print("__" *40)
    print("[bright_green]Ingredients[/bright_green] ")
    for i in range(1, 20):
        ingredient = data["meals"][0].get(f"strIngredient{i}")
        measure = data["meals"][0].get(f"strMeasure{i}")
        if ingredient:
            print(f" >> {measure} {ingredient}", end="\n")
    print("\n")

    


    

