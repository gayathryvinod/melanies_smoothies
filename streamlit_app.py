import streamlit as st
import pandas as pd
import requests  
import urllib.parse 
from snowflake.snowpark.functions import col

# --- 1. SETUP & CONNECTION ---
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

cnx = st.connection("snowflake")
session = cnx.session()

# Pull data and convert to Pandas for easy lookup
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()

name_on_order = st.text_input('Name on Smoothie')
if name_on_order:
    st.write('Name on your Smoothie will be:', name_on_order)

# --- 2. FRUIT SELECTION ---
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:', 
    pd_df['FRUIT_NAME'], 
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        
        # Get the search key
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0] 
        
        if search_on:
            #st.subheader(f"{fruit_chosen} Nutritional Information")
            st.write(f"**{fruit_chosen} Nutritional Information**")
            # Encode for special characters and spaces
            search_on_encoded = urllib.parse.quote(search_on)
            response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on_encoded}")
            
            if response.status_code == 200:
                sf_json = response.json()
                # Fetching 'nutrition' specifically
                nutrition_data = sf_json.get('nutrition')
                
                # Check if 'nutrition' exists AND is not an empty dictionary
                if nutrition_data and len(nutrition_data) > 0:
                    df_nutrition = pd.DataFrame([nutrition_data]).T
                    df_nutrition.columns = ['Value']
                    st.dataframe(df_nutrition, use_container_width=True)
                else:
                    # Graceful handling for missing nutrition values
                    st.info(f"The API found '{fruit_chosen}', but no nutritional facts are currently listed.")
            else:
                st.error(f"Could not find '{fruit_chosen}' in the API database.")
        else:
            st.warning(f"No search term set for {fruit_chosen} in your Snowflake table.")

    # --- 3. SUBMISSION SECTION ---
    # Moved outside the loop so it only appears once
    my_insert_stmt = f"""insert into smoothies.public.orders(ingredients, name_on_order) 
                        values ('{ingredients_string.strip()}', '{name_on_order}')"""
    
    time_to_insert = st.button('Submit Order')

    if time_to_insert: 
        if name_on_order:
            session.sql(my_insert_stmt).collect()
            st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")
        else:
            st.warning("Please enter a name for the order before submitting.")
