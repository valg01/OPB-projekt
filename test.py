import pandas as pd

pandas_postgres_types_mapping = {
    'int64': 'integer',
    'float64': 'double precision',
    'bool': 'boolean',
    'datetime64[ns]': 'timestamp',
    'timedelta64[ns]': 'interval',
    'object': 'text',
    'category': 'enum'
}

