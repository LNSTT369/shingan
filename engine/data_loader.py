import os
import glob
import pandas as pd
import numpy as np

class DataLoader:
    """
    High-performance intraday data loader for equity and futures datasets.
    Standardizes timestamps to America/New_York timezone.
    """
    def __init__(self, data_dir=None):
        if data_dir is None:
            # Check local data dir then fallback
            local_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'intraday_5m')
            fallback_path = '/Users/user/Desktop/ict mechanical/data/intraday_5m'
            self.data_dir = local_path if os.path.exists(local_path) else fallback_path
        else:
            self.data_dir = data_dir

    def load_ticker(self, ticker='QQQ', start_year=2010, end_year=2026):
        """
        Loads all 5-minute bars for a ticker across the requested year range.
        Returns a DataFrame indexed by America/New_York datetime.
        """
        dfs = []
        for y in range(start_year, end_year + 1):
            p = os.path.join(self.data_dir, str(y), f'{ticker}.csv')
            if os.path.exists(p):
                df_y = pd.read_csv(p)
                dfs.append(df_y)
        
        if not dfs:
            raise FileNotFoundError(f'No data found for ticker {ticker} in {self.data_dir}')
            
        full = pd.concat(dfs, ignore_index=True)
        full['dt'] = pd.to_datetime(full['timestamp']).dt.tz_convert('America/New_York')
        full = full.sort_values('dt').reset_index(drop=True)
        full['date'] = full['dt'].dt.date
        full['hour'] = full['dt'].dt.hour
        full['minute'] = full['dt'].dt.minute
        full['time_min'] = full['hour'] * 60 + full['minute']
        return full
