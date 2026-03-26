"""
Data loading and preprocessing utilities for hospital supply chain data
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Tuple, Dict
import os

class SupplyDataLoader:
    """Load and preprocess hospital supply chain data"""
    
    def __init__(self, data_dir: str = "data"):
        """Initialize data loader"""
        self.data_dir = data_dir
        self.usage_data = None
        self.inventory_data = None
        self.medicine_data = None
    
    def load_csv_data(self, filename: str) -> pd.DataFrame:
        """Load CSV data from data directory"""
        filepath = os.path.join(self.data_dir, filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        return pd.read_csv(filepath)
    
    def generate_sample_usage_data(self, days: int = 90, 
                                   facilities: int = 5,
                                   medicines_per_facility: int = 10) -> pd.DataFrame:
        """
        Generate sample usage data for demonstration
        
        Args:
            days: Number of days of historical data
            facilities: Number of hospital facilities
            medicines_per_facility: Number of medicine types per facility
        
        Returns:
            DataFrame with columns: date, facility_id, medicine_id, units_used, medicine_name
        """
        dates = [datetime.now() - timedelta(days=x) for x in range(days)]
        data = []
        
        for date in dates:
            for facility in range(1, facilities + 1):
                for med in range(1, medicines_per_facility + 1):
                    # Create realistic usage patterns with seasonality and randomness
                    base_usage = 20 + (med * 2)
                    noise = np.random.normal(0, 5)
                    seasonality = 5 * np.sin(2 * np.pi * date.day / 30)
                    usage = max(0, base_usage + noise + seasonality)
                    
                    data.append({
                        'date': date.date(),
                        'facility_id': f'FAC_{facility:02d}',
                        'medicine_id': f'MED_{med:03d}',
                        'units_used': round(usage),
                        'medicine_name': f'Medicine_{med}'
                    })
        
        df = pd.DataFrame(data)
        df.sort_values('date', inplace=True)
        return df
    
    def generate_sample_inventory_data(self, facilities: int = 5,
                                      medicines_per_facility: int = 10) -> pd.DataFrame:
        """Generate sample current inventory data"""
        data = []
        
        for facility in range(1, facilities + 1):
            for med in range(1, medicines_per_facility + 1):
                expiry_date = datetime.now() + timedelta(
                    days=np.random.randint(15, 180)
                )
                stock_level = np.random.randint(50, 500)
                
                data.append({
                    'facility_id': f'FAC_{facility:02d}',
                    'medicine_id': f'MED_{med:03d}',
                    'medicine_name': f'Medicine_{med}',
                    'current_stock': stock_level,
                    'expiry_date': expiry_date.date(),
                    'batch_id': f'BATCH_{facility}_{med}_{np.random.randint(1000, 9999)}'
                })
        
        return pd.DataFrame(data)
    
    def preprocess_usage_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and preprocess usage data
        
        Args:
            df: Raw usage data
        
        Returns:
            Cleaned usage data
        """
        df = df.copy()
        
        # Convert date to datetime
        if df['date'].dtype == 'object':
            df['date'] = pd.to_datetime(df['date'])
        
        # Remove negative values
        df = df[df['units_used'] >= 0]
        
        # Fill any missing values with forward fill then backward fill
        df.set_index(['date', 'facility_id', 'medicine_id'], inplace=True)
        df = df.unstack(fill_value=0).stack().reset_index()
        
        return df
    
    @staticmethod
    def aggregate_by_facility_medicine(df: pd.DataFrame) -> pd.DataFrame:
        """Aggregate usage data by facility and medicine"""
        return df.groupby(['date', 'facility_id', 'medicine_id']).agg({
            'units_used': 'sum',
            'medicine_name': 'first'
        }).reset_index()
    
    @staticmethod
    def calculate_daily_statistics(df: pd.DataFrame) -> Dict:
        """Calculate daily usage statistics"""
        stats = {
            'mean_daily_usage': df['units_used'].mean(),
            'std_daily_usage': df['units_used'].std(),
            'min_daily_usage': df['units_used'].min(),
            'max_daily_usage': df['units_used'].max(),
            'total_usage': df['units_used'].sum()
        }
        return stats
