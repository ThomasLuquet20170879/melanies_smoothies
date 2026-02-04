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

my_dataframe_bis = session.table("smoothies.public.orders").select(col('order_filled'),col('name_on_order'),col('ingredients'))
editable_df = st.data_editor(my_dataframe_bis)
      
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))

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

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen,' is ', search_on,'.')

        result = search_on if search_on is not None else fruit_chosen
        st.subheader(fruit_chosen+ ' Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/"+ result)
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
      
    st.write(ingredients_string)
    agree = st.checkbox("Filled")
    if agree:
      order_filled = 'TRUE'
      st.write(order_filled)
    else:
      order_filled = 'FALSE'
  
  
    my_insert_stmt = """ insert into smoothies.public.orders(order_filled, ingredients, name_on_order)
            values ('""" + order_filled + """','""" + ingredients_string + """','""" + name_on_order + """' )"""

    #st.write(my_insert_stmt)
    time_to_insert = st.button('Submit Order')
    if time_to_insert: 
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")


