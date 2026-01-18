# Task 2.1: Sales summaary Calculator

def calculate_total_revenue(transactions):
    """
    Calculates total revenue from all transactions

    Returns: float (total revenue)
    """
    total_revenue = 0.0

    for txn in transactions:
        try:
            quantity = txn.get("Quantity", 0)
            unit_price = txn.get("UnitPrice", 0.0)

            total_revenue += quantity * unit_price

        except (TypeError, ValueError):
            # Skip transactions with unexpected data types
            continue

    return round(total_revenue, 2)


def region_wise_sales(transactions):
    """
    Analyzes sales by region

    Returns: dictionary with region statistics
    """
    from utils.data_processor import calculate_total_revenue

    region_groups = {}

    # Group transactions by region
    for txn in transactions:
        region = txn["Region"]
        region_groups.setdefault(region, []).append(txn)

    # Calculate overall revenue once
    total_revenue_overall = calculate_total_revenue(transactions)

    region_stats = {}

    for region, txns in region_groups.items():
        region_revenue = calculate_total_revenue(txns)

        percentage = (
            (region_revenue / total_revenue_overall) * 100
            if total_revenue_overall > 0 else 0.0
        )

        region_stats[region] = {
            "total_sales": round(region_revenue, 2),
            "transaction_count": len(txns),
            "percentage": round(percentage, 2)
        }

    # Sort by total_sales descending
    sorted_region_stats = dict(
        sorted(
            region_stats.items(),
            key=lambda item: item[1]["total_sales"],
            reverse=True
        )
    )

    return sorted_region_stats

def top_selling_products(transactions, n=5):
    """
    Finds top n products by total quantity sold

    Returns: list of tuples
    """

    product_summary = {}

    for txn in transactions:
        product = txn["ProductName"]
        qty = txn["Quantity"]
        amount = qty * txn["UnitPrice"]

        summary = product_summary.setdefault(
            product, {"total_quantity": 0, "total_revenue": 0.0}
        )

        summary["total_quantity"] += qty
        summary["total_revenue"] += amount

    return sorted(
        [
            (product, data["total_quantity"], round(data["total_revenue"], 2))
            for product, data in product_summary.items()
        ],
        key=lambda x: x[1],
        reverse=True
    )[:n]

def customer_analysis(transactions):
    """
    Analyzes customer purchase patterns

    Returns: dictionary of customer statistics
    """

    customer_stats = {}

    for txn in transactions:
        cust = txn["CustomerID"]
        amount = txn["Quantity"] * txn["UnitPrice"]

        stats = customer_stats.setdefault(
            cust,
            {
                "total_spent": 0.0,
                "purchase_count": 0,
                "products_bought": set()
            }
        )

        stats["total_spent"] += amount
        stats["purchase_count"] += 1
        stats["products_bought"].add(txn["ProductName"])

    return dict(
        sorted(
            (
                cust,
                {
                    "total_spent": round(data["total_spent"], 2),
                    "purchase_count": data["purchase_count"],
                    "avg_order_value": round(
                        data["total_spent"] / data["purchase_count"], 2
                    ),
                    "products_bought": sorted(data["products_bought"])
                }
            )
            for cust, data in customer_stats.items()
        ),
        key=lambda item: item[1]["total_spent"],
        reverse=True
    )

# Task 2.2: Date-based Analysis

class SalesDateAnalyzer:
    """
    Performs date-based sales analysis using reusable aggregation logic
    """

    def __init__(self, transactions):
        self.transactions = transactions
        self._daily_data = None

    def _aggregate_by_date(self):
        """
        Analyzes sales trends by date

        Returns: dictionary sorted by date
        """
        if self._daily_data is not None:
            return self._daily_data

        daily_stats = {}

        for txn in self.transactions:
            date = txn["Date"]
            amount = txn["Quantity"] * txn["UnitPrice"]

            stats = daily_stats.setdefault(
                date,
                {
                    "revenue": 0.0,
                    "transaction_count": 0,
                    "unique_customers": set()
                }
            )

            stats["revenue"] += amount
            stats["transaction_count"] += 1
            stats["unique_customers"].add(txn["CustomerID"])

        self._daily_data = daily_stats
        return daily_stats

    def daily_sales_trend(self):
        """
        Analyzes sales trends by date

        Returns: dictionary sorted by date
        """
        aggregated = self._aggregate_by_date()

        return dict(
            sorted(
                (
                    date,
                    {
                        "revenue": round(data["revenue"], 2),
                        "transaction_count": data["transaction_count"],
                        "unique_customers": len(data["unique_customers"])
                    }
                )
                for date, data in aggregated.items()
            )
        )

    def find_peak_sales_day(self):
        """
        Identifies the date with highest revenue

        Returns: tuple (date, revenue, transaction_count)
        """
        aggregated = self._aggregate_by_date()

        peak_date, peak_data = max(
            aggregated.items(),
            key=lambda item: item[1]["revenue"]
        )

        return (
            peak_date,
            round(peak_data["revenue"], 2),
            peak_data["transaction_count"]
        )

def low_performing_products(transactions, threshold=10):
    """
    Identifies products with low sales

    Returns: list of tuples
    """

    product_stats = {}

    # Aggregate quantity and revenue by product
    for txn in transactions:
        product = txn["ProductName"]
        quantity = txn["Quantity"]
        revenue = quantity * txn["UnitPrice"]

        if product not in product_stats:
            product_stats[product] = {
                "total_quantity": 0,
                "total_revenue": 0.0
            }

        product_stats[product]["total_quantity"] += quantity
        product_stats[product]["total_revenue"] += revenue

    # Filter products below threshold and prepare output
    low_performers = [
        (
            product,
            data["total_quantity"],
            round(data["total_revenue"], 2)
        )
        for product, data in product_stats.items()
        if data["total_quantity"] < threshold
    ]

    # Sort by total quantity ascending
    low_performers.sort(key=lambda x: x[1])

    return low_performers
