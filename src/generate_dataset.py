import pandas as pd
import sys

def main(excel_path='dataset.xlsx', orders_sheet=None,  inventory_sheet=None
):
    # 1) Inspect sheets
    xls = pd.ExcelFile(excel_path)
    print("Found sheets:", xls.sheet_names)
    
    # 2) Get sheet names
    if orders_sheet is None:
        orders_sheet = xls.sheet_names[0]
    if inventory_sheet is None:
        inventory_sheet = xls.sheet_names[1] if len(xls.sheet_names) > 1 else None

    print(f"→ Using Orders sheet:   '{orders_sheet}'")
    print(f"→ Using Inventory sheet:'{inventory_sheet}'")

    # 3) Load
    orders = pd.read_excel(excel_path, sheet_name=orders_sheet)
    inventory = pd.read_excel(excel_path, sheet_name=inventory_sheet)

    # === ORDERS TRANSFORMATIONS ===

    # 4) Parse CreatedDate + extract temporal features
    if 'CreatedDate' in orders.columns:
        # Parse datetime and convert to timezone-naive for compatibility
        orders['CreatedDate'] = pd.to_datetime(orders['CreatedDate'], errors='coerce')
        
        # If timezone-aware, convert to naive (remove timezone info)
        if orders['CreatedDate'].dt.tz is not None:
            orders['CreatedDate'] = orders['CreatedDate'].dt.tz_convert(None)
        
        # Extract temporal features
        orders['Order_DayOfWeek'] = orders['CreatedDate'].dt.day_name()
        orders['Order_Hour']      = orders['CreatedDate'].dt.hour
        orders['Order_Month']     = orders['CreatedDate'].dt.month
        orders['Order_Week']      = orders['CreatedDate'].dt.isocalendar().week
        orders['Order_DayOfWeek_Num'] = orders['CreatedDate'].dt.dayofweek

    else:
        print("⚠️  'CreatedDate' column not found in orders — skipping date parsing.")

    # 5) Numeric coercion with better error handling
    numeric_cols = [
        'Quantity','OriginalUnitPrice','OriginalLineTotal',
        'FinalUnitPrice','FinalLineTotal',
        'FinalOrderItemsTotal','ShippingTotal','TotalOrderAmount'
    ]
    for c in numeric_cols:
        if c in orders.columns:
            orders[c] = pd.to_numeric(orders[c], errors='coerce')
            # Fill NaN values with 0 for quantity, but keep NaN for prices to identify missing data
            if c == 'Quantity':
                orders[c] = orders[c].fillna(0).astype(int)
        else:
            print(f"⚠️  '{c}' not found in orders — skipping numeric coercion for this column.")

    # 6) Calculate discount percentage and other derived fields
    if 'OriginalUnitPrice' in orders.columns and 'FinalUnitPrice' in orders.columns:
        orders['Discount_Amount'] = orders['OriginalUnitPrice'] - orders['FinalUnitPrice']
        orders['Discount_Pct'] = (
            orders['Discount_Amount'] / orders['OriginalUnitPrice']
        ).fillna(0)
        orders['Has_Discount'] = orders['Discount_Pct'] > 0

    # 7) Clean text fields and handle missing values
    text_cols = ['SKU', 'Item title', 'Category', 'Brand']
    for c in text_cols:
        if c in orders.columns:
            # Convert to string and handle missing values
            orders[c] = orders[c].astype(str).replace('nan', 'Unknown')
            # Clean up common issues
            orders[c] = orders[c].str.strip()  # Remove whitespace
            
    # 8) Categoricals → category dtype (after cleaning)
    cat_cols = ['SKU','Item title','Category','Brand','Order_DayOfWeek']
    for c in cat_cols:
        if c in orders.columns:
            orders[c] = orders[c].astype('category')

    # 9) Data quality checks
    print("\n📊 ORDERS DATA QUALITY SUMMARY:")
    print(f"   Total records: {len(orders):,}")
    print(f"   Date range: {orders['CreatedDate'].min()} to {orders['CreatedDate'].max()}")
    print(f"   Unique orders: {orders['OrderNumber'].nunique():,}")
    print(f"   Unique SKUs: {orders['SKU'].nunique():,}")
    print(f"   Records with discounts: {orders.get('Has_Discount', pd.Series()).sum():,}")
    
    # Check for missing critical data
    critical_cols = ['OrderNumber', 'SKU', 'Quantity', 'FinalUnitPrice']
    for col in critical_cols:
        if col in orders.columns:
            missing_count = orders[col].isnull().sum()
            if missing_count > 0:
                print(f"   ⚠️  Missing {col}: {missing_count:,} records")

    # 10) Export
    orders_out = 'orders_data.csv'
    orders.to_csv(orders_out, index=False)
    print(f"✅ Saved transformed orders → {orders_out} ({orders.shape[0]:,}×{orders.shape[1]})")

    # === INVENTORY TRANSFORMATIONS ===

    # 11) Clean SKU field first
    if 'SKU' in inventory.columns:
        inventory['SKU'] = inventory['SKU'].astype(str).str.strip()

    # 12) Numeric coercion for quantity
    if 'Quantity' in inventory.columns:
        inventory['Quantity'] = pd.to_numeric(inventory['Quantity'], errors='coerce').fillna(0).astype(int)
    else:
        print("⚠️  'Quantity' not found in inventory — skipping numeric coercion.")

    # 13) Stock level bins (optional but useful for analysis)
    if 'Quantity' in inventory.columns:
        inventory['Stock_Available'] = inventory['Quantity'] > 0
        
        # Get quantity statistics for better binning
        min_q = inventory['Quantity'].min()
        max_q = inventory['Quantity'].max()
        
        print(f"   Quantity range: {min_q} to {max_q}")
        
        # Create stock level categories using conditions (more robust than pd.cut)
        def categorize_stock(qty):
            if qty == 0:
                return 'Out_of_Stock'
            elif qty <= 10:
                return 'Critical_Low'
            elif qty <= 50:
                return 'Low'
            elif qty <= 200:
                return 'Medium'
            else:
                return 'High'
        
        inventory['Stock_Level'] = inventory['Quantity'].apply(categorize_stock)
        inventory['Stock_Level'] = inventory['Stock_Level'].astype('category')

    # 14) SKU as category
    if 'SKU' in inventory.columns:
        inventory['SKU'] = inventory['SKU'].astype('category')

    # 15) Data quality summary for inventory
    print("\n📦 INVENTORY DATA QUALITY SUMMARY:")
    print(f"   Total SKUs: {len(inventory):,}")
    print(f"   SKUs in stock: {(inventory['Quantity'] > 0).sum():,}")
    print(f"   SKUs out of stock: {(inventory['Quantity'] == 0).sum():,}")
    print(f"   Total inventory units: {inventory['Quantity'].sum():,}")
    if 'Stock_Level' in inventory.columns:
        print(f"   Stock level distribution:")
        for level, count in inventory['Stock_Level'].value_counts().items():
            print(f"     {level}: {count:,}")

    # 16) Cross-reference check
    orders_skus = set(orders['SKU'].unique()) if 'SKU' in orders.columns else set()
    inventory_skus = set(inventory['SKU'].unique()) if 'SKU' in inventory.columns else set()
    
    missing_inventory = orders_skus - inventory_skus
    if missing_inventory:
        print(f"\n⚠️  WARNING: {len(missing_inventory)} SKUs in orders but not in inventory:")
        print(f"   Examples: {list(missing_inventory)[:5]}")

    # 17) Export
    inv_out = 'inventory_data.csv'
    inventory.to_csv(inv_out, index=False)
    print(f"✅ Saved transformed inventory → {inv_out} ({inventory.shape[0]:,}×{inventory.shape[1]})")

    print(f"\n🎯 DATA PREPROCESSING COMPLETE!")
    print(f"   Files ready for bundling analysis:")
    print(f"   • {orders_out}")
    print(f"   • {inv_out}")

if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) == 0:
        main()
    elif len(args) == 1:
        main(excel_path=args[0])
    elif len(args) == 3:
        main(excel_path=args[0], orders_sheet=args[1], inventory_sheet=args[2])
    else:
        print("Usage:")
        print("  python preprocess.py [path_to_excel [orders_sheet inventory_sheet]]")