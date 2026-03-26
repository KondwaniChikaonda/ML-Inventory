"""
Analytics and reporting for hospital supply chain system
"""

import pandas as pd
import numpy as np
from typing import Dict, List
from datetime import datetime

class SupplyChainAnalytics:
    """Generate analytics and insights for supply chain management"""
    
    @staticmethod
    def calculate_key_metrics(usage_df: pd.DataFrame,
                            inventory_df: pd.DataFrame,
                            forecasts: Dict) -> Dict:
        """
        Calculate key performance indicators
        
        Args:
            usage_df: Historical usage data
            inventory_df: Current inventory
            forecasts: Demand forecasts
        
        Returns:
            Dictionary of KPIs
        """
        metrics = {}
        
        # Overall metrics
        metrics['total_unique_medicines'] = len(inventory_df['medicine_id'].unique())
        metrics['total_unique_facilities'] = len(inventory_df['facility_id'].unique())
        metrics['total_stock_value'] = inventory_df['current_stock'].sum()
        
        # Usage metrics
        metrics['avg_daily_usage'] = usage_df['units_used'].mean()
        metrics['total_usage_period'] = usage_df['units_used'].sum()
        metrics['usage_volatility'] = usage_df['units_used'].std()
        
        # Forecast metrics
        total_forecasted = sum(
            np.sum(forecast) for forecast in forecasts.values()
        )
        metrics['total_forecasted_demand'] = total_forecasted
        metrics['avg_forecasted_daily_demand'] = (
            total_forecasted / len(forecasts) / 7 if forecasts else 0
        )
        
        # Stock coverage
        avg_daily = metrics['avg_daily_usage']
        if avg_daily > 0:
            metrics['days_of_supply'] = metrics['total_stock_value'] / avg_daily
        else:
            metrics['days_of_supply'] = 0
        
        return metrics
    
    @staticmethod
    def facility_performance_analysis(usage_df: pd.DataFrame,
                                     inventory_df: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze performance by facility
        
        Args:
            usage_df: Usage history
            inventory_df: Current inventory
        
        Returns:
            DataFrame with facility metrics
        """
        facility_stats = []
        
        for facility_id in usage_df['facility_id'].unique():
            fac_usage = usage_df[usage_df['facility_id'] == facility_id]
            fac_inventory = inventory_df[inventory_df['facility_id'] == facility_id]
            
            stats = {
                'facility_id': facility_id,
                'total_medications': len(fac_inventory),
                'avg_daily_usage': fac_usage['units_used'].mean(),
                'total_current_stock': fac_inventory['current_stock'].sum(),
                'days_of_supply': (
                    fac_inventory['current_stock'].sum() / fac_usage['units_used'].mean()
                    if fac_usage['units_used'].mean() > 0 else 0
                ),
                'expiring_soon': len(fac_inventory[
                    pd.to_datetime(fac_inventory['expiry_date']) <
                    pd.Timestamp.now() + pd.Timedelta(days=14)
                ]),
                'utilization_rate': (
                    fac_usage['units_used'].mean() / 
                    (fac_inventory['current_stock'].sum() / 
                    len(fac_inventory) if len(fac_inventory) > 0 else 1)
                ) if len(fac_inventory) > 0 else 0
            }
            
            facility_stats.append(stats)
        
        return pd.DataFrame(facility_stats)
    
    @staticmethod
    def medicine_demand_analysis(usage_df: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze demand patterns for each medicine
        
        Args:
            usage_df: Usage history
        
        Returns:
            DataFrame with medicine demand metrics
        """
        medicine_stats = []
        
        for medicine_id in usage_df['medicine_id'].unique():
            med_usage = usage_df[usage_df['medicine_id'] == medicine_id]
            
            stats = {
                'medicine_id': medicine_id,
                'medicine_name': med_usage['medicine_name'].iloc[0],
                'total_usage': med_usage['units_used'].sum(),
                'avg_daily_usage': med_usage['units_used'].mean(),
                'max_daily_usage': med_usage['units_used'].max(),
                'min_daily_usage': med_usage['units_used'].min(),
                'usage_std': med_usage['units_used'].std(),
                'usage_cv': (
                    med_usage['units_used'].std() / med_usage['units_used'].mean()
                    if med_usage['units_used'].mean() > 0 else 0
                ),
                'num_facilities_using': med_usage['facility_id'].nunique()
            }
            
            medicine_stats.append(stats)
        
        return pd.DataFrame(medicine_stats)
    
    @staticmethod
    def generate_summary_report(all_alerts: List, 
                               redistribution_impact: Dict,
                               key_metrics: Dict) -> Dict:
        """
        Generate comprehensive summary report
        
        Args:
            all_alerts: List of all alerts (mix of Alert and ExpiryAlert)
            redistribution_impact: Impact of redistribution plans
            key_metrics: Key performance indicators
        
        Returns:
            Comprehensive report dictionary
        """
        # Count different types of alerts, handling both Alert and ExpiryAlert
        critical_count = 0
        warning_count = 0
        info_count = 0
        
        for alert in all_alerts:
            # Handle both Alert (severity) and ExpiryAlert (alert_level)
            severity = getattr(alert, 'severity', getattr(alert, 'alert_level', 'info'))
            if severity == 'critical':
                critical_count += 1
            elif severity == 'warning':
                warning_count += 1
            else:
                info_count += 1
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'system_health': {
                'total_medicines': key_metrics.get('total_unique_medicines', 0),
                'total_facilities': key_metrics.get('total_unique_facilities', 0),
                'days_of_supply': round(key_metrics.get('days_of_supply', 0), 2),
                'total_stock_units': int(key_metrics.get('total_stock_value', 0)),
            },
            'alert_summary': {
                'total_alerts': len(all_alerts),
                'critical_alerts': critical_count,
                'warning_alerts': warning_count,
                'shortage_risks': sum(1 for a in all_alerts if getattr(a, 'alert_type', None) == 'shortage'),
                'expiry_risks': sum(1 for a in all_alerts if getattr(a, 'alert_type', None) == 'expiry' or hasattr(a, 'batch_id')),
            },
            'redistribution_impact': redistribution_impact,
            'forecast_metrics': {
                'avg_daily_demand': round(
                    key_metrics.get('avg_forecasted_daily_demand', 0), 2
                ),
                'total_forecasted': int(key_metrics.get('total_forecasted_demand', 0)),
            },
            'recommendations': SupplyChainAnalytics._generate_recommendations(
                all_alerts, key_metrics
            )
        }
        
        return report
    
    @staticmethod
    def _generate_recommendations(all_alerts: List, 
                                 key_metrics: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Check supply levels
        days_supply = key_metrics.get('days_of_supply', 0)
        if days_supply < 7:
            recommendations.append(
                f"Critical: Inventory covers only {days_supply:.1f} days of demand. "
                "Increase procurement immediately."
            )
        elif days_supply < 14:
            recommendations.append(
                f"Warning: Inventory covers {days_supply:.1f} days of demand. "
                "Plan ahead for procurement."
            )
        
        # Critical alerts
        critical_count = sum(1 for a in all_alerts 
                            if getattr(a, 'severity', getattr(a, 'alert_level', 'info')) == 'critical')
        if critical_count > 0:
            recommendations.append(
                f"Action Required: {critical_count} critical alerts need immediate attention."
            )
        
        # Expiry management
        expiry_alerts = [a for a in all_alerts if hasattr(a, 'batch_id')]
        if len(expiry_alerts) > 0:
            recommendations.append(
                f"Redistribute {len(expiry_alerts)} batches with expiry risk to "
                "high-demand facilities to prevent waste."
            )
        
        # Shortage prevention
        shortage_alerts = [a for a in all_alerts if getattr(a, 'alert_type', None) == 'shortage']
        if len(shortage_alerts) > 0:
            recommendations.append(
                f"Address {len(shortage_alerts)} shortage risks through redistribution "
                "and/or emergency procurement."
            )
        
        return recommendations if recommendations else ["All systems operating normally."]
