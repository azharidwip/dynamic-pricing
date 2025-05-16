# feature_engineering.py
import pandas as pd
import numpy as np
from scipy import stats
import os

def calculate_dynamic_pricing(df, group_cols):
    # Pastikan tanggal sudah dalam format date
    #df['order_date'] = pd.to_datetime(df['order_purchase_timestamp']).dt.date

    # Grouping berdasarkan kolom yang ditentukan
    grouped = df.groupby(group_cols).agg(
        number_of_orders=('order_id', 'count'),
        number_of_sellers=('seller_id', 'nunique'),
        historical_cost=('price', 'mean')).dropna().reset_index()

    # Percentile untuk multiplier
    high_demand = np.percentile(grouped['number_of_orders'], 75)
    low_demand = np.percentile(grouped['number_of_orders'], 25)

    high_supply = np.percentile(grouped['number_of_sellers'], 75)
    low_supply = np.percentile(grouped['number_of_sellers'], 25)

    # Demand multiplier
    grouped['demand_multiplier'] = np.where(
        grouped['number_of_orders'] > high_demand,
        grouped['number_of_orders'] / high_demand,
        grouped['number_of_orders'] / low_demand)

    # Supply multiplier
    grouped['supply_multiplier'] = np.where(
        grouped['number_of_sellers'] > high_supply, 
        low_supply/ grouped['number_of_sellers'],
        high_supply / grouped['number_of_sellers'])

    # Threshold
    demand_threshold_low = 0.5
    supply_threshold_high = 0.5

    # Adjusted price
    cb_mlp = (
        np.maximum(grouped['demand_multiplier'], demand_threshold_low) *
        np.maximum(grouped['supply_multiplier'], supply_threshold_high))
    
    # Batasi multiplier agar tidak lebih dari 1.3 (30% kenaikan maksimum)
    max_increase = 1.15
    final_multiplier = np.minimum(cb_mlp, max_increase)

    # Hitung harga akhir dengan batas atas
    grouped['adjusted_price'] = grouped['historical_cost'] * final_multiplier

    return grouped



def get_dynamic_pricing(df, group_cols):
    return calculate_dynamic_pricing(df, group_cols)

def feature_engineering():
    """Performs feature engineering on the e-commerce transaction data."""
    os.makedirs('feature', exist_ok=True)
    df = pd.read_csv("data/e-commerce_transaction.csv")
    df_processed = calculate_dynamic_pricing(df.copy(), ['product_id', 'product_category_name', 'customer_state'])
    return df_processed

def get_dataframe():
    """Returns the processed dataframe."""
    return feature_engineering()

if __name__ == "__main__":
    df = pd.read_csv("data/e-commerce_transaction.csv") # Baca DataFrame di sini
    data = get_dynamic_pricing(df, ['product_id','product_category_name', 'customer_state'])
    print("Dynamic Pricing Data:")
    print(data.head())

    processed_df = feature_engineering()
    print("\nFeature engineering completed. Processed DataFrame:")
    print(processed_df.head())