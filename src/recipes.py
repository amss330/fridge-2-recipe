import os
from dotenv import load_dotenv
import requests

load_dotenv()

SPOONACULAR_API_KEY = os.getenv("SPOONACULAR_API_KEY")
BASE_URL = "https://api.spoonacular.com/recipes"


# function to get recipes
# input: list of ingredients
# output: list of dictionaries of recipes
def get_recipes(ingredients: list[str], max_results: int = 5, diet: str = None) -> list[dict]:
    if not ingredients:
        return []
    
    endpoint = f"{BASE_URL}/findByIngredients"

    params = {
        "ingredients": ",".join(ingredients),
        "number": max_results,
        "ranking": 2, # maximises used ingredients (vs ranking=2 which minimises missing ones)
        "ignorePantry": True, # ignores common staples like water, salt, oil when counting missing ingredients
        "apiKey": SPOONACULAR_API_KEY
    }

    if diet: # If diet is not None
        params["diet"] = diet

    # get API response(output) 
    response = requests.get(endpoint, params=params, timeout=10) # the request will give up after 10 seconds
    response.raise_for_status() # throws an exception if the API returns a 4xx or 5xx status code.

    recipes = response.json()

    return [
        {
            "id": r["id"],
            "title": r["title"],
            "image": r["image"],
            "used_count": r["usedIngredientCount"],
            "missed_count": r["missedIngredientCount"],
            "missed_ingredients": [i["name"] for i in r["missedIngredients"]],
            "url": f"https://spoonacular.com/recipes/{r['title'].replace(' ', '-').lower()}-{r['id']}"
        }
        for r in recipes
        ]





