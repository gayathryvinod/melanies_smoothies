# Import python packages
import streamlit as st
import pandas as pd
import requests  
import urllib.parse 
from snowflake.snowpark.functions import col

# App Title and Description
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Snowflake Connection
cnx = st.connection("snowflake")
session = cnx.session()

# Prepare Data
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()

# User Input for Name
name_on_order = st.text_input('Name on Smoothie')
if name_on_order:
    st.write('Name on your Smoothie will be:', name_on_order)

# Fruit Selection - Using Pandas DF for clean string output
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:', 
    pd_df['FRUIT_NAME'], 
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''

    # Loop through selected fruits to display nutrition
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        
        # Lookup the SEARCH_ON value from our Pandas DataFrame
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0] 
        
        if search_on:
            st.subheader(f"{fruit_chosen} Nutritional Information")
            
            # Encode for URLs (Handles spaces and parentheses like 'Ximenia (Hog Plum)')
            search_on_encoded = urllib.parse.quote(search_on)
            response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on_encoded}")
            
            if response.status_code == 200:
                sf_json = response.json()
                # Access the nested 'nutrition' dictionary
                nutrition_data = sf_json.get('nutrition')
                
                if nutrition_data:
                    df_nutrition = pd.DataFrame([nutrition_data]).T
                    df_nutrition.columns = ['Value']
                    st.dataframe(df_nutrition, use_container_width=True)
                else:
                    st.write(f"Nutrition data not available for {fruit_chosen}")
            else:
                st.error(f"Could not find data for {fruit_chosen} (Search term: {search_on})")
        else:
            st.warning(f"No search term configured in the database for {fruit_chosen}.")

    # --- ORDER SUBMISSION SECTION (Outside the For Loop) ---
    my_insert_stmt = f"""insert into smoothies.public.orders(ingredients, name_on_order) 
                        values ('{ingredients_string.strip()}', '{name_on_order}')"""
    
    time_to_insert = st.button('Submit Order')

    if time_to_insert: 
        if name_on_order: # Simple check to ensure a name was entered
            session.sql(my_insert_stmt).collect()
            st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")
        else:
            st.error("Please provide a name for the order before submitting.")
