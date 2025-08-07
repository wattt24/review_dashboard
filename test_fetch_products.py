# test_fetch_products.py
from services.woocommerce_service import fetch_products

products = fetch_products()
print(products)
