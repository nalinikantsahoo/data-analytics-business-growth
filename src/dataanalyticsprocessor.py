import os

import numpy as np
import pandas as pd

from src.config import DEMAND_FILE_PATH, INVENTORY_FILE_PATH, PRODUCT_MASTER_FILE_PATH, SALES_FILE_PATH, \
    OUTPUT_FILE_PATH, log


class DataInterpreter:

    def __init__(self):
        # Initialize the dataframes when the class is instantiated
        self.demand_df = pd.read_csv(
            DEMAND_FILE_PATH)
        self.inventory_df = pd.read_csv(
            INVENTORY_FILE_PATH)
        self.product_master_df = pd.read_csv(
            PRODUCT_MASTER_FILE_PATH)
        self.sales_df = pd.read_csv(
           SALES_FILE_PATH)

        # log.debug column names for reference
        log.debug(self.demand_df.columns)
        log.debug(self.inventory_df)
        log.debug(self.product_master_df)
        log.debug(self.sales_df)

    def clean_numeric_column(self, df, columns):
        """ Clean non-numeric characters and convert columns to numeric types. """
        for col in columns:
            if col in df.columns:
                df[col] = df[col].replace({',': ''}, regex=True)
                df[col].replace({' ': ''}, regex=True)# Remove commas
                df[col] = pd.to_numeric(df[col], errors='coerce')  # Convert to numeric, coercing errors to NaN
            else:
                log.debug(f"Warning: Column '{col}' not found in the dataframe")

    def calculate_kpi_trends(self):
        # Clean and convert columns to integers
        self.clean_numeric_column(self.sales_df, ['fiscal_week', 'sales_amount', 'sales_quantity'])
        self.sales_df['fiscal_week'] = self.sales_df['fiscal_week'].fillna(0).astype(int)
        self.sales_df['sales_amount'] = self.sales_df['sales_amount'].fillna(0).astype(int)
        self.sales_df['sales_quantity'] = self.sales_df['sales_quantity'].fillna(0).astype(int)

        self.clean_numeric_column(self.demand_df, ['fiscal_week', 'final_demand_amount', 'final_demand_quantity'])
        self.demand_df['fiscal_week'] = self.demand_df['fiscal_week'].fillna(0).astype(int)
        self.demand_df['final_demand_amount'] = self.demand_df['final_demand_amount'].fillna(0).astype(int)
        self.demand_df['final_demand_quantity'] = self.demand_df['final_demand_quantity'].fillna(0).astype(int)

        self.clean_numeric_column(self.inventory_df, ['fiscal_week', 'inventory_amount', 'inventory_quantity'])
        self.inventory_df['fiscal_week'] = self.inventory_df['fiscal_week'].fillna(0).astype(int)
        self.inventory_df['inventory_amount'] = self.inventory_df['inventory_amount'].fillna(0).astype(int)
        self.inventory_df['inventory_quantity'] = self.inventory_df['inventory_quantity'].fillna(0).astype(int)

        # Sales trend by fiscal week
        sales_trend = self.sales_df.groupby('fiscal_week').agg(
            {'sales_amount': 'sum', 'sales_quantity': 'sum'}).reset_index()

        # Customer demand trend by fiscal week
        demand_trend = self.demand_df.groupby('fiscal_week').agg(
            {'final_demand_amount': 'sum', 'final_demand_quantity': 'sum'}).reset_index()

        # Inventory trend by fiscal week
        inventory_trend = self.inventory_df.groupby('fiscal_week').agg(
            {'inventory_amount': 'sum', 'inventory_quantity': 'sum'}).reset_index()

        return sales_trend, demand_trend, inventory_trend

    def calculate_forecast_accuracy(self):
        columns_to_clean = [
            'final_demand_amount', 'demand_1_weeks_before_amount', 'demand_4_weeks_before_amount',
            'final_demand_quantity', 'demand_1_weeks_before_quantity', 'demand_4_weeks_before_quantity'
        ]


        self.demand_df.fillna(0, inplace=True)
        self.clean_numeric_column(self.demand_df, columns_to_clean)
        grouped_df = self.demand_df.groupby(['customer_name', 'fiscal_week']).agg(
            final_demand_quantity=('final_demand_quantity', 'sum'),
            demand_4_weeks_before_quantity=('demand_4_weeks_before_quantity', 'sum'),
            demand_1_weeks_before_quantity=('demand_1_weeks_before_quantity', 'sum')
        ).reset_index()

        grouped_df['forecast_accuracy_4_weeks'] = 100 * (
                1 - abs(grouped_df['demand_4_weeks_before_quantity'] - grouped_df['final_demand_quantity']) /
                grouped_df['final_demand_quantity'])
        grouped_df['forecast_accuracy_1_week'] = 100 * (
                1 - abs(grouped_df['demand_1_weeks_before_quantity'] - grouped_df['final_demand_quantity']) /
                grouped_df['final_demand_quantity'])

        return grouped_df[['fiscal_week', 'customer_name', 'forecast_accuracy_4_weeks', 'forecast_accuracy_1_week']]

    def calculate_ontime_shipments(self):
        columns_to_clean = ['ontime_delivery', 'no_of_delivery']

        self.clean_numeric_column(self.sales_df, columns_to_clean)
        self.sales_df['ontime_delivery'].fillna(0, inplace=True)
        self.sales_df['no_of_delivery'].fillna(0, inplace=True)

        self.sales_df['ontime_average'] = self.sales_df['ontime_delivery'] / self.sales_df['no_of_delivery']

        ontime_shipments = self.sales_df.groupby(['customer_name', 'plant']).agg(
            {'ontime_average': 'mean'}).reset_index()

        return ontime_shipments

    def identify_excess_inventory(self):
        merged_df = pd.merge(self.inventory_df, self.demand_df,
                             left_on=['region', 'product', 'plant', 'plant_country', 'fiscal_week'],
                             right_on=['region', 'product', 'plant_code', 'plant_country', 'fiscal_week'],
                             how='left')

        columns_to_clean = ['inventory_amount', 'future_demand_amount']

        self.clean_numeric_column(merged_df, columns_to_clean)

        merged_df['excess_inventory'] = merged_df['inventory_amount'] - merged_df['future_demand_amount']

        excess_inventory = merged_df[merged_df['excess_inventory'] > 0][['product', 'plant', 'excess_inventory']]

        return excess_inventory

    def calculate_average_week_of_stock(self):
        # Merge inventory and demand data
        merged_df = pd.merge(self.inventory_df, self.demand_df,
                             left_on=['region', 'product', 'plant', 'fiscal_week'],
                             right_on=['region', 'product', 'plant_code', 'fiscal_week'],
                             how='left')

        # Define columns to clean
        columns_to_clean = ['inventory_amount', 'future_demand_amount']

        # Clean numeric columns
        self.clean_numeric_column(merged_df, columns_to_clean)

        # Handle zero or missing values in 'future_demand_amount'
        merged_df['future_demand_amount'].replace(0, np.nan, inplace=True)

        # Calculate weeks of stock
        merged_df['weeks_of_stock'] = np.where(
            merged_df['future_demand_amount'].isna(),  # If future_demand_amount is NaN
            np.nan,  # Assign NaN instead of inf
            merged_df['inventory_amount'] / merged_df['future_demand_amount']  # Perform the division
        )

        # Group by plant and calculate average weeks of stock
        avg_weeks_of_stock = merged_df.groupby('plant').agg({'weeks_of_stock': 'mean'}).reset_index()

        # Handle plants with all NaN values
        avg_weeks_of_stock = avg_weeks_of_stock.replace({np.nan: 0})

        return avg_weeks_of_stock

    def predict_potential_sales(self, forecast_accuracy_df):
        self.demand_df = self.demand_df.drop_duplicates(subset='customer_name')
        forecast_accuracy_df = forecast_accuracy_df.drop_duplicates(subset='customer_name')

        merged_df = pd.merge(
            self.demand_df[['customer_name', 'future_demand_amount']],
            forecast_accuracy_df[['customer_name', 'forecast_accuracy_1_week']],
            on='customer_name', how='left'
        )

        merged_df['potential_sales'] = merged_df['future_demand_amount'] * merged_df['forecast_accuracy_1_week']

        potential_sales = merged_df.groupby('customer_name').agg({'potential_sales': 'sum'}).reset_index()

        return potential_sales

    def save_results_to_csv(self):
        # Save all calculated trends and metrics to CSV files
        sales_trend, demand_trend, inventory_trend = self.calculate_kpi_trends()
        forecast_accuracy = self.calculate_forecast_accuracy()
        ontime_shipments = self.calculate_ontime_shipments()
        excess_inventory = self.identify_excess_inventory()
        avg_weeks_of_stock = self.calculate_average_week_of_stock()
        potential_sales = self.predict_potential_sales(forecast_accuracy)

        if not os.path.exists(OUTPUT_FILE_PATH):
            os.makedirs(OUTPUT_FILE_PATH, exist_ok=True)
            log.debug(f"Created output directory: {OUTPUT_FILE_PATH}")
        else:
            log.debug(f"Output directory already exists: {OUTPUT_FILE_PATH}")

        sales_trend.to_csv(OUTPUT_FILE_PATH+'sales_trend.csv', sep=chr(29),index=False)
        demand_trend.to_csv(OUTPUT_FILE_PATH+'demand_trend.csv',sep=chr(29), index=False)
        inventory_trend.to_csv(OUTPUT_FILE_PATH+'inventory_trend.csv',sep=chr(29), index=False)
        forecast_accuracy.to_csv(OUTPUT_FILE_PATH+'forecast_accuracy.csv',sep=chr(29), index=False)
        ontime_shipments.to_csv(OUTPUT_FILE_PATH+'ontime_shipments.csv',sep=chr(29), index=False)
        excess_inventory.to_csv(OUTPUT_FILE_PATH+'excess_inventory.csv',sep=chr(29), index=False)
        avg_weeks_of_stock.to_csv(OUTPUT_FILE_PATH+'avg_weeks_of_stock.csv',sep=chr(29), index=False)
        potential_sales.to_csv(OUTPUT_FILE_PATH+'potential_sales.csv', sep=chr(29),index=False)



