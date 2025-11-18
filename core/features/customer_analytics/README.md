# Customer Analytics Platform

Data preprocessing and feature engineering for customer behavior analysis and churn prediction.

## Features

- ✅ CSV data validation and format checking
- ✅ Sessionization (configurable timeout)
- ✅ Session-level feature aggregation
- ✅ Customer-level feature engineering
- ✅ Churn prediction dataset creation
- ✅ Interactive CLI and command-line modes

## Quick Start

### Interactive Mode (Recommended)

The easiest way to use the platform is through the interactive CLI:

```bash
# Option 1: Using main.py
python main.py --interactive

# Option 2: Direct execution
python interactive_cli.py
```

The interactive mode will guide you through:
1. **Data Source**: Enter your CSV file path
2. **Data Validation**: Automatic format checking
3. **Session Timeout**: Configure session timeout (default: 15 minutes)
4. **Feature Engineering**: Choose to run feature engineering
5. **Split Time**: Auto-calculate or manually specify
6. **Save Options**: Choose where to save results
7. **Processing**: Automatic data processing

### Command-Line Mode

For automated scripts and batch processing:

```bash
# Preprocessing only
python main.py input.csv

# Preprocessing + Feature Engineering
python main.py input.csv --feature-engineering

# With custom options
python main.py input.csv \
    --feature-engineering \
    --split-time 2015-08-20 \
    --train-ratio 0.8 \
    --min-sessions 2 \
    --max-recency-days 30
```

## Data Format Requirements

The `preprocessing.py` module automatically validates your dataset before processing. Your CSV file **must** contain all required columns with exact names and correct data types.

### Required Columns

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| `timestamp` | int64 | ✅ Yes | UNIX timestamp for the event (UTC seconds since epoch). |
| `visitorid` | int64 | ✅ Yes | Unique customer/visitor identifier. Must be numeric. |
| `itemid` | int64 | ✅ Yes | Product/item identifier associated with the interaction. Must be numeric. |
| `event` | object/string | ✅ Yes | Event type. **Must be one of:** `view`, `addtocart`, `transaction` (case-sensitive). |
| `categoryid` | object/string | ✅ Yes | Product category identifier. Can be numeric or string. |
| `price` | float64 | ✅ Yes | Item price at the time of the event. Must be numeric (can include 0.0). |
| `datetime` | object/string | ✅ Yes | Human-readable timestamp (ISO-8601 format recommended, e.g., `2024-01-15 10:30:00`). |
| `row_number` | int64 | ✅ Yes | Sequential row counter (monotonic within the file). Must start from 1 and increment. |

### Event Type Values

The `event` column **must only** contain these exact values (case-sensitive):
- ✅ `view` - User viewed a product/item
- ✅ `addtocart` - User added item to shopping cart  
- ✅ `transaction` - User completed a purchase

**Invalid values will cause validation errors.** The preprocessing module automatically checks event vocabulary.

### Data Validation

The `preprocessing.py` module performs automatic validation:

- ✅ **Column existence check**: Verifies all 8 required columns are present
- ✅ **Data type validation**: Checks numeric columns are correct type (int64, float64)
- ✅ **Event value validation**: Ensures only valid event types (`view`, `addtocart`, `transaction`) exist
- ✅ **Format consistency**: Validates data structure matches expected format

**Validation errors** provide detailed messages indicating:
- Which columns are missing
- Type mismatches (e.g., if `visitorid` is string instead of int64)
- Invalid event values found (e.g., `purchase` instead of `transaction`)
- Expected vs. received format

### Example Valid Dataset

```csv
timestamp,visitorid,itemid,event,categoryid,price,datetime,row_number
1705316400,123456,789,view,electronics,149.99,2024-01-15 10:30:00,1
1705316460,123456,790,addtocart,electronics,299.99,2024-01-15 10:31:00,2
1705316520,123456,790,transaction,electronics,299.99,2024-01-15 10:32:00,3
1705316580,123457,791,view,clothing,49.99,2024-01-15 10:33:00,4
1705316640,123457,792,addtocart,clothing,79.99,2024-01-15 10:34:00,5
```

**See:** `preprocessing.py` source code for full validation logic (`validate_data_format()` function)

## Output Files

### Aggregated Sessions

Session-level aggregated features:
- `item_n`: Number of unique items
- `cat_n`: Number of unique categories
- `int_n`: Total interactions
- `view_n`, `cart_n`, `tran_n`: Event counts
- `view_sp`, `cart_sp`, `tran_sp`: Spending by event type
- `start_time`, `end_time`, `len`: Session timing
- `major_spend`: Largest transaction
- `major_spend_r`: Major spend ratio

### Classification Data

Customer-level features for churn prediction:
- Session recency metrics
- User recency metrics
- Session counts and ratios
- Transaction metrics
- Revenue metrics
- Temporal patterns (month, hour, weekend)
- Category interaction counts
- Target variable (churn/visit/transaction)

## Configuration Options

### Session Timeout

Time in minutes before a new session starts (default: 15 minutes).

### Split Time

Divides data into:
- **Features**: Sessions before split_time (historical behavior)
- **Target**: Sessions after split_time (future behavior)

Options:
- **Auto-calculate**: Automatically finds the split point (default: 70% for features, 30% for target)
- **Manual**: Specify a date (YYYY-MM-DD format)

### Train Ratio

When using auto-calculated split time, this determines the percentage of data used for features (default: 0.7 = 70%).

### Filtering Options

- **Min Sessions**: Minimum number of sessions required (default: 1)
- **Max Recency Days**: Maximum days since last session (default: 31)

## Output Locations

### Default Locations

- **Aggregated Sessions**: Same directory as input file with `_aggregated_sessions.csv` suffix
- **Classification Data**: `results/` directory with timestamp: `classification_data_YYYYMMDD_HHMMSS.csv`

### Custom Locations

In interactive mode, you can specify custom save locations and filenames.

## Examples

### Example 1: Basic Preprocessing

```bash
python main.py data.csv
```

Output: `data_aggregated_sessions.csv`

### Example 2: Full Pipeline with Auto Split

```bash
python main.py data.csv --feature-engineering --train-ratio 0.8
```

Output: `results/classification_data_TIMESTAMP.csv`

### Example 3: Manual Split Time

```bash
python main.py data.csv \
    --feature-engineering \
    --split-time 2015-08-20 \
    --min-sessions 2
```

## Interactive Mode Workflow

1. **Welcome Screen**: System information and capabilities
2. **Data Source**: Enter CSV file path
3. **Validation**: Automatic format checking
4. **Session Timeout**: Configure timeout (default: 15 min)
5. **Feature Engineering**: Choose to enable/disable
6. **Split Time**: Auto or manual configuration
7. **Filtering**: Min sessions and max recency
8. **Save Options**: 
   - Save aggregated sessions? (y/n)
   - Save classification data? (y/n)
   - Default or custom location?
   - Default or custom filename?
9. **Processing**: Automatic execution
10. **Results**: Summary and file locations

## Error Handling

The platform includes comprehensive error handling:

- **File Not Found**: Clear error messages with retry options
- **Format Validation**: Detailed error messages showing expected vs. received format
- **Invalid Input**: Validation with helpful error messages
- **Processing Errors**: Detailed error messages with traceback

## Tips

1. **First Time Users**: Use interactive mode for guided experience
2. **Automation**: Use command-line mode for scripts and batch processing
3. **Large Datasets**: Feature engineering can take time for large datasets
4. **Split Time**: Auto-calculate is recommended unless you have specific business requirements
5. **Save Options**: Default locations are organized and timestamped

## Support

For issues or questions, please check:
- Data format requirements
- Error messages (they are detailed and helpful)
- Example usage above

## License

Part of the DAFU Enterprise Fraud Detection & E-commerce Analytics Platform.

