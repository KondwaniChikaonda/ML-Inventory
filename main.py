"""
Main orchestration script for hospital supply chain ML system
Integrates demand forecasting, expiry tracking, and alert generation
"""

import sys
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import (
    FORECAST_HORIZON,
    LOOKBACK_PERIOD,
    EXPIRY_WARNING_DAYS,
    CRITICAL_EXPIRY_DAYS,
    SHORTAGE_PROBABILITY_THRESHOLD,
)

from utils import (
    SupplyDataLoader,
    DemandForecaster,
    ExpiryTracker,
    AlertSystem,
    RedistributionOptimizer,
    SupplyChainAnalytics
)


class HospitalSupplyChainSystem:
    """Main orchestration system for hospital supply chain management"""
    
    def __init__(self):
        """Initialize the system"""
        self.data_loader = SupplyDataLoader()
        self.forecaster = DemandForecaster(forecast_horizon=FORECAST_HORIZON)
        self.expiry_tracker = ExpiryTracker(
            warning_days=EXPIRY_WARNING_DAYS,
            critical_days=CRITICAL_EXPIRY_DAYS
        )
        self.alert_system = AlertSystem()
        self.optimizer = RedistributionOptimizer()
        self.analytics = SupplyChainAnalytics()
        
        self.usage_data = None
        self.inventory_data = None
        self.forecasts = {}
        self.all_alerts = []
        self.redistribution_plans = []
    
    def load_data(self, sample: bool = True):
        """
        Load data (sample for demo or from CSV)
        
        Args:
            sample: If True, generate sample data for demonstration
        """
        print("Loading data...")
        
        if sample:
            print("  - Generating sample usage data...")
            self.usage_data = self.data_loader.generate_sample_usage_data(
                days=90, facilities=5, medicines_per_facility=10
            )
            
            print("  - Generating sample inventory data...")
            self.inventory_data = self.data_loader.generate_sample_inventory_data(
                facilities=5, medicines_per_facility=10
            )
        else:
            try:
                self.usage_data = self.data_loader.load_csv_data('usage_history.csv')
                self.inventory_data = self.data_loader.load_csv_data('current_inventory.csv')
            except FileNotFoundError as e:
                print(f"Error loading CSV files: {e}")
                print("Falling back to sample data...")
                self.load_data(sample=True)
        
        # Preprocess data
        print("  - Preprocessing data...")
        self.usage_data = self.data_loader.preprocess_usage_data(self.usage_data)
        
        print(f"✓ Loaded {len(self.usage_data)} usage records")
        print(f"✓ Loaded {len(self.inventory_data)} inventory items")
    
    def train_forecasting_models(self):
        """Train demand forecasting models for each medicine"""
        print("\nTraining demand forecasting models...")
        
        unique_medicines = self.usage_data['medicine_id'].unique()
        num_medicines = len(unique_medicines)
        
        for idx, medicine_id in enumerate(unique_medicines, 1):
            medicine_usage = self.usage_data[
                self.usage_data['medicine_id'] == medicine_id
            ].sort_values('date').copy()
            
            if len(medicine_usage) > 7:  # Need at least 7 data points
                # Create dedicated forecaster for this medicine
                forecaster = DemandForecaster(forecast_horizon=FORECAST_HORIZON)
                
                try:
                    forecaster.train(medicine_usage, window=7)
                    self.forecasts[medicine_id] = {
                        'model': forecaster,
                        'forecast': forecaster.forecast(medicine_usage)
                    }
                    
                    if idx % 5 == 0:
                        print(f"  - Trained {idx}/{num_medicines} models...")
                except Exception as e:
                    print(f"  - Warning: Could not train model for {medicine_id}: {e}")
        
        print(f"✓ Trained {len(self.forecasts)} demand forecasting models")
    
    def generate_alerts(self):
        """Generate all alerts (shortage, low stock, expiry)"""
        print("\nGenerating alerts...")
        
        # Calculate usage statistics
        usage_stats = {}
        for medicine_id in self.usage_data['medicine_id'].unique():
            med_usage = self.usage_data[self.usage_data['medicine_id'] == medicine_id]['units_used']
            usage_stats[medicine_id] = float(med_usage.mean())
        
        # Track expiry
        print("  - Tracking expiry dates...")
        expiry_alerts = self.expiry_tracker.track_inventory(
            self.inventory_data, usage_stats
        )
        self.all_alerts.extend(expiry_alerts)
        
        # Generate demand alerts
        print("  - Checking shortage risks...")
        for facility_id in self.inventory_data['facility_id'].unique():
            facility_inventory = self.inventory_data[
                self.inventory_data['facility_id'] == facility_id
            ]
            
            for _, medicine in facility_inventory.iterrows():
                medicine_id = medicine['medicine_id']
                
                if medicine_id in self.forecasts:
                    forecast = self.forecasts[medicine_id]['forecast']
                    daily_usage = usage_stats.get(medicine_id, 20)
                    
                    # Check shortage risk
                    shortage_risk, shortage_prob = self.alert_system.check_shortage_risk(
                        forecast, medicine['current_stock']
                    )
                    
                    if shortage_risk and shortage_prob > SHORTAGE_PROBABILITY_THRESHOLD:
                        alert = self.alert_system.generate_shortage_alert(
                            facility_id,
                            medicine_id,
                            medicine['medicine_name'],
                            forecast,
                            medicine['current_stock'],
                            shortage_prob
                        )
                        self.all_alerts.append(alert)
                    
                    # Check low stock
                    is_low, severity = self.alert_system.check_low_stock(
                        medicine['current_stock'], daily_usage
                    )
                    
                    if is_low:
                        alert = self.alert_system.generate_low_stock_alert(
                            facility_id,
                            medicine_id,
                            medicine['medicine_name'],
                            medicine['current_stock'],
                            daily_usage,
                            severity
                        )
                        self.all_alerts.append(alert)
        
        print(f"✓ Generated {len(self.all_alerts)} alerts")
    
    def optimize_redistribution(self):
        """Optimize medicine redistribution between facilities"""
        print("\nOptimizing redistribution...")
        
        # Calculate usage statistics
        usage_stats = {}
        for medicine_id in self.usage_data['medicine_id'].unique():
            med_usage = self.usage_data[self.usage_data['medicine_id'] == medicine_id]['units_used']
            usage_stats[medicine_id] = float(med_usage.mean())
        
        # Create redistribution plans
        # Filter for shortage alerts only (not ExpiryAlerts)
        shortage_alerts = [a for a in self.all_alerts if hasattr(a, 'alert_type') and a.alert_type == 'shortage']
        
        self.redistribution_plans = self.optimizer.create_redistribution_plan(
            self.inventory_data,
            usage_stats,
            expiry_alerts=None,
            shortage_alerts=shortage_alerts
        )
        
        print(f"✓ Created {len(self.redistribution_plans)} redistribution plans")
    
    def generate_insights(self) -> dict:
        """Generate comprehensive analytics and insights"""
        print("\nGenerating insights...")
        
        # Calculate metrics
        usage_stats = self.usage_data.groupby('medicine_id')['units_used'].mean().to_dict()
        key_metrics = self.analytics.calculate_key_metrics(
            self.usage_data,
            self.inventory_data,
            {mid: forecast['forecast'] for mid, forecast in self.forecasts.items()}
        )
        
        # Facility analysis
        facility_perf = self.analytics.facility_performance_analysis(
            self.usage_data, self.inventory_data
        )
        
        # Medicine analysis
        medicine_demand = self.analytics.medicine_demand_analysis(self.usage_data)
        
        # Redistribution impact
        redistribution_impact = self.optimizer.estimate_impact(
            self.redistribution_plans
        )
        
        # Generate summary report
        report = self.analytics.generate_summary_report(
            self.all_alerts,
            redistribution_impact,
            key_metrics
        )
        
        return {
            'key_metrics': key_metrics,
            'facility_performance': facility_perf,
            'medicine_demand': medicine_demand,
            'summary_report': report,
            'redistribution_impact': redistribution_impact
        }
    
    def run_full_analysis(self):
        """Execute complete analysis pipeline"""
        print("=" * 70)
        print("HOSPITAL SUPPLY CHAIN ML SYSTEM")
        print("=" * 70)
        print(f"Analysis started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        try:
            # Load data
            self.load_data(sample=True)
            
            # Train models
            self.train_forecasting_models()
            
            # Generate alerts
            self.generate_alerts()
            
            # Optimize redistribution
            self.optimize_redistribution()
            
            # Generate insights
            insights = self.generate_insights()
            
            # Display results
            self.display_results(insights)
            
            print("\n" + "=" * 70)
            print("Analysis completed successfully!")
            print("=" * 70)
            
            return {
                'status': 'success',
                'alerts': self.all_alerts,
                'redistribution_plans': self.redistribution_plans,
                'insights': insights
            }
        
        except Exception as e:
            print(f"\n❌ Error during analysis: {e}")
            import traceback
            traceback.print_exc()
            return {'status': 'error', 'error': str(e)}
    
    def display_results(self, insights: dict):
        """Display analysis results in console"""
        report = insights['summary_report']
        
        print("\n" + "=" * 70)
        print("SYSTEM HEALTH SUMMARY")
        print("=" * 70)
        
        health = report['system_health']
        print(f"Total Medicines:        {health['total_medicines']}")
        print(f"Total Facilities:       {health['total_facilities']}")
        print(f"Current Stock:          {health['total_stock_units']} units")
        print(f"Days of Supply:         {health['days_of_supply']:.1f} days")
        
        print("\n" + "=" * 70)
        print("ALERT SUMMARY")
        print("=" * 70)
        
        alerts = report['alert_summary']
        print(f"Total Alerts:           {alerts['total_alerts']}")
        print(f"  ├─ Critical:          {alerts['critical_alerts']}")
        print(f"  ├─ Warning:           {alerts['warning_alerts']}")
        print(f"  ├─ Shortage Risks:    {alerts['shortage_risks']}")
        print(f"  └─ Expiry Risks:      {alerts['expiry_risks']}")
        
        print("\n" + "=" * 70)
        print("REDISTRIBUTION IMPACT")
        print("=" * 70)
        
        redis = insights['redistribution_impact']
        print(f"Units Redistributed:    {redis['total_units_redistributed']}")
        print(f"Transfers Planned:      {redis['number_of_transfers']}")
        print(f"Facilities Affected:    {redis['affected_facilities']}")
        
        print("\n" + "=" * 70)
        print("TOP RECOMMENDATIONS")
        print("=" * 70)
        
        for idx, rec in enumerate(report['recommendations'], 1):
            print(f"{idx}. {rec}\n")
        
        print("=" * 70)
        print("\nTop 5 Priority Alerts:")
        print("-" * 70)
        
        critical_alerts = [a for a in self.all_alerts 
                          if getattr(a, 'severity', getattr(a, 'alert_level', 'info')) == 'critical'][:5]
        
        for idx, alert in enumerate(critical_alerts, 1):
            medicine_name = getattr(alert, 'medicine_name', 'Unknown')
            facility_id = getattr(alert, 'facility_id', 'Unknown')
            message = getattr(alert, 'message', 'No details')
            action = getattr(alert, 'recommended_action', 'Review alert')
            
            print(f"\n{idx}. '{medicine_name}' at {facility_id}")
            print(f"   Message: {message}")
            print(f"   Action: {action}")


def main():
    """Main entry point"""
    system = HospitalSupplyChainSystem()
    result = system.run_full_analysis()
    
    return result


if __name__ == "__main__":
    main()
