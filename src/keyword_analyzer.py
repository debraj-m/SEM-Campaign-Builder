import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
import logging
import re
from collections import defaultdict
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KeywordAnalyzer:
    """AI-powered keyword analysis and filtering engine"""
    
    def __init__(self):
        self.min_search_volume = 500  # Default minimum search volume
        self.conversion_rate = 0.02   # Default 2% conversion rate
        
    def filter_keywords(self, keywords: List[Dict], 
                       min_search_volume: int = None,
                       max_competition_index: int = 80,
                       max_cpc: float = 10.0) -> List[Dict]:
        """Filter keywords based on performance criteria"""
        
        min_vol = min_search_volume or self.min_search_volume
        
        filtered_keywords = []
        for keyword in keywords:
            # Basic filtering criteria
            if (keyword.get('avg_monthly_searches', 0) >= min_vol and
                keyword.get('competition_index', 0) <= max_competition_index and
                keyword.get('high_top_page_bid', 0) <= max_cpc):
                
                # Calculate performance score
                keyword['performance_score'] = self._calculate_performance_score(keyword)
                filtered_keywords.append(keyword)
        
        # Sort by performance score
        filtered_keywords.sort(key=lambda x: x['performance_score'], reverse=True)
        
        logger.info(f"Filtered {len(keywords)} keywords down to {len(filtered_keywords)}")
        return filtered_keywords
    
    def _calculate_performance_score(self, keyword: Dict) -> float:
        """Calculate performance score for keyword prioritization"""
        try:
            search_volume = keyword.get('avg_monthly_searches', 0)
            competition_index = keyword.get('competition_index', 100)
            avg_cpc = (keyword.get('low_top_page_bid', 0) + keyword.get('high_top_page_bid', 0)) / 2
            
            # Normalize metrics (0-100 scale)
            volume_score = min(search_volume / 10000 * 100, 100)  # Cap at 10k searches
            competition_score = 100 - competition_index  # Lower competition = higher score
            
            # CPC efficiency score (lower CPC = higher score up to a point)
            if avg_cpc > 0:
                cpc_score = max(0, 100 - (avg_cpc * 20))  # Penalize high CPC
            else:
                cpc_score = 50  # Neutral score for unknown CPC
            
            # Weighted average
            performance_score = (
                volume_score * 0.4 +      # 40% weight on search volume
                competition_score * 0.35 + # 35% weight on competition
                cpc_score * 0.25          # 25% weight on CPC efficiency
            )
            
            return round(performance_score, 2)
            
        except Exception as e:
            logger.error(f"Error calculating performance score: {str(e)}")
            return 0.0
    
    def group_keywords_by_intent(self, keywords: List[Dict]) -> Dict[str, List[Dict]]:
        """Group keywords by search intent using AI analysis"""
        
        # Define intent patterns
        intent_patterns = {
            'brand': [r'\b(brand|company|official|website)\b'],
            'competitor': [r'\b(vs|versus|compare|alternative|competitor)\b'],
            'commercial': [r'\b(buy|purchase|price|cost|cheap|discount|deal|sale)\b'],
            'informational': [r'\b(what|how|why|guide|tips|tutorial|learn|information)\b'],
            'local': [r'\b(near me|local|in|location|city|area)\b'],
            'transactional': [r'\b(order|book|schedule|contact|call|hire)\b']
        }
        
        grouped_keywords = defaultdict(list)
        
        for keyword in keywords:
            keyword_text = keyword['keyword'].lower()
            intent_scores = {}
            
            # Calculate pattern-based scores
            for intent, patterns in intent_patterns.items():
                score = 0
                for pattern in patterns:
                    if re.search(pattern, keyword_text, re.IGNORECASE):
                        score += 1
                intent_scores[intent] = score
            
            # Determine primary intent
            if max(intent_scores.values()) > 0:
                primary_intent = max(intent_scores, key=intent_scores.get)
            else:
                primary_intent = self._classify_keyword_with_ai(keyword_text)
            
            grouped_keywords[primary_intent].append(keyword)
        
        return dict(grouped_keywords)
    
    def _classify_keyword_with_ai(self, keyword: str) -> str:
        """Use simple pattern matching for keyword intent classification"""
        
        # Simple rule-based classification since we removed OpenAI dependency
        keyword_lower = keyword.lower()
        
        # Brand patterns
        if any(brand in keyword_lower for brand in ['cube', 'cubehq', 'your-brand']):
            return 'brand'
        
        # Competitor patterns  
        if any(comp in keyword_lower for comp in ['vs', 'alternative', 'competitor', 'compare']):
            return 'competitor'
            
        # Commercial patterns
        if any(comm in keyword_lower for comm in ['buy', 'price', 'cost', 'pricing', 'purchase', 'software', 'tool', 'platform']):
            return 'commercial'
            
        # Informational patterns
        if any(info in keyword_lower for info in ['what', 'how', 'why', 'guide', 'tutorial', 'learn']):
            return 'informational'
            
        # Local patterns
        if any(local in keyword_lower for local in ['near me', 'local', 'location', 'address']):
            return 'local'
            
        return 'general'
    
    def create_ad_groups(self, keywords: List[Dict]) -> Dict[str, Dict]:
        """Create optimized ad groups from keywords"""
        
        # Group by intent first
        intent_groups = self.group_keywords_by_intent(keywords)
        
        ad_groups = {}
        
        for intent, intent_keywords in intent_groups.items():
            if not intent_keywords:
                continue
            
            # Further group by semantic similarity within intent
            semantic_groups = self._create_semantic_groups(intent_keywords)
            
            group_counter = 1
            for semantic_group in semantic_groups:
                if len(semantic_group) >= 3:  # Minimum keywords per ad group
                    
                    group_name = f"{intent.title()} Group {group_counter}"
                    
                    # Generate suggested match types
                    suggested_keywords = []
                    for kw in semantic_group:
                        match_types = self._suggest_match_types(kw['keyword'])
                        for match_type in match_types:
                            suggested_keywords.append({
                                'keyword': kw['keyword'],
                                'match_type': match_type,
                                'avg_monthly_searches': kw['avg_monthly_searches'],
                                'suggested_cpc': self._calculate_suggested_cpc(kw),
                                'performance_score': kw['performance_score']
                            })
                    
                    ad_groups[group_name] = {
                        'intent': intent,
                        'keywords': suggested_keywords,
                        'avg_search_volume': np.mean([kw['avg_monthly_searches'] for kw in semantic_group]),
                        'avg_competition': np.mean([kw.get('competition_index', 50) for kw in semantic_group]),
                        'suggested_budget_allocation': self._calculate_budget_allocation(semantic_group)
                    }
                    
                    group_counter += 1
        
        return ad_groups
    
    def _create_semantic_groups(self, keywords: List[Dict], max_group_size: int = 15) -> List[List[Dict]]:
        """Group keywords by semantic similarity"""
        
        # Simple keyword grouping based on common terms
        groups = []
        remaining_keywords = keywords.copy()
        
        while remaining_keywords:
            # Start new group with highest performing remaining keyword
            seed_keyword = max(remaining_keywords, key=lambda x: x['performance_score'])
            current_group = [seed_keyword]
            remaining_keywords.remove(seed_keyword)
            
            # Find similar keywords
            seed_words = set(seed_keyword['keyword'].lower().split())
            
            to_remove = []
            for keyword in remaining_keywords:
                if len(current_group) >= max_group_size:
                    break
                
                keyword_words = set(keyword['keyword'].lower().split())
                
                # Check for word overlap
                overlap = len(seed_words.intersection(keyword_words))
                if overlap >= 1:  # At least one word in common
                    current_group.append(keyword)
                    to_remove.append(keyword)
            
            # Remove grouped keywords from remaining
            for kw in to_remove:
                remaining_keywords.remove(kw)
            
            groups.append(current_group)
        
        return groups
    
    def _suggest_match_types(self, keyword: str) -> List[str]:
        """Suggest appropriate match types for a keyword"""
        
        word_count = len(keyword.split())
        
        if word_count == 1:
            return ['Phrase', 'Broad Match Modifier']
        elif word_count == 2:
            return ['Exact', 'Phrase', 'Broad Match Modifier']
        elif word_count >= 3:
            return ['Exact', 'Phrase']
        else:
            return ['Phrase']
    
    def _calculate_suggested_cpc(self, keyword: Dict) -> float:
        """Calculate suggested CPC bid"""
        
        low_bid = keyword.get('low_top_page_bid', 0)
        high_bid = keyword.get('high_top_page_bid', 0)
        
        if low_bid > 0 and high_bid > 0:
            # Start with average of low and high
            avg_bid = (low_bid + high_bid) / 2
            
            # Adjust based on performance score
            performance_score = keyword.get('performance_score', 50)
            
            if performance_score >= 80:
                multiplier = 1.1  # Bid slightly higher for high-performing keywords
            elif performance_score >= 60:
                multiplier = 1.0
            else:
                multiplier = 0.8  # Bid lower for lower-performing keywords
            
            suggested_cpc = round(avg_bid * multiplier, 2)
            
            # Apply reasonable bounds
            return max(0.25, min(suggested_cpc, 15.0))
        
        return 1.0  # Default bid
    
    def _calculate_budget_allocation(self, keyword_group: List[Dict]) -> float:
        """Calculate suggested budget allocation percentage for ad group"""
        
        total_volume = sum(kw['avg_monthly_searches'] for kw in keyword_group)
        avg_performance = np.mean([kw['performance_score'] for kw in keyword_group])
        
        # Base allocation on search volume and performance
        allocation_score = (total_volume * 0.7) + (avg_performance * 0.3)
        
        # Convert to percentage (this would be normalized across all groups)
        return round(allocation_score, 2)
    
    def generate_performance_max_themes(self, keywords: List[Dict]) -> List[Dict]:
        """Generate Performance Max campaign themes"""
        
        intent_groups = self.group_keywords_by_intent(keywords)
        
        themes = []
        
        # Product category themes
        commercial_keywords = intent_groups.get('commercial', [])
        if commercial_keywords:
            top_commercial = sorted(commercial_keywords, key=lambda x: x['performance_score'], reverse=True)[:10]
            themes.append({
                'theme_name': 'Product Category - Commercial Intent',
                'theme_type': 'Product Category',
                'keywords': [kw['keyword'] for kw in top_commercial],
                'target_audience': 'Ready to purchase',
                'asset_focus': 'Product images, pricing, offers'
            })
        
        # Informational themes
        info_keywords = intent_groups.get('informational', [])
        if info_keywords:
            top_info = sorted(info_keywords, key=lambda x: x['performance_score'], reverse=True)[:10]
            themes.append({
                'theme_name': 'Educational Content - Informational',
                'theme_type': 'Use-case Based',
                'keywords': [kw['keyword'] for kw in top_info],
                'target_audience': 'Research phase',
                'asset_focus': 'Educational content, guides, comparisons'
            })
        
        # Local themes
        local_keywords = intent_groups.get('local', [])
        if local_keywords:
            themes.append({
                'theme_name': 'Local Services',
                'theme_type': 'Geographic',
                'keywords': [kw['keyword'] for kw in local_keywords],
                'target_audience': 'Local customers',
                'asset_focus': 'Location info, local testimonials'
            })
        
        # Brand themes
        brand_keywords = intent_groups.get('brand', [])
        if brand_keywords:
            themes.append({
                'theme_name': 'Brand Protection',
                'theme_type': 'Brand',
                'keywords': [kw['keyword'] for kw in brand_keywords],
                'target_audience': 'Brand searchers',
                'asset_focus': 'Brand assets, official messaging'
            })
        
        return themes
