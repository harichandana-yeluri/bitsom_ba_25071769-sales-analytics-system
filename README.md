# Sales Analytics System

A Python-based sales analytics system that performs data validation, analysis,
API-based enrichment, and report generation on transactional sales data.

---

## 📌 Project Features

- Data ingestion and parsing from pipe-delimited text files
- Validation and cleaning of sales transactions
- Optional filtering by **region** and **transaction amount**
- Comprehensive sales analytics:
  - Total revenue
  - Region-wise performance
  - Top products and customers
  - Daily sales trends
  - Low-performing products
- Product data enrichment using DummyJSON API
- Detailed text-based sales report generation

---

## 📂 Project Structure

```text
sales-analytics-system/
  ├── README.md
  ├── main.py
  ├── utils/
  │   ├── file_handler.py
  │   ├── data_processor.py
  │   └── api_handler.py
  ├── data/
  │   ├── sales_data.txt (provided)
  |   └── enriched_sales_data.txt (generated)
  ├── output/
  │   └── Sales_report.txt 
  └── requirements.txt
```


---

## 📄 Input Data Requirement

### `data/sales_data.txt`

- Must exist before running the program
- Pipe-delimited (`|`) format
- Required columns:

TransactionID|Date|ProductID|ProductName|Quantity|UnitPrice|CustomerID|Region

---

## 🌐 External API Used

**DummyJSON Products API**
- URL: `https://dummyjson.com/products`
- Used to enrich sales transactions with:
  - Category
  - Brand
  - Rating

---

## 🐍 Python Version

- **Python 3.8 or higher** is required

---

## ⚙️ Installation & Setup

### 1️⃣ Install dependencies
```bash
pip install -r requirements.txt

---


---

## ⚙️ Workflow Overview

1. Read sales data from file
2. Parse and clean raw records
3. Display available filter options (regions and amount range)
4. **Optionally filter data by region and/or amount**
5. Validate transactions
6. Perform sales analytics
7. Fetch product data from external API
8. Enrich validated sales data
9. Save enriched data to file
10. Generate a comprehensive analytics report

---

## 🔍 Important Note on Filtering Behavior

> **Region filtering affects the entire pipeline**

If a **region filter is applied**, then:
- All validations
- All analytics (revenue, top customers, trends, etc.)
- API enrichment
- Final report generation  

⚠️ **Will be performed only on the filtered region’s data**

If **no region is selected**, the system processes **all available data**.

This behavior is **intentional** and ensures analytical consistency across outputs.

---

## 🧾 Generated Outputs

### Enriched Sales Data
- File: `data/enriched_sales_data.txt`
- Includes API-enriched fields:
  - Category
  - Brand
  - Rating
  - API match flag

### Sales Report
- File: `output/sales_report.txt`
- Includes:
  - Overall summary
  - Region-wise performance
  - Top products and customers
  - Daily trends
  - Product performance analysis
  - API enrichment summary

---

## 🧠 Error Handling

- File read errors handled gracefully
- Invalid records skipped during cleaning
- API failures handled without crashing
- Report generation wrapped in `try-except`

---

## ▶️ How to Run

```bash
python3 main.py
```
