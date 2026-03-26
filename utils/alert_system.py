"""
Alert system for shortage predictions and inventory issues
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from dataclasses import dataclass

@dataclass
class Alert:
    """Alert notification"""
    timestamp: str
    alert_type: str  # 'shortage', 'expiry', 'low_stock', 'surplus'
    facility_id: str
    medicine_id: str
    medicine_name: str
    severity: str  # 'critical', 'warning', 'info'
    message: str
    recommended_action: str
    confidence: float

class AlertSystem:
    """Automated alert system for inventory management"""
    
    def __init__(self):
        """Initialize alert system"""
        self.alerts = []
        self.alert_history = []
    
    def check_shortage_risk(self, 
                           forecasted_demand: List[float],
                           current_stock: int,
                           min_stock_threshold: int = 10) -> Tuple[bool, float]:
        """
        Check if medicine will face shortage
        
        Args:
            forecasted_demand: List of forecasted daily usage
            current_stock: Current inventory level
            min_stock_threshold: Minimum required stock
        
        Returns:
            Tuple of (shortage_risk, probability)
        """
        # Cumulative demand over forecast period
        cumulative_demand = np.sum(forecasted_demand)
        
        # Calculate shortage probability
        if cumulative_demand > current_stock:
            days_to_shortage = np.where(
                np.cumsum(forecasted_demand) > current_stock
            )[0]
            
            if len(days_to_shortage) > 0:
                shortage_day = days_to_shortage[0]
                
                # Higher probability if shortage occurs soon
                prob = min(1.0, (7 - shortage_day) / 7) if shortage_day < 7 else 0.3
            else:
                prob = 0.5
        else:
            # Stock sufficient, lower probability
            buffer_days = current_stock / np.mean(forecasted_demand)
            prob = max(0, 1 - (buffer_days / 7))
        
        shortage_risk = prob > 0.5
        return shortage_risk, float(prob)
    
    def check_low_stock(self,
                       current_stock: int,
                       average_daily_usage: float,
                       low_stock_days: int = 3) -> Tuple[bool, float]:
        """
        Check if current stock is dangerously low
        
        Args:
            current_stock: Current inventory
            average_daily_usage: Average daily usage
            low_stock_days: Days of supply considered acceptable
        
        Returns:
            Tuple of (is_low_stock, severity_score)
        """
        if average_daily_usage <= 0:
            return False, 0.0
        
        days_of_supply = current_stock / average_daily_usage
        
        if days_of_supply < low_stock_days:
            severity = 1 - (days_of_supply / low_stock_days)
            return True, float(np.clip(severity, 0, 1))
        
        return False, 0.0
    
    def generate_shortage_alert(self,
                              facility_id: str,
                              medicine_id: str,
                              medicine_name: str,
                              forecasted_demand: List[float],
                              current_stock: int,
                              shortage_prob: float) -> Alert:
        """Generate a shortage alert"""
        if shortage_prob > 0.7:
            severity = 'critical'
        elif shortage_prob > 0.5:
            severity = 'warning'
        else:
            severity = 'info'
        
        days_to_shortage = int(
            current_stock / np.mean(forecasted_demand)
        ) if np.mean(forecasted_demand) > 0 else 7
        
        return Alert(
            timestamp=datetime.now().isoformat(),
            alert_type='shortage',
            facility_id=facility_id,
            medicine_id=medicine_id,
            medicine_name=medicine_name,
            severity=severity,
            message=f"Potential shortage of {medicine_name} in {days_to_shortage} days "
                   f"(Probability: {shortage_prob*100:.1f}%)",
            recommended_action=f"Increase procurement or redistribute from nearby facilities",
            confidence=shortage_prob
        )
    
    def generate_low_stock_alert(self,
                                facility_id: str,
                                medicine_id: str,
                                medicine_name: str,
                                current_stock: int,
                                daily_usage: float,
                                severity_score: float) -> Alert:
        """Generate a low stock alert"""
        days_remaining = current_stock / daily_usage if daily_usage > 0 else 0
        
        if severity_score > 0.7:
            severity = 'critical'
        elif severity_score > 0.4:
            severity = 'warning'
        else:
            severity = 'info'
        
        return Alert(
            timestamp=datetime.now().isoformat(),
            alert_type='low_stock',
            facility_id=facility_id,
            medicine_id=medicine_id,
            medicine_name=medicine_name,
            severity=severity,
            message=f"Low stock of {medicine_name}: {current_stock} units remaining "
                   f"({days_remaining:.1f} days supply)",
            recommended_action=f"Place emergency order or request redistribution",
            confidence=severity_score
        )
    
    def generate_expiry_alert(self,
                            facility_id: str,
                            medicine_id: str,
                            medicine_name: str,
                            batch_id: str,
                            current_stock: int,
                            days_to_expiry: int) -> Alert:
        """Generate an expiry alert"""
        if days_to_expiry <= 3:
            severity = 'critical'
        elif days_to_expiry <= 14:
            severity = 'warning'
        else:
            severity = 'info'
        
        return Alert(
            timestamp=datetime.now().isoformat(),
            alert_type='expiry',
            facility_id=facility_id,
            medicine_id=medicine_id,
            medicine_name=medicine_name,
            severity=severity,
            message=f"Batch {batch_id} of {medicine_name} expires in {days_to_expiry} days "
                   f"({current_stock} units)",
            recommended_action=f"Prioritize usage or redistribute to high-demand facilities",
            confidence=float(min(1.0, 1 - days_to_expiry / 30))
        )
    
    def process_facility_alerts(self,
                               facility_id: str,
                               medicines: List[Dict],
                               forecasts: Dict,
                               usage_stats: Dict) -> List[Alert]:
        """
        Process all alerts for a facility
        
        Args:
            facility_id: Facility identifier
            medicines: List of medicine inventory dicts
            forecasts: Dictionary of forecasts by medicine_id
            usage_stats: Dictionary of usage statistics by medicine_id
        
        Returns:
            List of generated alerts
        """
        facility_alerts = []
        
        for medicine in medicines:
            medicine_id = medicine['medicine_id']
            medicine_name = medicine['medicine_name']
            
            # Get forecast and usage stats
            forecast = forecasts.get(medicine_id, [20] * 7)
            daily_usage = usage_stats.get(f'{medicine_id}_mean', 20)
            
            # Check shortage risk
            shortage_risk, shortage_prob = self.check_shortage_risk(
                forecast, medicine['current_stock']
            )
            if shortage_risk:
                alert = self.generate_shortage_alert(
                    facility_id, medicine_id, medicine_name,
                    forecast, medicine['current_stock'], shortage_prob
                )
                facility_alerts.append(alert)
            
            # Check low stock
            is_low, severity = self.check_low_stock(
                medicine['current_stock'], daily_usage
            )
            if is_low:
                alert = self.generate_low_stock_alert(
                    facility_id, medicine_id, medicine_name,
                    medicine['current_stock'], daily_usage, severity
                )
                facility_alerts.append(alert)
        
        return facility_alerts
    
    def filter_priority_alerts(self, alerts: List[Alert],
                             critical_only: bool = False) -> List[Alert]:
        """Filter alerts by priority"""
        if critical_only:
            return [a for a in alerts if a.severity == 'critical']
        else:
            # Sort by severity
            severity_order = {'critical': 0, 'warning': 1, 'info': 2}
            return sorted(
                alerts,
                key=lambda x: (severity_order[x.severity], -x.confidence)
            )
    
    def generate_alert_report(self, alerts: List[Alert]) -> Dict:
        """Generate summary report of all alerts"""
        return {
            'total_alerts': len(alerts),
            'critical_alerts': sum(1 for a in alerts if a.severity == 'critical'),
            'warning_alerts': sum(1 for a in alerts if a.severity == 'warning'),
            'info_alerts': sum(1 for a in alerts if a.severity == 'info'),
            'by_type': {
                'shortage': sum(1 for a in alerts if a.alert_type == 'shortage'),
                'low_stock': sum(1 for a in alerts if a.alert_type == 'low_stock'),
                'expiry': sum(1 for a in alerts if a.alert_type == 'expiry'),
            },
            'affected_facilities': len(set(a.facility_id for a in alerts)),
            'affected_medicines': len(set(a.medicine_id for a in alerts)),
            'critical_actions_needed': [
                a for a in alerts if a.severity == 'critical'
            ][:5]  # Top 5
        }
