"""
Optimize medicine redistribution between facilities
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class RedistributionPlan:
    """Plan for medicine redistribution"""
    medicine_id: str
    medicine_name: str
    source_facility: str
    destination_facility: str
    quantity: int
    reason: str  # 'shortage_prevention', 'expiry_prevention', 'rebalance'
    priority: int  # 1-5, 1 is highest

class RedistributionOptimizer:
    """Optimize redistribution of medicines between facilities"""
    
    def __init__(self):
        """Initialize optimizer"""
        self.redistribution_plans = []
    
    @staticmethod
    def calculate_facility_balance(inventory_df: pd.DataFrame,
                                  usage_stats: Dict[str, float]) -> Dict:
        """
        Calculate balance score for each facility
        
        Args:
            inventory_df: Current inventory data
            usage_stats: Usage statistics by medicine
        
        Returns:
            Dictionary with balance scores
        """
        balance = {}
        
        for facility_id in inventory_df['facility_id'].unique():
            facility_inv = inventory_df[inventory_df['facility_id'] == facility_id]
            
            # Calculate days of supply per medicine
            supply_days = []
            for _, row in facility_inv.iterrows():
                medicine_id = row['medicine_id']
                daily_usage = usage_stats.get(medicine_id, 20)
                days = row['current_stock'] / daily_usage if daily_usage > 0 else 0
                supply_days.append(days)
            
            # Balance score: variance of supply days (lower is better)
            if len(supply_days) > 1:
                balance[facility_id] = {
                    'mean_days_supply': np.mean(supply_days),
                    'std_days_supply': np.std(supply_days),
                    'min_days_supply': np.min(supply_days),
                    'max_days_supply': np.max(supply_days),
                }
            else:
                balance[facility_id] = {
                    'mean_days_supply': supply_days[0] if supply_days else 0,
                    'std_days_supply': 0,
                    'min_days_supply': supply_days[0] if supply_days else 0,
                    'max_days_supply': supply_days[0] if supply_days else 0,
                }
        
        return balance
    
    def find_redistribution_pairs(self,
                                 inventory_df: pd.DataFrame,
                                 usage_stats: Dict[str, float],
                                 min_stock_threshold: int = 10) -> List[Tuple]:
        """
        Find optimal pairs for medicine redistribution
        
        Args:
            inventory_df: Current inventory
            usage_stats: Usage statistics
            min_stock_threshold: Minimum stock level
        
        Returns:
            List of (source_facility, dest_facility, medicine_id, quantity) tuples
        """
        redistribution_pairs = []
        
        # Group by medicine
        for medicine_id in inventory_df['medicine_id'].unique():
            med_inv = inventory_df[
                inventory_df['medicine_id'] == medicine_id
            ].copy()
            
            daily_usage = usage_stats.get(medicine_id, 20)
            
            # Sort facilities by current stock
            med_inv = med_inv.sort_values('current_stock', ascending=False)
            
            facilities = med_inv.to_dict('records')
            
            # Find low-stock facilities
            for i, dest_fac in enumerate(facilities):
                if dest_fac['current_stock'] < min_stock_threshold:
                    # Find surplus facilities
                    for j in range(i):
                        source_fac = facilities[j]
                        
                        # Calculate transfer quantity
                        avg_stock = np.mean(med_inv['current_stock'])
                        transfer_qty = min(
                            source_fac['current_stock'] - int(avg_stock * 0.7),
                            int(avg_stock * 0.3)
                        )
                        
                        if transfer_qty > 0:
                            redistribution_pairs.append((
                                source_fac['facility_id'],
                                dest_fac['facility_id'],
                                medicine_id,
                                transfer_qty
                            ))
        
        return redistribution_pairs
    
    def create_redistribution_plan(self,
                                  inventory_df: pd.DataFrame,
                                  usage_stats: Dict[str, float],
                                  expiry_alerts: List = None,
                                  shortage_alerts: List = None) -> List[RedistributionPlan]:
        """
        Create comprehensive redistribution plan
        
        Args:
            inventory_df: Current inventory
            usage_stats: Usage statistics
            expiry_alerts: List of expiry alerts
            shortage_alerts: List of shortage risk alerts
        
        Returns:
            List of RedistributionPlan objects
        """
        plans = []
        
        # Process expiry risks first (highest priority)
        if expiry_alerts:
            for alert in expiry_alerts:
                if alert.alert_level == 'critical':
                    # Find facilities with high usage of this medicine
                    med_facilities = inventory_df[
                        inventory_df['medicine_id'] == alert.medicine_id
                    ]
                    
                    # Sort by current stock (ascending) to find low-stock destinations
                    candidates = med_facilities.sort_values('current_stock').to_dict('records')
                    
                    if len(candidates) > 1:
                        # Transfer to facility with lowest stock
                        source = alert
                        dest = candidates[0]
                        
                        # Calculate transfer quantity (don't over-transfer)
                        transfer_qty = min(
                            int(source.current_stock * 0.5),
                            int(usage_stats.get(alert.medicine_id, 20) * 7)
                        )
                        
                        if transfer_qty > 0:
                            plan = RedistributionPlan(
                                medicine_id=alert.medicine_id,
                                medicine_name=alert.medicine_name,
                                source_facility=alert.facility_id,
                                destination_facility=dest['facility_id'],
                                quantity=transfer_qty,
                                reason='expiry_prevention',
                                priority=1
                            )
                            plans.append(plan)
        
        # Process shortage risks
        if shortage_alerts:
            for alert in shortage_alerts:
                # Find facilities with surplus stock of this medicine
                med_inv = inventory_df[
                    inventory_df['medicine_id'] == alert.medicine_id
                ]
                
                surplus_facilities = med_inv[
                    med_inv['current_stock'] > 
                    usage_stats.get(alert.medicine_id, 20) * 14
                ]
                
                if len(surplus_facilities) > 0:
                    source = surplus_facilities.iloc[0]
                    
                    # Calculate transfer quantity
                    daily_usage = usage_stats.get(alert.medicine_id, 20)
                    transfer_qty = int(daily_usage * 7)
                    
                    if transfer_qty > 0 and source['current_stock'] > transfer_qty:
                        plan = RedistributionPlan(
                            medicine_id=alert.medicine_id,
                            medicine_name=alert.medicine_name,
                            source_facility=source['facility_id'],
                            destination_facility=alert.facility_id,
                            quantity=transfer_qty,
                            reason='shortage_prevention',
                            priority=2
                        )
                        plans.append(plan)
        
        # Sort by priority
        self.redistribution_plans = sorted(plans, key=lambda x: x.priority)
        return self.redistribution_plans
    
    def estimate_impact(self, plans: List[RedistributionPlan]) -> Dict:
        """
        Estimate impact of redistribution plan
        
        Args:
            plans: List of redistribution plans
        
        Returns:
            Impact metrics dictionary
        """
        if not plans:
            return {
                'total_units_redistributed': 0,
                'units_for_expiry_prevention': 0,
                'units_for_shortage_prevention': 0,
                'shortage_risk_reduction': 0,
                'waste_reduction': 0,
                'number_of_transfers': 0,
                'affected_facilities': 0
            }
        
        total_units = sum(p.quantity for p in plans)
        
        expiry_prevention = sum(
            p.quantity for p in plans if p.reason == 'expiry_prevention'
        )
        shortage_prevention = sum(
            p.quantity for p in plans if p.reason == 'shortage_prevention'
        )
        
        return {
            'total_units_redistributed': total_units,
            'units_for_expiry_prevention': expiry_prevention,
            'units_for_shortage_prevention': shortage_prevention,
            'shortage_risk_reduction': min(1.0, shortage_prevention / max(1, total_units)),
            'waste_reduction': expiry_prevention,
            'number_of_transfers': len(plans),
            'affected_facilities': len(set(
                p.source_facility for p in plans
            ) | set(p.destination_facility for p in plans))
        }
