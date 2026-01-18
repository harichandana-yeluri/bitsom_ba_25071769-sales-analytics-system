from utils.file_handler import read_sales_data, parse_transactions, validate_and_filter
from utils.data_processor import (
    calculate_total_revenue,
    region_wise_sales,
    top_selling_products,
    customer_analysis,
    SalesDateAnalyzer,
    low_performing_products
)


def main():
    """
    Main execution function (up to validation & filtering + Part 2 analysis)
    """
    try:
        print("=" * 40)
        print("SALES ANALYTICS SYSTEM")
        print("=" * 40)
        print()

        # Step 1: Read sales data
        print("[1/10] Reading sales data...")
        raw_lines = read_sales_data("data/sales_data.txt")
        print(f"✓ Successfully read {len(raw_lines)} transactions\n")

        # Step 2: Parse and clean transactions
        print("[2/10] Parsing and cleaning data...")
        transactions = parse_transactions(raw_lines)
        print(f"✓ Parsed {len(transactions)} records\n")

        # Step 3: Display filter options
        print("[3/10] Filter Options Available:")

        # Preview validation to show regions and amount range
        _valid_preview, _invalid_preview, _ = validate_and_filter(transactions)

        print()
        choice = input("Do you want to filter data? (y/n): ").strip().lower()
        print()

        region = None
        min_amount = None
        max_amount = None

        if choice == "y":
            region = input("Enter region to filter (or press Enter to skip): ").strip()
            region = region if region else None

            try:
                min_amt_input = input("Enter minimum transaction amount (or press Enter to skip): ").strip()
                min_amount = float(min_amt_input) if min_amt_input else None

                max_amt_input = input("Enter maximum transaction amount (or press Enter to skip): ").strip()
                max_amount = float(max_amt_input) if max_amt_input else None
            except ValueError:
                print("⚠ Invalid amount entered. Skipping amount filters.")
                min_amount = None
                max_amount = None

        # Step 4: Validate and apply filters
        print("[4/10] Validating transactions...")
        valid_transactions, invalid_count, summary = validate_and_filter(
            transactions,
            region=region,
            min_amount=min_amount,
            max_amount=max_amount
        )

        print("✓ Validation Summary")
        print(f"  Total input records        : {summary['total_input']}")
        print(f"  Invalid records (cleaning): {summary['invalid']}")
        print(f"  Filtered by region        : {summary['filtered_by_region']}")
        print(f"  Filtered by amount        : {summary['filtered_by_amount']}")
        print(f"  Final valid transactions  : {summary['final_count']}\n")




        # Step 8: Perform all data analyses (Part 2)
        print("[8/10] Performing sales data analysis...")

        total_revenue = calculate_total_revenue(valid_transactions)
        print(f"✓ Total Revenue Calculated: ₹{round(total_revenue, 2)}")

        region_sales = region_wise_sales(valid_transactions)
        print("✓ Region-wise sales analysis complete")

        top_products = top_selling_products(valid_transactions)
        print("✓ Top selling products identified")

        customer_stats = customer_analysis(valid_transactions)
        print("✓ Customer purchase analysis complete")

        daily_trend = SalesDateAnalyzer(valid_transactions).daily_sales_trend()
        print("✓ Daily sales trend calculated")

        peak_date, peak_revenue, peak_count = SalesDateAnalyzer(valid_transactions).find_peak_sales_day()
        print(
            f"✓ Peak Sales Day: {peak_date} | "
            f"Revenue: ₹{peak_revenue} | "
            f"Transactions: {peak_count}"
        )

        low_products = low_performing_products(valid_transactions)
        print("✓ Low performing products identified\n")

        print("[10/10] Process Complete!")
        print("=" * 40)

    except FileNotFoundError as e:
        print("❌ File Error:", e)

    except Exception as e:
        print("❌ Unexpected Error Occurred:")
        print(str(e))


if __name__ == "__main__":
    main()
