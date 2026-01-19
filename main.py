import os
from datetime import datetime

from utils.file_handler import (
    read_sales_data,
    parse_transactions,
    validate_and_filter
)
from utils.data_processor import (
    calculate_total_revenue,
    region_wise_sales,
    top_selling_products,
    customer_analysis,
    SalesDateAnalyzer,
    low_performing_products
)
from utils.api_handler import (
    fetch_all_products,
    create_product_mapping,
    enrich_sales_data,
    save_enriched_data
)

from datetime import datetime


def generate_sales_report(
    *,
    valid_transactions,
    total_revenue,
    region_sales,
    top_products,
    customer_stats,
    daily_trend,
    peak_sales_day,
    low_products,
    enriched_transactions,
    output_file="output/sales_report.txt"
):
    """
    Generates a comprehensive formatted text report
    """
    try:
        # -----------------------------
        # PRE-COMPUTED DERIVED METRICS
        # -----------------------------
        total_transactions = len(valid_transactions)
        avg_order_value = (
            total_revenue / total_transactions
            if total_transactions else 0
        )

        dates = [txn["Date"] for txn in valid_transactions]
        date_range = (
            min(dates), max(dates)
        ) if dates else ("N/A", "N/A")

        # API enrichment summary
        enriched_count = sum(
            1 for t in enriched_transactions if t.get("API_Match")
        )
        enrichment_rate = (
            enriched_count / total_transactions * 100
            if total_transactions else 0
        )

        failed_products = sorted({
            t["ProductName"]
            for t in enriched_transactions
            if not t.get("API_Match")
        })

        # Average transaction value per region
        avg_value_per_region = {
            region: (
                data["total_sales"] / data["transaction_count"]
                if data["transaction_count"] else 0
            )
            for region, data in region_sales.items()
        }

        # -----------------------------
        # WRITE REPORT
        # -----------------------------
        with open(output_file, "w", encoding="utf-8") as f:

            # HEADER
            f.write("=" * 44 + "\n")
            f.write("           SALES ANALYTICS REPORT\n")
            f.write(
                f"     Generated: "
                f"{datetime.now():%Y-%m-%d %H:%M:%S}\n"
            )
            f.write(f"     Records Processed: {total_transactions}\n")
            f.write("=" * 44 + "\n\n")

            # OVERALL SUMMARY
            f.write("OVERALL SUMMARY\n")
            f.write("-" * 44 + "\n")
            f.write(f"Total Revenue:        ₹{total_revenue:,.2f}\n")
            f.write(f"Total Transactions:   {total_transactions}\n")
            f.write(f"Average Order Value:  ₹{avg_order_value:,.2f}\n")
            f.write(
                f"Date Range:           "
                f"{date_range[0]} to {date_range[1]}\n\n"
            )

            # REGION-WISE PERFORMANCE
            f.write("REGION-WISE PERFORMANCE\n")
            f.write("-" * 44 + "\n")
            f.write(
                f"{'Region':<10}"
                f"{'Sales':<15}"
                f"{'% of Total':<12}"
                f"Transactions\n"
            )

            for region, data in region_sales.items():
                f.write(
                    f"{region:<10}"
                    f"₹{data['total_sales']:>12,.2f}  "
                    f"{data['percentage']:>8.2f}%    "
                    f"{data['transaction_count']}\n"
                )
            f.write("\n")

            # TOP PRODUCTS
            f.write("TOP 5 PRODUCTS\n")
            f.write("-" * 44 + "\n")
            f.write(
                f"{'Rank':<6}"
                f"{'Product Name':<25}"
                f"{'Qty':<6}"
                f"Revenue\n"
            )

            for idx, (name, qty, revenue) in enumerate(
                top_products[:5], start=1
            ):
                f.write(
                    f"{idx:<6}"
                    f"{name:<25}"
                    f"{qty:<6}"
                    f"₹{revenue:,.2f}\n"
                )
            f.write("\n")

            # TOP CUSTOMERS
            top_customers = sorted(
                customer_stats.items(),
                key=lambda x: x[1].get("total_spent", 0),
                reverse=True
            )[:5]

            f.write("TOP 5 CUSTOMERS\n")
            f.write("-" * 44 + "\n")
            f.write(
                f"{'Rank':<6}"
                f"{'Customer ID':<15}"
                f"{'Spent':<15}"
                f"Orders\n"
            )

            for rank, (cust_id, data) in enumerate(top_customers, start=1):
                f.write(
                    f"{rank:<6}"
                    f"{cust_id:<15}"
                    f"₹{data['total_spent']:>12,.2f}  "
                    f"{data['purchase_count']}\n"
                )
            f.write("\n")

            # DAILY SALES TREND
            f.write("DAILY SALES TREND\n")
            f.write("-" * 44 + "\n")
            f.write(
                f"{'Date':<12}"
                f"{'Revenue':<15}"
                f"{'Txn':<6}"
                f"Customers\n"
            )

            for date, data in daily_trend.items():
                f.write(
                    f"{date:<12}"
                    f"₹{data['revenue']:>12,.2f}  "
                    f"{data['transaction_count']:<6}"
                    f"{data['unique_customers']}\n"
                )
            f.write("\n")

            # PRODUCT PERFORMANCE
            f.write("PRODUCT PERFORMANCE ANALYSIS\n")
            f.write("-" * 44 + "\n")
            peak_date, peak_revenue, peak_txn = peak_sales_day
            f.write(
                f"Best Selling Day: {peak_date} "
                f"(₹{peak_revenue:,.2f}, "
                f"{peak_txn} transactions)\n\n"
            )

            if low_products:
                f.write("Low Performing Products:\n")
                for name, qty, revenue in low_products:
                    f.write(
                        f"- {name}: "
                        f"{qty} units, "
                        f"₹{revenue:,.2f}\n"
                    )
            else:
                f.write("No low performing products identified.\n")

            f.write("\nAverage Transaction Value per Region:\n")
            for region, value in avg_value_per_region.items():
                f.write(f"- {region}: ₹{value:,.2f}\n")

            f.write("\n")

            # API ENRICHMENT
            f.write("API ENRICHMENT SUMMARY\n")
            f.write("-" * 44 + "\n")
            f.write(
                f"Total Enriched Records: "
                f"{enriched_count}/{total_transactions}\n"
            )
            f.write(f"Success Rate: {enrichment_rate:.2f}%\n")

            if failed_products:
                f.write("Products not enriched:\n")
                for product in failed_products:
                    f.write(f"- {product}\n")
            else:
                f.write("All products enriched successfully.\n")

        print(f"✓ Report successfully saved to: {output_file}")

    except FileNotFoundError:
        print("❌ Report Error: Output directory does not exist.")

    except PermissionError:
        print("❌ Report Error: Permission denied while writing report.")

    except Exception as e:
        print("❌ Report Generation Failed:")
        print(str(e))



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

        analyzer = SalesDateAnalyzer(valid_transactions)
        daily_trend = analyzer.daily_sales_trend()
        print("✓ Daily sales trend calculated")

        peak_date, peak_revenue, peak_count = analyzer.find_peak_sales_day()
        print(
            f"✓ Peak Sales Day: {peak_date} | "
            f"Revenue: ₹{peak_revenue} | "
            f"Transactions: {peak_count}"
        )

        low_products = low_performing_products(valid_transactions)
        print("✓ Low performing products identified\n")

        # -----------------------------
        # STEP 9: Fetch products from API
        # -----------------------------
        print("[9/10] Fetching product data from API...")
        api_products = fetch_all_products()

        if not api_products:
            print("⚠ No product data fetched. Skipping enrichment.")
            return

        product_mapping = create_product_mapping(api_products)

        # -----------------------------
        # STEP 10: Enrich sales data
        # -----------------------------
        print("[10/10] Enriching sales data...")
        enriched_transactions = enrich_sales_data(valid_transactions, product_mapping)

        matched = sum(1 for txn in enriched_transactions if txn.get("API_Match"))
        total = len(enriched_transactions)
        percentage = (matched / total * 100) if total else 0

        print(f"✓ Enriched {matched}/{total} transactions ({percentage:.2f}%)")

        # -----------------------------
        # STEP 11: Save enriched data
        # -----------------------------
        print("\nSaving enriched data...")
        save_enriched_data(enriched_transactions)

        print("\n[✔] Process Complete!")
        print("=" * 40)

        generate_sales_report(
            valid_transactions=valid_transactions,
            total_revenue=total_revenue,
            region_sales=region_sales,
            top_products=top_products,
            customer_stats=customer_stats,
            daily_trend=daily_trend,
            peak_sales_day=(peak_date, peak_revenue, peak_count),
            low_products=low_products,
            enriched_transactions=enriched_transactions
        )


        print("[10/10] Process Complete!")
        print("=" * 40)

    except FileNotFoundError as e:
        print("❌ File Error:", e)

    except Exception as e:
        print("❌ Unexpected Error Occurred:")
        print(str(e))


if __name__ == "__main__":
    main()