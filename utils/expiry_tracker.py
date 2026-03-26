"""
Medicine expiry tracking and redistribution prioritization
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from dataclasses import dataclass

@dataclass
class ExpiryAlert:
    """Data class for expiry alerts"""
    facility_id: str
    medicine_id: str
    medicine_name: str
    batch_id: str
    current_stock: int
    expiry_date: str
    days_to_expiry: int
    alert_level: str  # 'critical', 'warning', 'normal'
    waste_risk: float  # Estimated waste probability (0-1)

class ExpiryTracker:
    """Track medicine expiry dates and trigger redistribution"""
    
    def __init__(self, warning_days: int = 14, critical_days: int = 3):
        """
        Initialize expiry tracker
        
        Args:
            warning_days: Days before expiry to issue warning
            critical_days: Days before expiry for critical alert
        """
        self.warning_days = warning_days
        self.critical_days = critical_days
        self.alerts = []
    
    @staticmethod
    def calculate_days_to_expiry(expiry_date: str) -> int:
        """Calculate days until medicine expires"""
        expiry = pd.to_datetime(expiry_date).date()
        today = datetime.now().date()
        return (expiry - today).days
    
    def categorize_alert(self, days_to_expiry: int) -> str:
        """Categorize alert severity"""
        if days_to_expiry <= self.critical_days:
            return 'critical'
        elif days_to_expiry <= self.warning_days:
            return 'warning'
        else:
            return 'normal'
    
    def estimate_waste_risk(self, current_stock: int, 
                           daily_usage: float,
                           days_to_expiry: int) -> float:
        """
        Estimate probability of waste based on usage rate and expiry timeline
        
        Args:
            current_stock: Current units in inventory
            daily_usage: Average daily usage
            days_to_expiry: Days until expiry
        
        Returns:
            Waste risk probability (0-1)
        """
        if days_to_expiry <= 0:
            return 1.0
        
        # Expected usage by expiry date
        expected_usage = daily_usage * days_to_expiry
        
        # Calculate waste probability
        if expected_usage <= 0:
            waste_risk = 1.0
        else:
            # Logistic function to smooth waste probability
            ratio = current_stock / expected_usage
            waste_risk = 1 / (1 + np.exp(-(ratio - 1)))
        
        return float(np.clip(waste_risk, 0, 1))
    
    def track_inventory(self, inventory_df: pd.DataFrame,
                       usage_stats: Dict[str, float]) -> List[ExpiryAlert]:
        """
        Track inventory and identify expiry risks
        
        Args:
            inventory_df: DataFrame with current inventory
            usage_stats: Dictionary with usage statistics by medicine
        
        Returns:
            List of ExpiryAlert objects
        """
        alerts = []
        
        for _, row in inventory_df.iterrows():
            medicine_id = row['medicine_id']
            
            # Get daily usage for this medicine
            daily_usage = usage_stats.get(medicine_id, 20)  # default 20 units/day
            
            # Calculate days to expiry
            days_to_expiry = self.calculate_days_to_expiry(row['expiry_date'])
            
            # Estimate waste risk
            waste_risk = self.estimate_waste_risk(
                row['current_stock'],
                daily_usage,
                days_to_expiry
            )
            
            # Categorize alert
            alert_level = self.categorize_alert(days_to_expiry)
            
            # Only create alert if there's risk
            if alert_level != 'normal' or waste_risk > 0.3:
                alert = ExpiryAlert(
                    facility_id=row['facility_id'],
                    medicine_id=medicine_id,
                    medicine_name=row['medicine_name'],
                    batch_id=row['batch_id'],
                    current_stock=row['current_stock'],
                    expiry_date=str(row['expiry_date']),
                    days_to_expiry=days_to_expiry,
                    alert_level=alert_level,
                    waste_risk=waste_risk
                )
                alerts.append(alert)
        
        self.alerts = alerts
        return alerts
    
    def get_redistribution_candidates(self, usage_df: pd.DataFrame,
                                     inventory_df: pd.DataFrame) -> Dict[str, List]:
        """
        Identify medicines for redistribution from low-usage facilities
        
        Args:
            usage_df: Usage history dataframe
            inventory_df: Current inventory dataframe
        
        Returns:
            Dictionary mapping medicine_id to redistribution opportunities
        """
        redistribution_map = {}
        
        # Group inventory by medicine
        for medicine_id in inventory_df['medicine_id'].unique():
            medicine_inv = inventory_df[
                inventory_df['medicine_id'] == medicine_id
            ]
            
            # Find facilities with expiry risks
            expiring = medicine_inv[
                medicine_inv['expiry_date'] < 
                (datetime.now() + timedelta(days=self.warning_days)).date()
            ]
            
            if len(expiring) > 0:
                # Calculate usage by facility for this medicine
                facility_usage = usage_df[
                    usage_df['medicine_id'] == medicine_id
                ].groupby('facility_id')['units_used'].mean()
                
                # Sort facilities by usage (low usage first)
                facilities_sorted = facility_usage.sort_values().index.tolist()
                
                redistribution_map[medicine_id] = {
                    'expiring_facilities': expiring[['facility_id', 'current_stock', 'expiry_date']].to_dict('records'),
                    'facilities_by_usage': facilities_sorted
                }
        
        return redistribution_map
    
    def prioritize_distribution(self, alerts: List[ExpiryAlert],
                               max_items: int = 10) -> List[ExpiryAlert]:
        """
        Prioritize medicines for urgent distribution
        
        Args:
            alerts: List of expiry alerts
            max_items: Maximum number of items to prioritize
        
        Returns:
            Sorted list of high-priority items
        """
        # Score each alert: critical > warning, higher waste risk, fewer days
        def priority_score(alert: ExpiryAlert) -> float:
            level_score = {
                'critical': 100,
                'warning': 50,
                'normal': 0
            }
            
            score = (
                level_score[alert.alert_level] +
                alert.waste_risk * 50 -
                max(0, alert.days_to_expiry)
            )
            return score
        
        # Sort by priority score (highest first)
        prioritized = sorted(alerts, key=priority_score, reverse=True)
        
        return prioritized[:max_items]
    
    def generate_redistribution_plan(self, alerts: List[ExpiryAlert],
                                    prioritized: List[ExpiryAlert]) -> Dict:
        """
        Generate detailed redistribution plan
        
        Args:
            alerts: All expiry alerts
            prioritized: Prioritized alerts for action
        
        Returns:
            Dictionary with redistribution plan
        """
        plan = {
            'total_alerts': len(alerts),
            'critical_alerts': sum(1 for a in alerts if a.alert_level == 'critical'),
            'warning_alerts': sum(1 for a in alerts if a.alert_level == 'warning'),
            'total_at_risk_units': sum(a.current_stock for a in alerts),
            'estimated_waste_value': sum(
                a.current_stock * a.waste_risk for a in alerts
            ),
            'urgent_actions': [
                {
                    'facility_id': a.facility_id,
                    'medicine_id': a.medicine_id,
                    'medicine_name': a.medicine_name,
                    'batch_id': a.batch_id,
                    'units': a.current_stock,
                    'expiry_date': a.expiry_date,
                    'days_to_expiry': a.days_to_expiry,
                    'action': 'REDISTRIBUTE' if a.alert_level == 'critical' else 'MONITOR'
                }
                for a in prioritized
            ]
        }
        
        return plan
