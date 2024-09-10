# config.py
import os

from logs.log import setup_logger

log = setup_logger()
# Input File paths
DEMAND_FILE_PATH = os.environ.get("DEMAND_FILE_PATH") or r"src\configs\demand.csv"
INVENTORY_FILE_PATH = os.environ.get("INVENTORY_FILE_PATH") or r"src\configs\inventory.csv"
PRODUCT_MASTER_FILE_PATH = os.environ.get("PRODUCT_MASTER_FILE_PATH") or r"src\configs\product_master.csv"
SALES_FILE_PATH = os.environ.get("SALES_FILE_PATH") or r"src\configs\sales.csv"

#Output file paths
OUTPUT_FILE_PATH= os.environ.get("OUTPUT_FILE_PATH") or r"target/"