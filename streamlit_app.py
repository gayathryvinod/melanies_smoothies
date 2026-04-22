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

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
#st.dataframe(data = my_dataframe, use_container_width = True)

name_on_order = st.text_input('Name on Smoothie')
st.write('Name on your Smoothie will be:', name_on_order)

ingredients_list = st.multiselect('Choose upto 5 ingredients:', my_dataframe, max_selections = 5)

if ingredients_list:
    ingredients_string = ''
    
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '    
        
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order) values ('""" + ingredients_string + """', '"""+ name_on_order + """')"""
    #st.write(my_insert_stmt)
    time_to_insert = st.button('Submit Order')

    #button needed else every selection results in an extra 'orders'
    if time_to_insert: 
        session.sql(my_insert_stmt).collect()
        st.success("Your Smoothie is ordered, " + name_on_order + "!", icon = "✅")
      
# new section to display smoothfroot nutrition information 
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
sf_df = pd.DataFrame(smoothiefroot_response.json()) 
st.dataframe(sf_df)
