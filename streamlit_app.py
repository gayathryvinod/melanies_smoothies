# Import python packages.
import streamlit as st
import pandas as pd
import requests  
from snowflake.snowpark.functions import col

st.title(f":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write(
  """Choose the fruits you want in your custom Smoothie!""")

cnx = st.connection("snowflake")
session = cnx.session()

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()


name_on_order = st.text_input('Name on Smoothie')
st.write('Name on your Smoothie will be:', name_on_order)

ingredients_list = st.multiselect('Choose upto 5 ingredients:', my_dataframe, max_selections = 5)

if ingredients_list:
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
      ingredients_string += fruit_chosen + ' '

      search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
      st.write('The search value for ', fruit_chosen,' is ', search_on, '.')

      
      st.subheader(fruit_chosen + ' Nutritional Information')
      response = requests.get("https://my.smoothiefroot.com/api/fruit/" + fruit_chosen)
      # Ensure we got a valid response before trying to display it
      if response.status_code == 200:
        sf_json = response.json()
        nutrition_data = sf_json.get('nutrition')
        if nutrition_data:
            df_nutrition = pd.DataFrame([nutrition_data]).T
            df_nutrition.columns = ['Value']
            st.dataframe(df_nutrition, use_container_width=True)
        else:
            st.write(f"Nutrition data not available for {fruit_chosen}")
      else:
          st.error(f"Could not find data for {fruit_chosen}")
  
  
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order) values ('""" + ingredients_string + """', '"""+ name_on_order + """')"""
    #st.write(my_insert_stmt)
    time_to_insert = st.button('Submit Order')

    #button needed else every selection results in an extra 'orders'
    if time_to_insert: 
        session.sql(my_insert_stmt).collect()
        st.success("Your Smoothie is ordered, " + name_on_order + "!", icon = "✅")
    
