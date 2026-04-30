import streamlit as st
from datetime import datetime
from src.vision import detect_ingredients
from src.recipes import get_recipes

DIET_MAP = {
    "None": None,
    "Vegetarian": "vegetarian",
    "Vegan": "vegan",
    "Gluten-free": "gluten free",
    "Paleo": "paleo",
    "Keto": "ketogenic"
}

st.set_page_config(
    page_title="Fridge 2 Recipe", 
    page_icon="🍳",
    layout="wide")


st.title("Fridge 2 Recipe 🍳")
st.markdown(":red[Don't know what to cook? Upload a photo of your fridge and we'll suggest recipes based on what you have!]")

# The sidebar
with st.sidebar:
    st.header("Settings")
    max_recipes = st.slider("Max recipes", min_value=1, max_value=10, value=6, step=1)
    diet_label = st.selectbox("Diet preference", options = list(DIET_MAP.keys()))
    diet = DIET_MAP[diet_label]

    st.space()
    if st.button("Refresh recipes"):
        st.session_state.pop("recipes", None) # remove recipes from session state and repull API call with updated setting

# The main layout

col1, col2 = st.columns([1, 1], gap="large")

# The LFS: File uploader/ingredients detector
with col1:
    st.subheader("Your Fridge")
    uploaded_file = st.file_uploader(
        "Upload a photo of the inside of your fridge.", 
        type=["jpg", "jpeg", "png"], 
        help="Take a photo of your open fridge or lay your ingredients out on a counter",
        accept_multiple_files=False
        )
    
    if uploaded_file is not None:
        # display the uploaded photo
        st.image(uploaded_file, caption="Uploaded photo", width='stretch') 

        # add a button and a spinner to analyze the fridge
        if st.button("Analyze fridge", type="primary"): # if this button is pressed
            with st.spinner("Identifying ingredients..."):

                try:
                    # clear the current-result keys, so information is fresh with every new upload
                    st.session_state.pop("ingredients", None)
                    st.session_state.pop("image_bytes", None)
                    st.session_state.pop("recipes", None)

                    image_bytes = uploaded_file.getvalue() # getvalue() avoids stream-position issues across reruns/re-clicks
                    ingredients = detect_ingredients(image_bytes) # API Call

                    if ingredients: # if the list is not blank
                        # update current results
                        st.session_state["ingredients"] = ingredients
                        st.session_state["image_bytes"] = image_bytes

                        # update to running history 
                        if "scan_history" not in st.session_state:
                            st.session_state["scan_history"] = []
                        
                        st.session_state["scan_history"].append({
                            "ingredients": ingredients,
                            "timestamp": datetime.now().isoformat()
                        })

                    else: # if the list is blank
                        st.warning("Couldn't detect any ingredients — try a clearer photo.")
                
                except Exception as e:
                    st.error(f"Something went wrong: {str(e)}")
        st.subheader("Detected ingredients")

        if "ingredients" in st.session_state: # check if the ingredients are in the session state
            ingredients = st.session_state["ingredients"]
            
            with st.expander(f"Found {len(ingredients)} ingredients!"):
                for ingredient in ingredients:
                    st.markdown(f"- {ingredient}")
        else:
            st.markdown("*No ingredients detected.*")

# The RHS: Display suggested recipes
with col2:
    st.subheader("Suggested Recipes")

    if "ingredients" in st.session_state:

        # storing recipe results in session state so it doesn’t re-fetch on every UI interaction
        if "recipes" not in st.session_state:
            with st.spinner("Finding recipes..."):
                try:
                    recipes = get_recipes(ingredients, max_results=max_recipes, diet=diet) # API Call
                    st.session_state["recipes"] = recipes # list of dictionaries 
                except Exception as e:
                    st.error(f"Could not fetch recipes: {str(e)}")

        if "recipes" in st.session_state:
            recipes = st.session_state["recipes"]

            if not recipes: # no recipes returned from API
                st.info("No recipes found for these ingredients. Try uploading a different photo.")
            else:
                for recipe in recipes:
                    with st.container():
                        img_col, text_col = st.columns([1, 2])

                        with img_col:
                            st.image(recipe["image"], width='stretch')
                        with text_col:
                            st.markdown(f"**{recipe['title']}**")
                            st.caption(
                                f"Uses {recipe['used_count']} of your ingredients · "
                                f"Missing {recipe['missed_count']}"
                            )
                            if recipe["missed_ingredients"]:
                                st.caption(f"You'd need: {', '.join(recipe['missed_ingredients'])}")

                            st.link_button("View recipe", recipe["url"])