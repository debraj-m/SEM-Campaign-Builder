import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BidOptimizer:
    """Advanced bid optimization and CPA calculations"""
    
    def __init__(self, conversion_rate: float = None, target_roas: float = None):
        self.conversion_rate = conversion_rate or 0.02  # Default 2%
        self.target_roas = target_roas or 400  # Default 400%
        
    def calculate_target_cpa(self, avg_order_value: float, profit_margin: float = 0.3) -> float:
        """Calculate target CPA based on business metrics"""
        
        # Target CPA = (AOV * Profit Margin * Target ROAS%) / 100
        target_cpa = (avg_order_value * profit_margin * (self.target_roas / 100)) / 100
        
        return round(target_cpa, 2)
    
    def calculate_max_cpc(self, target_cpa: float, conversion_rate: float = None) -> float:
        """Calculate maximum CPC based on target CPA and conversion rate"""
        
        conv_rate = conversion_rate or self.conversion_rate
        
        if conv_rate <= 0:
            logger.warning("Invalid conversion rate, using default")
            conv_rate = 0.02
        
        max_cpc = target_cpa * conv_rate
        
        return round(max_cpc, 2)
    
    def optimize_keyword_bids(self, keywords: List[Dict], 
                             total_budget: float,
                             avg_order_value: float = 100,
                             profit_margin: float = 0.3) -> List[Dict]:
        """Optimize bids for a list of keywords based on performance potential"""
        
        target_cpa = self.calculate_target_cpa(avg_order_value, profit_margin)
        
        optimized_keywords = []
        
        for keyword in keywords:
            # Get keyword metrics
            search_volume = keyword.get('avg_monthly_searches', 0)
            competition_index = keyword.get('competition_index', 50)
            performance_score = keyword.get('performance_score', 50)
            
            # Market CPC range
            low_market_cpc = keyword.get('low_top_page_bid', 0)
            high_market_cpc = keyword.get('high_top_page_bid', 0)
            avg_market_cpc = (low_market_cpc + high_market_cpc) / 2 if both_exist(low_market_cpc, high_market_cpc) else 1.0
            
            # Calculate theoretical max CPC
            theoretical_max_cpc = self.calculate_max_cpc(target_cpa)
            
            # Performance-based bid adjustment
            performance_multiplier = self._get_performance_multiplier(performance_score)
            
            # Competition-based adjustment
            competition_multiplier = self._get_competition_multiplier(competition_index)
            
            # Volume-based adjustment (higher volume = potentially higher bid)
            volume_multiplier = self._get_volume_multiplier(search_volume)
            
            # Calculate optimized bid
            base_bid = min(avg_market_cpc, theoretical_max_cpc)
            optimized_bid = base_bid * performance_multiplier * competition_multiplier * volume_multiplier
            
            # Apply bounds
            min_bid = 0.25
            max_bid = min(theoretical_max_cpc * 1.2, high_market_cpc * 1.1) if high_market_cpc > 0 else theoretical_max_cpc
            
            final_bid = max(min_bid, min(optimized_bid, max_bid))
            
            # Calculate projections
            projected_clicks = self._estimate_clicks(search_volume, final_bid, avg_market_cpc)
            projected_conversions = projected_clicks * self.conversion_rate
            projected_cost = projected_clicks * final_bid
            projected_cpa = projected_cost / projected_conversions if projected_conversions > 0 else 0
            
            optimized_keyword = keyword.copy()
            optimized_keyword.update({
                'optimized_cpc': round(final_bid, 2),
                'market_avg_cpc': round(avg_market_cpc, 2),
                'theoretical_max_cpc': round(theoretical_max_cpc, 2),
                'bid_strategy': self._get_bid_strategy(performance_score, competition_index),
                'projections': {
                    'monthly_clicks': round(projected_clicks),
                    'monthly_conversions': round(projected_conversions, 1),
                    'monthly_cost': round(projected_cost, 2),
                    'projected_cpa': round(projected_cpa, 2)
                },
                'optimization_notes': self._get_optimization_notes(
                    performance_score, competition_index, final_bid, avg_market_cpc
                )
            })
            
            optimized_keywords.append(optimized_keyword)
        
        # Budget allocation optimization
        optimized_keywords = self._optimize_budget_allocation(optimized_keywords, total_budget)
        
        return optimized_keywords
    
    def _get_performance_multiplier(self, performance_score: float) -> float:
        """Get bid multiplier based on keyword performance score"""
        
        if performance_score >= 90:
            return 1.15  # Bid 15% higher for top performers
        elif performance_score >= 80:
            return 1.10
        elif performance_score >= 70:
            return 1.05
        elif performance_score >= 50:
            return 1.0   # Market rate
        elif performance_score >= 30:
            return 0.90
        else:
            return 0.80  # Bid 20% lower for poor performers
    
    def _get_competition_multiplier(self, competition_index: float) -> float:
        """Get bid multiplier based on competition level"""
        
        if competition_index <= 20:
            return 0.85  # Lower bids in low competition
        elif competition_index <= 40:
            return 0.95
        elif competition_index <= 60:
            return 1.0   # Market rate
        elif competition_index <= 80:
            return 1.05  # Slightly higher in high competition
        else:
            return 1.10  # 10% higher in very high competition
    
    def _get_volume_multiplier(self, search_volume: int) -> float:
        """Get bid multiplier based on search volume"""
        
        if search_volume >= 10000:
            return 1.05  # Higher bids for high volume
        elif search_volume >= 5000:
            return 1.02
        elif search_volume >= 1000:
            return 1.0   # Standard
        elif search_volume >= 500:
            return 0.98
        else:
            return 0.95  # Lower bids for low volume
    
    def _estimate_clicks(self, search_volume: int, bid_cpc: float, market_cpc: float) -> float:
        """Estimate monthly clicks based on bid competitiveness"""
        
        if market_cpc <= 0:
            market_cpc = 1.0
        
        # Bid competitiveness ratio
        bid_ratio = bid_cpc / market_cpc
        
        # Estimate impression share based on bid ratio
        if bid_ratio >= 1.2:
            impression_share = 0.8  # 80% impression share
        elif bid_ratio >= 1.0:
            impression_share = 0.6  # 60% impression share
        elif bid_ratio >= 0.8:
            impression_share = 0.4  # 40% impression share
        else:
            impression_share = 0.2  # 20% impression share
        
        # Estimate CTR (simplified model)
        estimated_ctr = 0.02  # 2% base CTR
        
        # Calculate clicks
        estimated_impressions = search_volume * impression_share
        estimated_clicks = estimated_impressions * estimated_ctr
        
        return estimated_clicks
    
    def _get_bid_strategy(self, performance_score: float, competition_index: float) -> str:
        """Recommend bid strategy based on keyword characteristics"""
        
        if performance_score >= 80 and competition_index <= 40:
            return "Aggressive - High performance, low competition"
        elif performance_score >= 70 and competition_index <= 60:
            return "Moderate - Good performance, medium competition"
        elif performance_score >= 50:
            return "Conservative - Average performance"
        elif competition_index >= 80:
            return "Cautious - High competition market"
        else:
            return "Low priority - Poor performance indicators"
    
    def _get_optimization_notes(self, performance_score: float, competition_index: float, 
                              final_bid: float, market_cpc: float) -> str:
        """Generate optimization notes for the keyword"""
        
        notes = []
        
        if final_bid > market_cpc * 1.1:
            notes.append("Bidding above market average for competitive advantage")
        elif final_bid < market_cpc * 0.9:
            notes.append("Conservative bid to maintain profitability")
        
        if performance_score >= 80:
            notes.append("High-performing keyword - monitor closely")
        elif performance_score <= 40:
            notes.append("Low performance - consider for optimization or removal")
        
        if competition_index >= 80:
            notes.append("High competition - expect higher CPCs")
        
        return "; ".join(notes) if notes else "Standard optimization applied"
    
    def _optimize_budget_allocation(self, keywords: List[Dict], total_budget: float) -> List[Dict]:
        """Optimize budget allocation across keywords"""
        
        # Calculate total projected cost
        total_projected_cost = sum(kw['projections']['monthly_cost'] for kw in keywords)
        
        if total_projected_cost <= total_budget:
            # Budget is sufficient - no adjustment needed
            for kw in keywords:
                kw['budget_allocation'] = kw['projections']['monthly_cost']
                kw['budget_utilization'] = 'Full'
        else:
            # Budget constraint - allocate proportionally based on performance
            total_performance_score = sum(kw.get('performance_score', 50) for kw in keywords)
            
            for kw in keywords:
                performance_weight = kw.get('performance_score', 50) / total_performance_score
                allocated_budget = total_budget * performance_weight
                
                kw['budget_allocation'] = round(allocated_budget, 2)
                kw['budget_utilization'] = 'Constrained'
                
                # Recalculate projections based on allocated budget
                if kw['optimized_cpc'] > 0:
                    adjusted_clicks = allocated_budget / kw['optimized_cpc']
                    adjusted_conversions = adjusted_clicks * self.conversion_rate
                    
                    kw['projections'].update({
                        'monthly_clicks': round(adjusted_clicks),
                        'monthly_conversions': round(adjusted_conversions, 1),
                        'monthly_cost': allocated_budget
                    })
        
        return keywords
    
    def generate_bid_recommendations_report(self, optimized_keywords: List[Dict]) -> Dict:
        """Generate comprehensive bid recommendations report"""
        
        # Overall statistics
        total_keywords = len(optimized_keywords)
        total_budget = sum(kw.get('budget_allocation', 0) for kw in optimized_keywords)
        total_projected_clicks = sum(kw['projections']['monthly_clicks'] for kw in optimized_keywords)
        total_projected_conversions = sum(kw['projections']['monthly_conversions'] for kw in optimized_keywords)
        
        avg_cpc = sum(kw['optimized_cpc'] for kw in optimized_keywords) / total_keywords
        avg_projected_cpa = total_budget / total_projected_conversions if total_projected_conversions > 0 else 0
        
        # Performance distribution
        high_performers = [kw for kw in optimized_keywords if kw.get('performance_score', 0) >= 70]
        medium_performers = [kw for kw in optimized_keywords if 40 <= kw.get('performance_score', 0) < 70]
        low_performers = [kw for kw in optimized_keywords if kw.get('performance_score', 0) < 40]
        
        # Bid strategy distribution
        strategy_distribution = {}
        for kw in optimized_keywords:
            strategy = kw.get('bid_strategy', 'Unknown')
            strategy_distribution[strategy] = strategy_distribution.get(strategy, 0) + 1
        
        report = {
            'summary': {
                'total_keywords': total_keywords,
                'total_monthly_budget': round(total_budget, 2),
                'average_cpc': round(avg_cpc, 2),
                'projected_monthly_clicks': round(total_projected_clicks),
                'projected_monthly_conversions': round(total_projected_conversions, 1),
                'projected_average_cpa': round(avg_projected_cpa, 2)
            },
            'performance_breakdown': {
                'high_performers': len(high_performers),
                'medium_performers': len(medium_performers), 
                'low_performers': len(low_performers)
            },
            'strategy_distribution': strategy_distribution,
            'top_opportunities': sorted(
                optimized_keywords, 
                key=lambda x: x.get('performance_score', 0), 
                reverse=True
            )[:10],
            'optimization_priorities': self._identify_optimization_priorities(optimized_keywords)
        }
        
        return report
    
    def _identify_optimization_priorities(self, keywords: List[Dict]) -> List[str]:
        """Identify key optimization priorities"""
        
        priorities = []
        
        # High volume, low performance keywords
        high_vol_low_perf = [
            kw for kw in keywords 
            if kw.get('avg_monthly_searches', 0) >= 1000 and kw.get('performance_score', 0) <= 50
        ]
        if high_vol_low_perf:
            priorities.append(f"Optimize {len(high_vol_low_perf)} high-volume, low-performing keywords")
        
        # High CPC keywords
        high_cpc = [kw for kw in keywords if kw.get('optimized_cpc', 0) >= 5.0]
        if high_cpc:
            priorities.append(f"Monitor {len(high_cpc)} high-CPC keywords for efficiency")
        
        # Budget-constrained keywords
        constrained = [kw for kw in keywords if kw.get('budget_utilization') == 'Constrained']
        if constrained:
            priorities.append(f"Consider budget increase for {len(constrained)} constrained keywords")
        
        # Low competition opportunities
        low_comp_high_perf = [
            kw for kw in keywords 
            if kw.get('competition_index', 100) <= 30 and kw.get('performance_score', 0) >= 70
        ]
        if low_comp_high_perf:
            priorities.append(f"Capitalize on {len(low_comp_high_perf)} low-competition, high-performance opportunities")
        
        return priorities

def both_exist(val1, val2):
    """Helper function to check if both values exist and are greater than 0"""
    return val1 and val2 and val1 > 0 and val2 > 0
