# Import python packages
import streamlit as st
import pandas as pd
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie ! :cup_with_straw:")
st.write(
  """Choose the fruits you want in your custom Smoothie !
  """
)

name_on_order = st.text_input("Name on smoothie")
st.write("The name on your smoothie will be :", name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

pd_df = my_dataframe.to_pandas()

ingredient_list = st.multiselect(
    'Choose up to 5 ingredient: '
    , my_dataframe
    , max_selections=5
)
if ingredient_list:
    
    ingredients_string = ''

    for fruit_chosen in ingredient_list:
        ingredients_string += fruit_chosen + ' '
          
        st.subheader(fruit_chosen+ ' Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/"+fruit_chosen)
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
      
    st.write(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
            values ('""" + ingredients_string + """','""" + name_on_order + """' )"""

    #st.write(my_insert_stmt)
    time_to_insert = st.button('Submit Order')
    if time_to_insert: 
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")


