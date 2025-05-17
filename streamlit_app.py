# filename: streamtlit_app.py
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, OneHotEncoder
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, root_mean_squared_error, mean_squared_error
from sklearn.ensemble import RandomForestRegressor
from sqlalchemy import create_engine
import streamlit as st
import pickle 
import os
import sys
import importlib

st.set_page_config(
    page_title="Dynamic Pricing Model",
    page_icon="📊")
    
DB_URL = st.secrets["neon"]["url"]
engine = create_engine(DB_URL)

@st.cache_data
def load_data():
    query = """
    SELECT
        order_purchase_timestamp,
        product_id,
        product_category_name,
        customer_state,
        order_id,
        seller_id,
        price
    FROM public.datamart;
    """
    df = pd.read_sql(query, engine)
    return df

# @st.cache_data
# def load_data():
#     with open("data/df.pkl","rb") as file:
#         df = pickle.load(file)
#     return df

df = load_data()
    
@st.cache_data
def calculate_dynamic_pricing(df, group_cols):
    df['order_date'] = pd.to_datetime(df['order_purchase_timestamp']).dt.date

    grouped = df.groupby(group_cols).agg(
        number_of_orders=('order_id', 'count'),
        number_of_sellers=('seller_id', "nunique"),
        historical_cost=('price', "median")
    ).dropna().reset_index()

    # Hitung percentile
    high_demand = np.percentile(grouped['number_of_orders'], 75)
    low_demand = np.percentile(grouped['number_of_orders'], 25)
    high_supply = np.percentile(grouped['number_of_sellers'], 75)
    low_supply = np.percentile(grouped['number_of_sellers'], 25)

    # Demand multiplier: lebih dari 1 jika demand tinggi
    grouped['demand_multiplier'] = np.where(
        grouped['number_of_orders'] > high_demand,
        grouped['number_of_orders'] / high_demand,
        grouped['number_of_orders'] / low_demand
    )
    grouped['demand_multiplier'] = grouped['demand_multiplier'].clip(lower=0.8, upper=1.2)

    # Supply multiplier: lebih dari 1 jika supply rendah
    grouped['supply_multiplier'] = np.where(
        grouped['number_of_sellers'] > high_supply,
        low_supply / grouped['number_of_sellers'],  # supply tinggi = multiplier kecil
        high_supply / grouped['number_of_sellers']  # supply rendah = multiplier besar
)
    grouped['supply_multiplier'] = grouped['supply_multiplier'].clip(lower=0.8, upper=1.2)

    # Harga dinamis
    grouped['adjusted_price'] = grouped['historical_cost'] * (
        grouped['demand_multiplier'] * grouped['supply_multiplier']
    )  
    return grouped

def get_dynamic_pricing(df, group_cols):
    return calculate_dynamic_pricing(df, group_cols)
    
data = get_dynamic_pricing(df, ['product_id','product_category_name', 'customer_state'])

le = LabelEncoder()
le.fit(data['product_id'])

org_label = le.classes_
enc_label = range(len(le.classes_))
product_id_map = dict(zip(org_label, enc_label))

data['product_id_enc'] = data['product_id'].map(product_id_map)

product_category = data['product_category_name']
customer_st = data['customer_state']

unique_info = data.drop_duplicates(subset='product_id')[['product_id', 'product_category_name', 'customer_state']]
product_info = dict(zip(unique_info['product_id'], zip(unique_info['product_category_name'], unique_info['customer_state'])))

df_pi = pd.DataFrame.from_dict(product_info, orient='index', columns = ['product_category_name','customer_state'])
df_pi.reset_index(inplace=True)
df_pi.rename(columns={'index':'product_id'}, inplace=True)


# import hasil product_id_map ke CSV
#df_map = pd.DataFrame(list(product_id_map.items()), columns=['product_id','product_id_encoding'])


#product_id_map
product_category_map = {
        'Agro_Industry_And_Commerce': 239.02153153153154,
        'Air_Conditioning': 193.12535031847133,
        'Art': 107.19664,
        'Arts_And_Craftmanship': 93.46312499999999,
        'Audio': 143.76246913580246,
        'Auto': 122.5136780104712,
        'Baby': 113.52516445470282,
        'Bed_Bath_Table': 131.15992125984252,
        'Books_General_Interest': 111.6870207253886,
        'Books_Imported': 93.25690476190476,
        'Books_Technical': 97.0312972972973,
        'Cds_Dvds_Musicals': 89.85818181818182,
        'Christmas_Supplies': 87.73022727272728,
        'Cine_Photo': 96.32039999999999,
        'Computers': 372.8123076923076,
        'Computers_Accessories': 143.16584360476864,
        'Consoles_Games': 128.69317415730336,
        'Construction_Tools_Construction': 162.26493256262043,
        'Construction_Tools_Lights': 150.27339869281045,
        'Construction_Tools_Safety': 190.50037037037038,
        'Cool_Stuff': 158.11517211328976,
        'Costruction_Tools_Garden': 138.8006,
        'Costruction_Tools_Tools': 122.91597222222224,
        'Diapers_And_Hygiene': 117.79666666666668,
        'Drinks': 96.81435555555555,
        'Dvds_Blu_Ray': 92.48772727272727,
        'Electronics': 74.20153387533874,
        'Fashio_Female_Clothing': 104.13740740740741,
        'Fashion_Bags_Accessories': 88.95949039881832,
        'Fashion_Childrens_Clothes': 94.505,
        'Fashion_Male_Clothing': 122.37438775510205,
        'Fashion_Shoes': 108.07952879581151,
        'Fashion_Sport': 107.37076923076924,
        'Fashion_Underwear_Beach': 89.8880412371134,
        'Fixed_Telephony': 134.28670967741934,
        'Flowers': 67.81227272727273,
        'Food': 86.62140186915889,
        'Food_Drink': 93.41389743589743,
        'Furniture_Bedroom': 107.33099999999999,
        'Furniture_Decor': 134.64923434856175,
        'Furniture_Living_Room': 139.56748691099477,
        'Furniture_Mattress_And_Upholstery': 174.99666666666667,
        'Garden_Tools': 138.54620881155128,
        'Health_Beauty': 138.93024947690327,
        'Home_Appliances': 93.16306640625,
        'Home_Appliances_2': 247.02578125,
        'Home_Comfort_2': 63.99117647058823,
        'Home_Confort': 175.11205323193917,
        'Home_Construction': 159.90168674698796,
        'Housewares': 108.5887441740031,
        'Industry_Commerce_And_Business': 182.48013157894738,
        'Kitchen_Dining_Laundry_Garden_Furniture': 126.37486238532111,
        'La_Cuisine': 230.185,
        'Luggage_Accessories': 115.49466386554622,
        'Market_Place': 112.79020942408377,
        'Music': 144.3904,
        'Musical_Instruments': 161.79696319018404,
        'Office_Furniture': 195.81420560747662,
        'Party_Supplies': 100.67730769230769,
        'Perfumery': 137.81338301716352,
        'Pet_Shop': 131.35940783986655,
        'Security_And_Services': 115.45,
        'Signaling_And_Security': 133.11123595505617,
        'Small_Appliances': 158.59928767123287,
        'Small_Appliances_Home_Oven_And_Coffee': 106.61157894736841,
        'Sports_Leisure': 129.3060853681984,
        'Stationery': 111.2574074074074,
        'Tablets_Printing_Image': 110.0141935483871,
        'Telephony': 80.41140955631398,
        'Toys': 129.28465544244324,
        'Watches_Gifts': 183.53816893878644
    }

    # product_id_map ke kolom baru
data["product_category_enc"] = data["product_category_name"].map(product_category_map)

    # Cek hasil
    #print(data[["product_category_name", "product_category_enc"]].head())

    #Converting time of booking to a numerical feature
state_map = {
        "Andhra Pradesh": 0.685111306,
        "Gujarat": 0.130986103,
        "Chhattisgarh": 0.048393077,
        "Haryana": 0.030343928,
        "Delhi": 0.022854346,
        "Karnataka": 0.021386092,
        "Jammu & Kashmir": 0.010826523,
        "Madhya Pradesh": 0.008690881,
        "West Bengal": 0.008587065,
        "Arunachal Pradesh": 0.007489581,
        "Rajasthan": 0.005413262,
        "Maharashtra": 0.00504249,
        "Tamil Nadu": 0.004122977,
        "Himachal Pradesh": 0.004019161,
        "Kerala": 0.002476753,
        "Orissa": 0.001631394,
        "Uttar Pradesh": 0.001542409,
        "Punjab": 0.000548742,
        "Uttaranchal": 0.000533911
    }

    # product_id_map ke dataframe
data["customer_state_enc"] = data["customer_state"].map(state_map)

# Cek hasil
#print(data[["customer_state", "customer_state_enc"]].head())
    
@st.cache_resource
def load_model():
    with open("models/randomforest.pkl",'rb') as file:
        loaded = pickle.load(file)
    return loaded

#Define function to get encoding result

def product_category_numeric(product_category_enc):
    product_category_numeric_mapping = product_category_map
    product_category_numeric = product_category_numeric_mapping.get(product_category_enc)
    return product_category_numeric

def state_numeric(customer_state_enc):
    state_numeric_mapping = state_map
    state_numeric = state_numeric_mapping.get(customer_state_enc)
    return state_numeric

def product_id_numeric(product_id_enc):
    product_id_numeric_mapping = product_id_map
    product_id_numeric = product_id_numeric_mapping.get(product_id_enc)
    return product_id_numeric

model = load_model()

def main():
    #making predictions using user input values
    def predict_price(product_id_enc,product_category_enc,customer_state_enc,historical_cost,number_of_orders):
        product_id_numeric_result = product_id_numeric(product_id_enc)
        if product_id_numeric_result is None:
            raise ValueError("Invalid vehicle type")

        product_category_numeric_result = product_category_numeric(product_category_enc)
        if product_category_numeric_result is None:
            raise ValueError("Invalid time of booking")

        customer_state_numeric_result = state_numeric(customer_state_enc)
        if customer_state_numeric_result is None:
            raise ValueError("Invalid time of booking")

        X_pred = pd.DataFrame([[
            product_id_numeric_result,
            product_category_numeric_result,
            customer_state_numeric_result,
            historical_cost,
            number_of_orders
            ]], columns=['product_id_enc', 'product_category_enc', 'customer_state_enc', 'historical_cost', 'number_of_orders'])

    # Lakukan prediksi
        predicted_price = model.predict(X_pred)[0]
        return predicted_price

    st.title("Dynamic Pricing Model")

    if "final_data" not in st.session_state:
        st.session_state.final_data = pd.DataFrame(columns=['product_id_enc','product_category_enc','customer_state_enc','historical_cost','number_of_orders'])

    product_category_enc = st.selectbox("Category", options=list(product_category_map.keys()))
    filtered_products = df_pi[df_pi['product_category_name']==product_category_enc]['product_id'].unique().tolist()

    with st.form("Input Your Information"):

        product_id_enc  = st.selectbox("Product Id", options=filtered_products, key='product_id')
        customer_state_enc = st.selectbox("State", options=list(state_map.keys()))
        historical_cost = st.number_input("Price", min_value=1)
        number_of_orders= st.number_input("Number of Orders", min_value=1)
        submitted = st.form_submit_button("Predicted Price")

    if submitted:
       predicted_price = predict_price(product_id_enc,product_category_enc,customer_state_enc,historical_cost,number_of_orders)
       price = predicted_price.item()  # atau predicted_price[0] jika pasti 1D

       data_submitted = pd.DataFrame({
           'product_id_enc':[product_id_enc],
           'product_category_enc':[product_category_enc],
           'customer_state_enc':[customer_state_enc],
           'historical_cost':[historical_cost],
           'number_of_orders':[number_of_orders]})
       
       st.session_state.final_data = pd.concat([st.session_state.final_data, data_submitted], ignore_index=True)
       st.success(f"Predicted price for {product_id_enc} in {product_category_enc} for customer who live in {customer_state_enc} are: Rp {price:,.0f}")
    
    st.subheader("Dynamic Pricing Data")
    st.dataframe(st.session_state.final_data)

if __name__ == "__main__":
    main()

