import streamlit as st
from datetime import datetime
from src.vision import detect_ingredients

st.set_page_config(
    page_title="Fridge 2 Recipe", 
    page_icon="🍳",
    layout="wide")


st.title("Fridge 2 Recipe 🍳")
st.markdown(":red[Don't know what to cook? Upload a photo of your fridge and we'll suggest recipes based on what you have!]")

# The sidebar
with st.sidebar:
    st.header("Settings")
    max_recipes = st.slider("Max recipes", min_value=1, max_value=10, value=3, step=1)
    diet_preference = st.selectbox("Diet preference", options=["None", "Vegan", "Vegetarian", "Gluten-free", "Paleo", "Keto"])

# The main layout
col1, col2 = st.columns(2, gap="large")

# The LFS: File uploader/image detector
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
                    # session state is a dictionary object that can be accessed using the st.session_state object
                    # it is used to store data in the browser and persist between reruns

                    # clear the current-result keys
                    st.session_state.pop("ingredients", None)
                    st.session_state.pop("image_bytes", None)

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

# The RHS: Display detected ingredients
with col2:
    st.subheader("Detected ingredients")

    if "ingredients" in st.session_state: # check if the ingredients are in the session state
        ingredients = st.session_state["ingredients"]
        st.success(f"Found {len(ingredients)} ingredients!")

        for ingredient in ingredients:
            st.markdown(f"- {ingredient}")
        
        st.divider()
        st.subheader("Recipes")
        st.info("(Recipe suggestions will appear here.)")
    else:
        st.markdown("*No ingredients detected.*")
