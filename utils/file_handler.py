def read_sales_data(filename):
    """
    Reads sales data from file handling encoding issues

    Returns: list of raw lines (strings)

    Expected Output Format:
    ['T001|2024-12-01|P101|Laptop|2|45000|C001|North', ...]

    Requirements:
    - Use 'with' statement
    - Handle different encodings (try 'utf-8', 'latin-1', 'cp1252')
    - Handle FileNotFoundError with appropriate error message
    - Skip the header row
    - Remove empty lines
    """
    encodings = ["utf-8", "latin-1", "cp1252"]

    for encoding in encodings:
        try:
            with open(filename, "r", encoding=encoding) as file:
                lines = file.readlines()

            # Skip header and remove empty lines
            data_lines = [
                line.strip()
                for line in lines[1:]
                if line.strip()
            ]

            return data_lines

        except UnicodeDecodeError:
            # Try next encoding
            continue

        except FileNotFoundError:
            raise FileNotFoundError(
                f"Error: The file '{filename}' was not found."
            )

    # If all encodings fail
    raise UnicodeDecodeError(
        "read_sales_data",
        b"",
        0,
        1,
        "Unable to decode file using supported encodings."
    )

def parse_transactions(raw_lines):
    """
    Parses raw lines into clean list of dictionaries

    Returns: list of dictionaries with keys:
    ['TransactionID', 'Date', 'ProductID', 'ProductName',
     'Quantity', 'UnitPrice', 'CustomerID', 'Region']
    """
    parsed_records = []

    for line in raw_lines:
        parts = line.split("|")

        # Skip rows with incorrect number of fields
        if len(parts) != 8:
            continue

        (
            transaction_id,
            date,
            product_id,
            product_name,
            quantity,
            unit_price,
            customer_id,
            region
        ) = parts

        try:
            # Clean product name (remove commas)
            product_name = product_name.replace(",", " ").strip()

            # Clean and convert numeric fields
            quantity = int(quantity.replace(",", ""))
            unit_price = float(unit_price.replace(",", ""))

            record = {
                "TransactionID": transaction_id.strip(),
                "Date": date.strip(),
                "ProductID": product_id.strip(),
                "ProductName": product_name,
                "Quantity": quantity,
                "UnitPrice": unit_price,
                "CustomerID": customer_id.strip(),
                "Region": region.strip()
            }

            parsed_records.append(record)

        except ValueError:
            # Skip records with unconvertible numeric values
            continue

    return parsed_records


def validate_and_filter(transactions, region=None, min_amount=None, max_amount=None):
    """
    Validates transactions and applies optional filters
    """
    total_input = len(transactions)
    invalid_count = 0
    valid_transactions = []

    required_fields = {
        "TransactionID", "Date", "ProductID", "ProductName",
        "Quantity", "UnitPrice", "CustomerID", "Region"
    }

    # Collect region and amount info for display
    available_regions = set()
    amounts = []

    for txn in transactions:
        # Check required fields
        if not required_fields.issubset(txn.keys()):
            invalid_count += 1
            continue

        # Validate ID formats
        if not (
            txn["TransactionID"].startswith("T")
            and txn["ProductID"].startswith("P")
            and txn["CustomerID"].startswith("C")
        ):
            invalid_count += 1
            continue

        # Validate numeric fields
        if txn["Quantity"] <= 0 or txn["UnitPrice"] <= 0:
            invalid_count += 1
            continue

        amount = txn["Quantity"] * txn["UnitPrice"]

        available_regions.add(txn["Region"])
        amounts.append(amount)

        txn["TransactionAmount"] = amount
        valid_transactions.append(txn)

    # Display available regions and amount range
    if available_regions:
        print(f"Available Regions: {sorted(available_regions)}")

    if amounts:
        print(f"Transaction Amount Range: {min(amounts)} to {max(amounts)}")

    # Apply region filter
    filtered_by_region = 0
    if region:
        before = len(valid_transactions)
        valid_transactions = [
            txn for txn in valid_transactions
            if txn["Region"] == region
        ]
        filtered_by_region = before - len(valid_transactions)
        print(f"Records after region filter ({region}): {len(valid_transactions)}")

    # Apply amount filter
    filtered_by_amount = 0
    if min_amount is not None or max_amount is not None:
        before = len(valid_transactions)
        valid_transactions = [
            txn for txn in valid_transactions
            if (
                (min_amount is None or txn["TransactionAmount"] >= min_amount)
                and (max_amount is None or txn["TransactionAmount"] <= max_amount)
            )
        ]
        filtered_by_amount = before - len(valid_transactions)
        print(f"Records after amount filter: {len(valid_transactions)}")

    filter_summary = {
        "total_input": total_input,
        "invalid": invalid_count,
        "filtered_by_region": filtered_by_region,
        "filtered_by_amount": filtered_by_amount,
        "final_count": len(valid_transactions)
    }

    return valid_transactions, invalid_count, filter_summary
