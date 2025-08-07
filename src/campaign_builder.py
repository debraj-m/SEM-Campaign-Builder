import pandas as pd
from typing import Dict, List, Any
import logging
from datetime import datetime
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CampaignBuilder:
    """Generate structured SEM campaign plans and exports"""
    
    def __init__(self, conversion_rate: float = 0.02):
        self.conversion_rate = conversion_rate
        
    def build_search_campaign_structure(self, ad_groups: Dict[str, Dict], 
                                      search_budget: float) -> Dict[str, Any]:
        """Build complete Search campaign structure"""
        
        campaign_structure = {
            'campaign_type': 'Search',
            'campaign_name': f'Search Campaign - {datetime.now().strftime("%Y%m%d")}',
            'total_budget': search_budget,
            'daily_budget': search_budget / 30,
            'ad_groups': [],
            'campaign_settings': {
                'network': 'Google Search',
                'location_targeting': 'As specified in input',
                'language_targeting': 'English',
                'bidding_strategy': 'Manual CPC',
                'conversion_tracking': 'Required'
            },
            'performance_projections': {}
        }
        
        total_allocation_score = sum(group['suggested_budget_allocation'] for group in ad_groups.values())
        
        for group_name, group_data in ad_groups.items():
            # Calculate budget allocation
            if total_allocation_score > 0:
                budget_percentage = group_data['suggested_budget_allocation'] / total_allocation_score
            else:
                budget_percentage = 1 / len(ad_groups)
            
            allocated_budget = search_budget * budget_percentage
            
            # Calculate projections
            total_monthly_searches = sum(kw['avg_monthly_searches'] for kw in group_data['keywords'])
            avg_cpc = sum(kw['suggested_cpc'] for kw in group_data['keywords']) / len(group_data['keywords'])
            
            estimated_clicks = min(allocated_budget / avg_cpc, total_monthly_searches * 0.1)  # Assume 10% CTR max
            estimated_conversions = estimated_clicks * self.conversion_rate
            estimated_cpa = allocated_budget / estimated_conversions if estimated_conversions > 0 else 0
            
            ad_group_structure = {
                'ad_group_name': group_name,
                'intent_category': group_data['intent'],
                'allocated_budget': round(allocated_budget, 2),
                'daily_budget': round(allocated_budget / 30, 2),
                'keywords': group_data['keywords'],
                'keyword_count': len(group_data['keywords']),
                'avg_search_volume': round(group_data['avg_search_volume']),
                'avg_competition': round(group_data['avg_competition'], 1),
                'recommended_ads': self._generate_ad_recommendations(group_data),
                'projections': {
                    'estimated_monthly_clicks': round(estimated_clicks),
                    'estimated_monthly_conversions': round(estimated_conversions, 1),
                    'estimated_cpa': round(estimated_cpa, 2),
                    'avg_cpc': round(avg_cpc, 2)
                }
            }
            
            campaign_structure['ad_groups'].append(ad_group_structure)
        
        # Calculate overall campaign projections
        total_clicks = sum(ag['projections']['estimated_monthly_clicks'] for ag in campaign_structure['ad_groups'])
        total_conversions = sum(ag['projections']['estimated_monthly_conversions'] for ag in campaign_structure['ad_groups'])
        
        campaign_structure['performance_projections'] = {
            'estimated_monthly_clicks': total_clicks,
            'estimated_monthly_conversions': round(total_conversions, 1),
            'estimated_overall_cpa': round(search_budget / total_conversions, 2) if total_conversions > 0 else 0,
            'projected_roas': round((total_conversions * 100) / search_budget, 1) if search_budget > 0 else 0  # Assume $100 avg order value
        }
        
        return campaign_structure
    
    def build_shopping_campaign_structure(self, keywords: List[Dict], 
                                        shopping_budget: float) -> Dict[str, Any]:
        """Build Shopping campaign structure with CPC recommendations"""
        
        # Filter for commercial/product-related keywords
        shopping_keywords = [
            kw for kw in keywords 
            if any(term in kw['keyword'].lower() for term in 
                  ['buy', 'purchase', 'product', 'shop', 'price', 'cost', 'cheap', 'deal'])
        ]
        
        if not shopping_keywords:
            shopping_keywords = keywords[:20]  # Use top keywords if no commercial found
        
        # Calculate target CPC based on performance
        avg_performance_score = sum(kw.get('performance_score', 50) for kw in shopping_keywords) / len(shopping_keywords)
        
        # Base CPC calculation
        avg_competitor_cpc = sum(
            (kw.get('low_top_page_bid', 0) + kw.get('high_top_page_bid', 0)) / 2 
            for kw in shopping_keywords
        ) / len(shopping_keywords)
        
        # Adjust for Shopping campaigns (typically 10-20% lower than Search)
        shopping_cpc_modifier = 0.85
        target_cpc = avg_competitor_cpc * shopping_cpc_modifier
        
        # Performance-based adjustment
        if avg_performance_score >= 80:
            target_cpc *= 1.1
        elif avg_performance_score <= 40:
            target_cpc *= 0.8
        
        # Calculate projections
        estimated_clicks = shopping_budget / target_cpc if target_cpc > 0 else 0
        estimated_conversions = estimated_clicks * self.conversion_rate
        estimated_cpa = shopping_budget / estimated_conversions if estimated_conversions > 0 else 0
        
        campaign_structure = {
            'campaign_type': 'Shopping',
            'campaign_name': f'Shopping Campaign - {datetime.now().strftime("%Y%m%d")}',
            'total_budget': shopping_budget,
            'daily_budget': shopping_budget / 30,
            'campaign_settings': {
                'campaign_subtype': 'Standard Shopping',
                'priority': 'Medium',
                'merchant_center_required': True,
                'product_feed_required': True,
                'bidding_strategy': 'Manual CPC'
            },
            'bid_recommendations': {
                'starting_cpc': round(target_cpc * 0.8, 2),  # Start conservative
                'target_cpc': round(target_cpc, 2),
                'max_cpc': round(target_cpc * 1.3, 2),
                'bid_adjustment_strategy': 'Performance-based optimization'
            },
            'targeting_keywords': [kw['keyword'] for kw in shopping_keywords[:15]],
            'product_group_suggestions': self._generate_product_groups(shopping_keywords),
            'performance_projections': {
                'estimated_monthly_clicks': round(estimated_clicks),
                'estimated_monthly_conversions': round(estimated_conversions, 1),
                'estimated_cpa': round(estimated_cpa, 2),
                'target_roas': '400%',  # Typical target for Shopping campaigns
                'break_even_roas': round((1 / self.conversion_rate) * (target_cpc / 100), 1)  # Assuming $100 AOV
            }
        }
        
        return campaign_structure
    
    def build_performance_max_structure(self, themes: List[Dict], 
                                      pmax_budget: float) -> Dict[str, Any]:
        """Build Performance Max campaign structure"""
        
        budget_per_theme = pmax_budget / len(themes) if themes else pmax_budget
        
        campaign_structure = {
            'campaign_type': 'Performance Max',
            'campaign_name': f'Performance Max Campaign - {datetime.now().strftime("%Y%m%d")}',
            'total_budget': pmax_budget,
            'daily_budget': pmax_budget / 30,
            'campaign_settings': {
                'goal': 'Sales/Conversions',
                'bidding_strategy': 'Maximize Conversions',
                'target_cpa': None,  # To be set based on account history
                'target_roas': '400%',
                'audience_signals_required': True
            },
            'asset_groups': [],
            'performance_projections': {
                'estimated_reach_increase': '15-30%',
                'cross_channel_optimization': True,
                'automated_bidding': True
            }
        }
        
        for i, theme in enumerate(themes):
            asset_group = {
                'asset_group_name': theme['theme_name'],
                'theme_type': theme['theme_type'],
                'allocated_budget': round(budget_per_theme, 2),
                'target_audience': theme['target_audience'],
                'keywords': theme['keywords'],
                'asset_requirements': {
                    'headlines': '3-15 required',
                    'descriptions': '2-5 required',
                    'images': 'Multiple sizes required',
                    'videos': 'Optional but recommended',
                    'final_url': 'Required'
                },
                'asset_focus': theme['asset_focus'],
                'audience_signals': self._generate_audience_signals(theme),
                'optimization_focus': self._get_optimization_focus(theme['theme_type'])
            }
            
            campaign_structure['asset_groups'].append(asset_group)
        
        return campaign_structure
    
    def _generate_ad_recommendations(self, group_data: Dict) -> List[Dict]:
        """Generate ad copy recommendations for ad groups"""
        
        intent = group_data['intent']
        top_keywords = sorted(group_data['keywords'], key=lambda x: x['performance_score'], reverse=True)[:3]
        
        ad_recommendations = []
        
        if intent == 'commercial':
            ad_recommendations = [
                {
                    'headline_1': f"Best {top_keywords[0]['keyword'].title()}",
                    'headline_2': "Compare Prices & Save",
                    'description': "Find the perfect solution for your needs. Free quotes available.",
                    'ad_type': 'Responsive Search Ad'
                },
                {
                    'headline_1': f"Professional {top_keywords[0]['keyword'].title()}",
                    'headline_2': "Get Started Today",
                    'description': "Trusted by thousands. See why customers choose us.",
                    'ad_type': 'Responsive Search Ad'
                }
            ]
        elif intent == 'informational':
            ad_recommendations = [
                {
                    'headline_1': f"Learn About {top_keywords[0]['keyword'].title()}",
                    'headline_2': "Free Expert Guide",
                    'description': "Everything you need to know. Download our comprehensive guide.",
                    'ad_type': 'Responsive Search Ad'
                }
            ]
        elif intent == 'local':
            ad_recommendations = [
                {
                    'headline_1': f"Local {top_keywords[0]['keyword'].title()}",
                    'headline_2': "Near You",
                    'description': "Serving your area with professional service. Call now for quote.",
                    'ad_type': 'Responsive Search Ad'
                }
            ]
        else:
            # Generic recommendations
            ad_recommendations = [
                {
                    'headline_1': f"{top_keywords[0]['keyword'].title()}",
                    'headline_2': "Quality Service",
                    'description': "Professional solutions tailored to your needs.",
                    'ad_type': 'Responsive Search Ad'
                }
            ]
        
        return ad_recommendations
    
    def _generate_product_groups(self, keywords: List[Dict]) -> List[str]:
        """Generate product group suggestions for Shopping campaigns"""
        
        # Extract potential product categories from keywords
        categories = set()
        
        for kw in keywords:
            words = kw['keyword'].lower().split()
            for word in words:
                if len(word) > 3 and word not in ['best', 'cheap', 'professional', 'buy', 'purchase']:
                    categories.add(word.title())
        
        return list(categories)[:10]  # Return top 10 categories
    
    def _generate_audience_signals(self, theme: Dict) -> List[str]:
        """Generate audience signals for Performance Max campaigns"""
        
        theme_type = theme['theme_type']
        
        if theme_type == 'Product Category':
            return [
                'Users who searched for similar products',
                'Previous website visitors',
                'Similar to your converters'
            ]
        elif theme_type == 'Use-case Based':
            return [
                'In-market for related products',
                'Content engagement audiences',
                'Custom intent audiences'
            ]
        elif theme_type == 'Geographic':
            return [
                'Local area targeting',
                'Users near business locations',
                'Local service searchers'
            ]
        else:
            return [
                'Website visitors',
                'Similar audiences',
                'Demographic targeting'
            ]
    
    def _get_optimization_focus(self, theme_type: str) -> str:
        """Get optimization focus based on theme type"""
        
        focus_map = {
            'Product Category': 'Conversion value optimization',
            'Use-case Based': 'Conversion volume optimization', 
            'Geographic': 'Local action optimization',
            'Brand': 'Brand awareness and conversions'
        }
        
        return focus_map.get(theme_type, 'Conversion optimization')
    
    def export_campaign_structure(self, search_structure: Dict, 
                                shopping_structure: Dict, 
                                pmax_structure: Dict,
                                export_format: str = 'excel') -> str:
        """Export complete campaign structure to specified format"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if export_format.lower() == 'excel':
            filename = f"exports/SEM_Campaign_Plan_{timestamp}.xlsx"
            
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Search Campaign Export
                if search_structure:
                    search_summary = pd.DataFrame([{
                        'Campaign Type': 'Search',
                        'Total Budget': search_structure['total_budget'],
                        'Daily Budget': search_structure['daily_budget'],
                        'Ad Groups': len(search_structure['ad_groups']),
                        'Estimated Monthly Clicks': search_structure['performance_projections']['estimated_monthly_clicks'],
                        'Estimated Monthly Conversions': search_structure['performance_projections']['estimated_monthly_conversions'],
                        'Estimated CPA': search_structure['performance_projections']['estimated_overall_cpa']
                    }])
                    search_summary.to_excel(writer, sheet_name='Search_Summary', index=False)
                    
                    # Detailed ad groups
                    search_details = []
                    for ag in search_structure['ad_groups']:
                        for kw in ag['keywords']:
                            search_details.append({
                                'Ad Group': ag['ad_group_name'],
                                'Intent': ag['intent_category'],
                                'Keyword': kw['keyword'],
                                'Match Type': kw['match_type'],
                                'Monthly Searches': kw['avg_monthly_searches'],
                                'Suggested CPC': kw['suggested_cpc'],
                                'Performance Score': kw['performance_score']
                            })
                    
                    pd.DataFrame(search_details).to_excel(writer, sheet_name='Search_Keywords', index=False)
                
                # Shopping Campaign Export
                if shopping_structure:
                    shopping_summary = pd.DataFrame([{
                        'Campaign Type': 'Shopping',
                        'Total Budget': shopping_structure['total_budget'],
                        'Target CPC': shopping_structure['bid_recommendations']['target_cpc'],
                        'Max CPC': shopping_structure['bid_recommendations']['max_cpc'],
                        'Estimated Monthly Clicks': shopping_structure['performance_projections']['estimated_monthly_clicks'],
                        'Estimated Monthly Conversions': shopping_structure['performance_projections']['estimated_monthly_conversions'],
                        'Estimated CPA': shopping_structure['performance_projections']['estimated_cpa']
                    }])
                    shopping_summary.to_excel(writer, sheet_name='Shopping_Summary', index=False)
                
                # Performance Max Export
                if pmax_structure:
                    pmax_summary = []
                    for ag in pmax_structure['asset_groups']:
                        pmax_summary.append({
                            'Asset Group': ag['asset_group_name'],
                            'Theme Type': ag['theme_type'],
                            'Allocated Budget': ag['allocated_budget'],
                            'Target Audience': ag['target_audience'],
                            'Asset Focus': ag['asset_focus'],
                            'Keywords Count': len(ag['keywords'])
                        })
                    
                    pd.DataFrame(pmax_summary).to_excel(writer, sheet_name='PMax_Asset_Groups', index=False)
            
            logger.info(f"Campaign structure exported to {filename}")
            return filename
        
        elif export_format.lower() == 'json':
            filename = f"exports/SEM_Campaign_Plan_{timestamp}.json"
            
            export_data = {
                'export_timestamp': timestamp,
                'search_campaign': search_structure,
                'shopping_campaign': shopping_structure,
                'performance_max_campaign': pmax_structure
            }
            
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"Campaign structure exported to {filename}")
            return filename
        
        else:
            raise ValueError("Unsupported export format. Use 'excel' or 'json'.")
