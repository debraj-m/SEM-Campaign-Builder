#!/usr/bin/env python3
"""
SEM Campaign Builder - Configuration-driven application
Run this script after setting up config.yaml with your inputs
"""

import yaml
import sys
import os
import logging
import random
from datetime import datetime
from typing import Dict, List

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.enhanced_keyword_research import EnhancedKeywordResearch
from src.web_scraper import WebScraper
from src.keyword_analyzer import KeywordAnalyzer
from src.campaign_builder import CampaignBuilder
from src.bid_optimizer import BidOptimizer

class ConfigDrivenSEMBuilder:
    """Configuration-driven SEM Campaign Builder"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config = self.load_config()
        self.setup_logging()
        
        # Initialize components
        self.enhanced_research = EnhancedKeywordResearch()
        self.web_scraper = WebScraper()
        self.keyword_analyzer = KeywordAnalyzer()
        self.campaign_builder = CampaignBuilder(
            conversion_rate=self.config['business']['conversion_rate']
        )
        self.bid_optimizer = BidOptimizer(
            conversion_rate=self.config['business']['conversion_rate'],
            target_roas=self.config['business']['target_roas']
        )
        
        self.results = {}
    
    def load_config(self) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as file:
                config = yaml.safe_load(file)
            print(f"✓ Configuration loaded from {self.config_path}")
            return config
        except FileNotFoundError:
            print(f"❌ Configuration file {self.config_path} not found!")
            print("Please copy config.yaml.example to config.yaml and configure it.")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"❌ Error parsing YAML configuration: {e}")
            sys.exit(1)
    
    def setup_logging(self):
        """Setup logging based on configuration"""
        if self.config['advanced']['enable_logging']:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(f'sem_builder_{datetime.now().strftime("%Y%m%d")}.log'),
                    logging.StreamHandler()
                ]
            )
        else:
            logging.basicConfig(level=logging.WARNING)
    
    def run_complete_analysis(self) -> Dict:
        """Run complete SEM analysis based on configuration"""
        
        print("🚀 SEM Campaign Builder - Configuration-driven Analysis")
        print("=" * 70)
        
        # Display configuration summary
        self.display_config_summary()
        
        # Step 1: Keyword Research
        print("\n🔍 Step 1: Comprehensive Keyword Research")
        print("-" * 50)
        keywords = self.perform_keyword_research()
        
        if not keywords:
            print("❌ No keywords found. Please check your configuration.")
            return {}
        
        print(f"✓ Total keywords discovered: {len(keywords)}")
        
        # Step 2: Keyword Analysis and Filtering
        print("\n🧹 Step 2: Keyword Analysis and Filtering")
        print("-" * 50)
        filtered_keywords = self.analyze_and_filter_keywords(keywords)
        
        if not filtered_keywords:
            print("❌ No keywords passed filtering. Try lowering min_search_volume.")
            return {}
        
        print(f"✓ High-quality keywords: {len(filtered_keywords)}")
        
        # Step 3: Campaign Structure Creation
        print("\n🏗️ Step 3: Campaign Structure Creation")
        print("-" * 50)
        campaigns = self.create_campaign_structure(filtered_keywords)
        
        # Step 4: Bid Optimization
        print("\n⚡ Step 4: Bid Optimization")
        print("-" * 50)
        bid_optimization = self.optimize_bids(filtered_keywords)
        
        # Step 5: Export Results
        print("\n📊 Step 5: Export Results")
        print("-" * 50)
        export_file = self.export_results(campaigns, bid_optimization)
        
        # Step 6: Generate Summary
        print("\n📋 Step 6: Analysis Summary")
        print("-" * 50)
        self.display_results_summary(campaigns, filtered_keywords, bid_optimization)
        
        # Store results
        self.results = {
            'keywords': keywords,
            'filtered_keywords': filtered_keywords,
            'campaigns': campaigns,
            'bid_optimization': bid_optimization,
            'export_file': export_file
        }
        
        return self.results
    
    def display_config_summary(self):
        """Display configuration summary"""
        config = self.config
        
        print(f"\n📋 CONFIGURATION SUMMARY:")
        print(f"  Brand: {config['brand']['company_name']}")
        print(f"  Website: {config['brand']['website_url']}")
        print(f"  Industry: {config['brand']['industry']}")
        print(f"  Total Budget: ${config['budget']['total']:,}")
        print(f"  Target Locations: {', '.join(config['locations'])}")
        print(f"  Competitors: {len(config['competitors'])} configured")
        print(f"  Seed Keywords: {len(config['seed_keywords'])} provided")
    
    def perform_keyword_research(self) -> List[Dict]:
        """Perform comprehensive keyword research"""
        all_keywords = []
        
        # Method 1: Enhanced research (WordStream + others)
        if self.config['keyword_research']['use_wordstream']:
            print("Extracting keywords using WordStream and enhanced methods...")
            enhanced_keywords = self.enhanced_research.comprehensive_keyword_research(
                self.config['brand']['website_url'],
                self.config['seed_keywords']
            )
            all_keywords.extend(enhanced_keywords)
            print(f"✓ Enhanced research: {len(enhanced_keywords)} keywords")
        
        # Method 2: Competitor analysis
        if self.config['keyword_research']['use_competitor_analysis']:
            for competitor in self.config['competitors']:
                print(f"Analyzing competitor: {competitor['name']}")
                try:
                    comp_keywords = self.enhanced_research._analyze_website_content(competitor['url'])
                    # Add competitor variations
                    for kw in comp_keywords[:20]:  # Limit per competitor
                        # Create variations targeting the competitor
                        competitor_variations = [
                            f"{kw['keyword']} alternative",
                            f"better than {competitor['name'].lower()}",
                            f"{kw['keyword']} vs {competitor['name'].lower()}"
                        ]
                        
                        for var in competitor_variations:
                            all_keywords.append({
                                'keyword': var,
                                'avg_monthly_searches': kw['avg_monthly_searches'] // 2,
                                'competition': 'MEDIUM',
                                'competition_index': 50,
                                'low_top_page_bid': kw['low_top_page_bid'],
                                'high_top_page_bid': kw['high_top_page_bid'],
                                'data_source': f'competitor_{competitor["name"]}'
                            })
                    
                    print(f"✓ {competitor['name']}: {len(comp_keywords)} base keywords")
                except Exception as e:
                    print(f"⚠️ Failed to analyze {competitor['name']}: {e}")
        
        # Method 3: Industry-specific keyword generation
        industry_keywords = self.generate_industry_keywords()
        all_keywords.extend(industry_keywords)
        print(f"✓ Industry-specific: {len(industry_keywords)} keywords")
        
        # Remove duplicates
        seen = set()
        unique_keywords = []
        for kw in all_keywords:
            if kw['keyword'] not in seen:
                seen.add(kw['keyword'])
                unique_keywords.append(kw)
        
        return unique_keywords
    
    def generate_industry_keywords(self) -> List[Dict]:
        """Generate industry-specific keywords based on configuration"""
        industry = self.config['brand']['industry'].lower()
        company_name = self.config['brand']['company_name'].lower()
        
        # Industry-specific patterns
        industry_patterns = {
            'saas': [
                'software as a service', 'cloud software', 'saas platform', 'subscription software',
                'cloud-based', 'web application', 'online software', 'saas solution'
            ],
            'analytics': [
                'data analytics', 'business intelligence', 'data visualization', 'reporting tool',
                'dashboard', 'metrics', 'kpi tracking', 'data insights', 'analytics platform'
            ],
            'marketing': [
                'marketing automation', 'digital marketing', 'marketing platform', 'crm',
                'lead generation', 'email marketing', 'marketing software'
            ]
        }
        
        keywords = []
        
        # Generate based on industry
        for key, patterns in industry_patterns.items():
            if key in industry:
                for pattern in patterns:
                    # Create variations
                    variations = [
                        pattern,
                        f"best {pattern}",
                        f"{pattern} software",
                        f"{pattern} tool",
                        f"{pattern} platform",
                        f"enterprise {pattern}",
                        f"{pattern} solution",
                        f"affordable {pattern}",
                        f"{pattern} pricing",
                        f"{pattern} comparison"
                    ]
                    
                    for var in variations:
                        keywords.append({
                            'keyword': var,
                            'avg_monthly_searches': self.estimate_industry_volume(var),
                            'competition': self.estimate_industry_competition(var),
                            'competition_index': self.estimate_competition_index(var),
                            'low_top_page_bid': round(self.estimate_industry_cpc(var) * 0.7, 2),
                            'high_top_page_bid': round(self.estimate_industry_cpc(var) * 1.4, 2),
                            'data_source': 'industry_specific'
                        })
        
        return keywords[:50]  # Limit industry keywords
    
    def estimate_industry_volume(self, keyword: str) -> int:
        """Estimate search volume based on keyword characteristics"""
        import random
        
        # Base volume
        base = 1000
        
        # Adjust based on keyword type
        if any(word in keyword for word in ['best', 'top', 'comparison']):
            base *= 2
        if any(word in keyword for word in ['enterprise', 'business']):
            base *= 1.5
        if any(word in keyword for word in ['free', 'cheap', 'affordable']):
            base *= 3
        if 'pricing' in keyword:
            base *= 1.8
        
        # Add randomness
        return random.randint(int(base * 0.5), int(base * 2))
    
    def estimate_industry_competition(self, keyword: str) -> str:
        """Estimate competition level"""
        if any(word in keyword for word in ['enterprise', 'business', 'software']):
            return 'HIGH'
        elif any(word in keyword for word in ['best', 'comparison', 'pricing']):
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def estimate_competition_index(self, keyword: str) -> int:
        """Convert competition to index"""
        competition = self.estimate_industry_competition(keyword)
        if competition == 'HIGH':
            return random.randint(70, 95)
        elif competition == 'MEDIUM':
            return random.randint(40, 70)
        else:
            return random.randint(10, 40)
    
    def estimate_industry_cpc(self, keyword: str) -> float:
        """Estimate CPC based on industry and keyword type"""
        import random
        
        # Base CPC for different industries
        industry_base_cpc = {
            'saas': 4.0,
            'analytics': 3.5,
            'marketing': 5.0,
            'finance': 8.0,
            'legal': 12.0
        }
        
        industry = self.config['brand']['industry'].lower()
        base_cpc = 3.0  # Default
        
        for key, cpc in industry_base_cpc.items():
            if key in industry:
                base_cpc = cpc
                break
        
        # Adjust based on keyword intent
        if any(word in keyword for word in ['buy', 'purchase', 'pricing', 'cost']):
            base_cpc *= 1.5
        if any(word in keyword for word in ['free', 'how to', 'what is']):
            base_cpc *= 0.4
        if 'enterprise' in keyword:
            base_cpc *= 2.0
        
        return round(random.uniform(base_cpc * 0.6, base_cpc * 1.8), 2)
    
    def analyze_and_filter_keywords(self, keywords: List[Dict]) -> List[Dict]:
        """Filter and analyze keywords based on configuration"""
        
        # Apply filtering
        filtered = self.keyword_analyzer.filter_keywords(
            keywords,
            min_search_volume=self.config['keyword_research']['min_search_volume']
        )
        
        # Display top keywords
        if filtered:
            print("\n🏆 Top 15 Keywords by Performance Score:")
            top_keywords = sorted(filtered, key=lambda x: x['performance_score'], reverse=True)[:15]
            
            for i, kw in enumerate(top_keywords, 1):
                print(f"  {i:2d}. {kw['keyword']:<40} "
                      f"Score: {kw['performance_score']:>5.1f} | "
                      f"Vol: {kw['avg_monthly_searches']:>6,} | "
                      f"CPC: ${kw.get('high_top_page_bid', 0):>5.2f}")
        
        return filtered
    
    def create_campaign_structure(self, keywords: List[Dict]) -> Dict:
        """Create campaign structure based on configuration"""
        
        # Create ad groups
        ad_groups = self.keyword_analyzer.create_ad_groups(keywords)
        print(f"✓ Created {len(ad_groups)} ad groups")
        
        # Build campaigns
        search_campaign = self.campaign_builder.build_search_campaign_structure(
            ad_groups, 
            self.config['budget']['search_ads']
        )
        
        shopping_campaign = self.campaign_builder.build_shopping_campaign_structure(
            keywords,
            self.config['budget']['shopping_ads']
        )
        
        pmax_themes = self.keyword_analyzer.generate_performance_max_themes(keywords)
        pmax_campaign = self.campaign_builder.build_performance_max_structure(
            pmax_themes,
            self.config['budget']['performance_max']
        )
        
        campaigns = {
            'search': search_campaign,
            'shopping': shopping_campaign,
            'performance_max': pmax_campaign
        }
        
        print(f"✓ Search Campaign: {len(search_campaign['ad_groups'])} ad groups")
        print(f"✓ Shopping Campaign: Target CPC ${shopping_campaign['bid_recommendations']['target_cpc']:.2f}")
        print(f"✓ Performance Max: {len(pmax_campaign['asset_groups'])} asset groups")
        
        return campaigns
    
    def optimize_bids(self, keywords: List[Dict]) -> Dict:
        """Optimize bids based on configuration"""
        
        optimized_keywords = self.bid_optimizer.optimize_keyword_bids(
            keywords,
            self.config['budget']['search_ads'],
            avg_order_value=self.config['business']['average_order_value'],
            profit_margin=self.config['business']['profit_margin']
        )
        
        bid_report = self.bid_optimizer.generate_bid_recommendations_report(optimized_keywords)
        
        print(f"✓ Optimized {bid_report['summary']['total_keywords']} keywords")
        print(f"✓ Avg CPC: ${bid_report['summary']['average_cpc']:.2f}")
        print(f"✓ Projected conversions: {bid_report['summary']['projected_monthly_conversions']}")
        
        return {
            'optimized_keywords': optimized_keywords,
            'bid_report': bid_report
        }
    
    def export_results(self, campaigns: Dict, bid_optimization: Dict) -> str:
        """Export results based on configuration"""
        
        try:
            filename = self.campaign_builder.export_campaign_structure(
                campaigns['search'],
                campaigns['shopping'], 
                campaigns['performance_max'],
                self.config['export']['format']
            )
            print(f"✓ Results exported to: {filename}")
            return filename
        except Exception as e:
            print(f"⚠️ Export failed: {e}")
            return None
    
    def display_results_summary(self, campaigns: Dict, keywords: List[Dict], bid_optimization: Dict):
        """Display comprehensive results summary"""
        
        print("\n" + "=" * 70)
        print("📊 SEM CAMPAIGN ANALYSIS RESULTS")
        print("=" * 70)
        
        # Configuration summary
        config = self.config
        print(f"\n🏢 BRAND: {config['brand']['company_name']}")
        print(f"   Industry: {config['brand']['industry']}")
        print(f"   Website: {config['brand']['website_url']}")
        
        # Budget breakdown
        total_budget = config['budget']['total']
        print(f"\n💰 BUDGET ALLOCATION (${total_budget:,}/month):")
        print(f"   Search Ads:      ${config['budget']['search_ads']:,} ({config['budget']['search_ads']/total_budget*100:.1f}%)")
        print(f"   Shopping Ads:    ${config['budget']['shopping_ads']:,} ({config['budget']['shopping_ads']/total_budget*100:.1f}%)")
        print(f"   Performance Max: ${config['budget']['performance_max']:,} ({config['budget']['performance_max']/total_budget*100:.1f}%)")
        
        # Keyword insights
        print(f"\n🔍 KEYWORD INSIGHTS:")
        print(f"   Total Keywords: {len(keywords)}")
        
        # Performance distribution
        high_perf = len([k for k in keywords if k.get('performance_score', 0) >= 80])
        med_perf = len([k for k in keywords if 50 <= k.get('performance_score', 0) < 80])
        low_perf = len([k for k in keywords if k.get('performance_score', 0) < 50])
        
        print(f"   High Performers (80+): {high_perf}")
        print(f"   Medium Performers (50-79): {med_perf}")
        print(f"   Low Performers (<50): {low_perf}")
        
        # Intent distribution
        intent_dist = {}
        for kw in keywords:
            intent = kw.get('intent', 'unknown')
            intent_dist[intent] = intent_dist.get(intent, 0) + 1
        
        print(f"   Intent Distribution:")
        for intent, count in intent_dist.items():
            print(f"     {intent.title()}: {count}")
        
        # Campaign projections
        search = campaigns['search']
        shopping = campaigns['shopping']
        
        print(f"\n📈 PERFORMANCE PROJECTIONS:")
        print(f"   Search Campaign:")
        print(f"     Est. Monthly Clicks: {search['performance_projections']['estimated_monthly_clicks']:,}")
        print(f"     Est. Monthly Conversions: {search['performance_projections']['estimated_monthly_conversions']}")
        print(f"     Est. CPA: ${search['performance_projections']['estimated_overall_cpa']:.2f}")
        
        print(f"   Shopping Campaign:")
        print(f"     Target CPC: ${shopping['bid_recommendations']['target_cpc']:.2f}")
        print(f"     Est. Monthly Clicks: {shopping['performance_projections']['estimated_monthly_clicks']:,}")
        print(f"     Est. Monthly Conversions: {shopping['performance_projections']['estimated_monthly_conversions']}")
        
        # Key recommendations
        print(f"\n💡 KEY RECOMMENDATIONS:")
        bid_report = bid_optimization['bid_report']
        for priority in bid_report.get('optimization_priorities', []):
            print(f"   • {priority}")
        
        print(f"\n🎯 SUCCESS METRICS TO TRACK:")
        print(f"   • Target ROAS: {config['business']['target_roas']}%")
        print(f"   • Target Conversion Rate: {config['business']['conversion_rate']*100:.1f}%")
        print(f"   • Average Order Value: ${config['business']['average_order_value']:,}")
        
        print("\n" + "=" * 70)
        print("🎉 Analysis Complete! Review the exported file for detailed campaign structure.")
        print("=" * 70)

def main():
    """Main function to run the configuration-driven SEM builder"""
    
    # Check if config file exists
    if not os.path.exists("config.yaml"):
        print("❌ config.yaml not found!")
        print("Please copy config.yaml and configure it with your inputs.")
        return
    
    try:
        # Initialize and run analysis
        builder = ConfigDrivenSEMBuilder()
        results = builder.run_complete_analysis()
        
        if results:
            print(f"\n✅ SEM Campaign Analysis completed successfully!")
            print(f"📁 Results exported to: {results.get('export_file', 'exports folder')}")
        else:
            print("❌ Analysis failed. Please check your configuration and try again.")
    
    except KeyboardInterrupt:
        print("\n⚠️ Analysis interrupted by user.")
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
