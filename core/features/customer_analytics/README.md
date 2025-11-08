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

Your CSV file must have the following columns:

| Column      | Type    | Description                    |
|-------------|---------|--------------------------------|
| timestamp   | int64   | Unix timestamp                 |
| visitorid   | int64   | Unique visitor identifier      |
| itemid      | int64   | Item/product identifier        |
| event       | object  | Event type (view/addtocart/transaction) |
| categoryid  | object  | Category identifier            |
| price       | float64 | Item price                     |
| datetime    | object  | Human-readable datetime        |
| row_number  | int64   | Row number                     |

### Event Types

The `event` column must contain only these values:
- `view`
- `addtocart`
- `transaction`

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

