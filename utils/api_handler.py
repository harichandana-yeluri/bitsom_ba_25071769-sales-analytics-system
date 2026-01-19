import requests


def fetch_all_products():
    """
    Fetches all products from DummyJSON API

    Returns: list of product dictionaries
    """
    url = "https://dummyjson.com/products"
    params = {
        "limit": 100   # fetch maximum allowed products in one call
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # raises HTTPError for 4xx/5xx

        data = response.json()
        products = data.get("products", [])

        cleaned_products = []

        for product in products:
            cleaned_products.append({
                "id": product.get("id"),
                "title": product.get("title"),
                "category": product.get("category"),
                "brand": product.get("brand", "N/A"),  # brand may be missing
                "price": product.get("price"),
                "rating": product.get("rating")
            })

        print(f"✓ Successfully fetched {len(cleaned_products)} products\n")
        return cleaned_products

    except requests.exceptions.RequestException as e:
        print("❌ Failed to fetch products from API")
        print(f"Reason: {e}")
        return []


def create_product_mapping(api_products):
    """
    Creates a mapping of product IDs to product info

    Parameters: api_products from fetch_all_products()

    Returns: dictionary mapping product IDs to info
    """
    product_mapping = {}

    for product in api_products:
        product_id = product.get("id")

        # Skip records without valid ID
        if product_id is None:
            continue

        product_mapping[product_id] = {
            "title": product.get("title"),
            "category": product.get("category"),
            "brand": product.get("brand", "N/A"),
            "rating": product.get("rating")
        }

    return product_mapping

def enrich_sales_data(transactions, product_mapping):
    """
    Enriches transaction data with API product information
    """
    enriched_transactions = []

    for txn in transactions:
        enriched_txn = txn.copy()

        # Default enrichment values
        enriched_txn["API_Category"] = None
        enriched_txn["API_Brand"] = None
        enriched_txn["API_Rating"] = None
        enriched_txn["API_Match"] = False

        try:
            product_id_str = txn.get("ProductID", "")

            # Extract numeric part: P101 -> 101
            numeric_id = int("".join(filter(str.isdigit, product_id_str)))

            api_product = product_mapping.get(numeric_id)

            if api_product:
                enriched_txn["API_Category"] = api_product.get("category")
                enriched_txn["API_Brand"] = api_product.get("brand")
                enriched_txn["API_Rating"] = api_product.get("rating")
                enriched_txn["API_Match"] = True

        except Exception:
            # Any parsing / mapping issue → enrichment fails gracefully
            enriched_txn["API_Match"] = False

        enriched_transactions.append(enriched_txn)

    return enriched_transactions


def save_enriched_data(enriched_transactions, filename="data/enriched_sales_data.txt"):
    """
    Saves enriched transactions back to file
    """
    header = [
        "TransactionID", "Date", "ProductID", "ProductName",
        "Quantity", "UnitPrice", "CustomerID", "Region",
        "API_Category", "API_Brand", "API_Rating", "API_Match"
    ]

    try:
        with open(filename, "w", encoding="utf-8") as file:
            # Write header
            file.write("|".join(header) + "\n")

            for txn in enriched_transactions:
                row = [
                    str(txn.get("TransactionID", "")),
                    str(txn.get("Date", "")),
                    str(txn.get("ProductID", "")),
                    str(txn.get("ProductName", "")),
                    str(txn.get("Quantity", "")),
                    str(txn.get("UnitPrice", "")),
                    str(txn.get("CustomerID", "")),
                    str(txn.get("Region", "")),
                    str(txn.get("API_Category", "")),
                    str(txn.get("API_Brand", "")),
                    str(txn.get("API_Rating", "")),
                    str(txn.get("API_Match", "False"))
                ]

                file.write("|".join(row) + "\n")

        print(f"✓ Enriched data saved to: {filename}\n")

    except Exception as e:
        print("❌ Failed to save enriched data")
        print(f"Reason: {e}")

