from src.recipes import get_recipes

test_ingredients = ['cheese', 'tomatos', 'spinach', 'egg']
recipes = get_recipes(ingredients=test_ingredients, max_results=5)

for r in recipes:
    print(f"{r['title']}")
    print(f"  Uses: {r['used_count']} of your ingredients")
    print(f"  Missing: {r['missed_ingredients']}")
    print(f"  URL: {r['url']}")
    print()