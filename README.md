# SEM Campaign Builder

A comprehensive tool for building structured SEM (Search Engine Marketing) campaigns using Search, Shopping, and Performance Max campaigns. This tool works completely without requiring Google Ads API access by using alternative keyword research methods and web scraping techniques.

## Quick Start Guide

## Quick Start Guide

### Step 1: Install Dependencies
Open your terminal/command prompt and run:
```bash
pip install -r requirements.txt
```

### Step 2: Configure Your Campaign Settings
Edit the `config.yaml` file with your business information:
```yaml
brand:
  website_url: "https://your-website.com"
  company_name: "Your Company Name"
  industry: "Your Industry"

budget:
  total: 10000
  search_ads: 5000
  shopping_ads: 2000
  performance_max: 3000

seed_keywords:
  - "your main keyword"
  - "your product category"
  - "your service type"
```

### Step 3: Run the Analysis
Execute the main script:
```bash
python run_analysis.py
```

### Step 4: Get Your Results
Check the `exports/` folder for:
- Complete Excel campaign plan
- Keyword lists with search volumes
- Bid recommendations
- Campaign structure ready for Google Ads import

## Key Features

## Key Features

- **No API Required**: Works without Google Ads API access using alternative data sources
- **Complete Automation**: Configure once, run script, get complete campaign plan
- **AI-Powered Analysis**: Uses machine learning for keyword analysis and intent classification
- **Industry Intelligent**: Automatically adapts keyword strategies to your business type
- **Competitor Analysis**: Extracts insights from competitor websites automatically
- **Export Ready**: Generates Excel files ready for direct Google Ads import

## How It Works - Alternative Keyword Research Methods

Since this tool doesn't require Google Ads API access, it uses multiple alternative methods:

## How It Works - Alternative Keyword Research Methods

Since this tool doesn't require Google Ads API access, it uses multiple alternative methods:

### 1. Google Autocomplete Integration
- Extracts real keyword suggestions from Google's autocomplete API
- Captures search queries that people actually type
- Provides long-tail keyword variations automatically

### 2. Website Content Analysis
- Analyzes your website content to extract relevant keywords
- Identifies core business terms and industry language
- Generates keyword variations based on your actual offerings

### 3. Competitor Intelligence  
- Scrapes competitor websites for keyword insights
- Analyzes competitor content and terminology
- Generates "alternative to [competitor]" keyword variations

### 4. AI-Powered Keyword Enhancement
- Uses machine learning for intent classification (commercial, informational, local)
- Applies performance scoring algorithms
- Generates intelligent keyword variations and combinations

### 5. Industry-Specific Generation
- Applies tailored keyword patterns for different industries (SaaS, E-commerce, Services)
- Uses business model aware keyword generation
- Prioritizes conversion-focused keywords based on your industry

## Sample Output and Results

The tool generates comprehensive campaign plans with detailed analytics:

```
SEM CAMPAIGN ANALYSIS RESULTS
============================================

BRAND: Cube HQ
Industry: SaaS/Analytics
Website: https://www.cubehq.ai

BUDGET ALLOCATION ($10,000/month):
Search Ads:      $5,000 (50.0%)
Shopping Ads:    $2,000 (20.0%)
Performance Max: $3,000 (30.0%)

KEYWORD INSIGHTS:
Total Keywords: 238
High Performers (80+): 0
Medium Performers (50-79): 28
Low Performers (<50): 210

PERFORMANCE PROJECTIONS:
Search Campaign:
  Est. Monthly Clicks: 2,318
  Est. Monthly Conversions: 69.6
  Est. CPA: $71.84

KEY RECOMMENDATIONS:
• Optimize 192 high-volume, low-performing keywords
• Focus on conversion-oriented keywords
• Test different match types for top performers
```

## Project Structure and Files

```
SEM-Campaign-Builder/
├── config.yaml                    # Main configuration file - edit this first
├── run_analysis.py                # Main script to execute
├── requirements.txt               # Python dependencies
├── src/
│   ├── enhanced_keyword_research.py  # Keyword discovery engine
│   ├── keyword_analyzer.py           # AI-powered keyword analysis
│   ├── campaign_builder.py           # Campaign structure generator
│   └── bid_optimizer.py             # Bid optimization algorithms
├── exports/                       # Generated campaign plans appear here
└── data/                         # Temporary data storage
```

## Configuration Guide

### Basic Configuration (Required)
Edit `config.yaml` with your business details:

```yaml
# Brand Information
brand:
  website_url: "https://your-website.com"
  company_name: "Your Company Name"
  industry: "Your Industry Type"

# Budget Allocation (monthly amounts in USD)
budget:
  total: 10000
  search_ads: 5000
  shopping_ads: 2000
  performance_max: 3000
```

### Advanced Configuration (Optional)
```yaml
# Competitor Analysis
competitors:
  - url: "https://competitor1.com"
    name: "Competitor 1"
  - url: "https://competitor2.com"
    name: "Competitor 2"

# Seed Keywords (helps if your website has limited content)
seed_keywords:
  - "your main product"
  - "your main service"
  - "your industry term"

# Business Metrics
business:
  average_order_value: 2000
  profit_margin: 0.40
  conversion_rate: 0.03
  target_roas: 500
```

## Testing and Troubleshooting

### Test Your Installation
Run this command to verify everything is working:
```bash
python src/enhanced_keyword_research.py
```

This will test all keyword research methods and show you sample results.

### Common Issues and Solutions

**Issue: SSL Certificate Errors**
- Solution: The tool automatically handles SSL issues with fallback methods

**Issue: Website Access Blocked**
- Solution: Tool uses multiple data sources, so blocking of one source doesn't stop analysis

**Issue: Low Keyword Count**
- Solution: Add more seed keywords in config.yaml or check that your website has sufficient content

**Issue: Installation Problems**
- Solution: Make sure you have Python 3.7+ installed
- Try: `pip install --upgrade pip` then `pip install -r requirements.txt`

### Getting Better Results

1. **Add More Seed Keywords**: Include 8-12 relevant keywords in your config
2. **Add Competitors**: Include 2-4 main competitors for broader keyword discovery
3. **Detailed Website Content**: Ensure your website has clear product/service descriptions
4. **Industry Specification**: Set your industry type accurately in config.yaml

## Live Demo Example

The tool comes pre-configured with a working example:

**Current Demo Setup:**
- Website: `https://www.cubehq.ai` (Analytics/BI platform)
- Competitors: Looker, Tableau, Power BI, Sisense
- Budget: $10,000/month allocation
- Industry: SaaS/Analytics

**To test immediately:**
```bash
python run_analysis.py
```

**Expected Results:**
- 200+ targeted keywords for analytics/BI industry
- Organized ad groups by intent and keyword themes
- Bid recommendations based on industry benchmarks
- Complete Excel campaign plan in exports/ folder

## What You Get

### Keyword Research Output
- Comprehensive keyword list with search volumes
- Intent classification (commercial, informational, local)
- Competition analysis and difficulty scores
- Cost-per-click estimates
- Performance projections

### Campaign Structure
- **Search Campaigns**: Organized ad groups with targeted keywords
- **Shopping Campaigns**: Product group recommendations
- **Performance Max**: Asset group themes and audience targeting
- **Bid Strategy**: Automated bid recommendations for each keyword

### Export Files
- Excel spreadsheet with complete campaign structure
- Ready-to-import format for Google Ads
- Detailed keyword analysis and recommendations
- Budget allocation and performance projections

## System Requirements

- **Python**: Version 3.7 or higher
- **Operating System**: Windows, macOS, or Linux
- **Internet Connection**: Required for keyword research and website analysis
- **Browser**: Chrome browser (for Selenium web scraping)

## Who This Tool Is For

- **Digital Marketing Agencies**: Generate campaign plans for multiple clients
- **Small/Medium Businesses**: Create professional SEM campaigns without expensive tools
- **Marketing Professionals**: Save time on keyword research and campaign planning
- **Freelancers**: Offer comprehensive SEM planning services to clients
- **Anyone**: Who needs Google Ads campaigns but doesn't have API access

## Support and Documentation

This tool is designed to be self-sufficient and user-friendly. All configuration is done through the single `config.yaml` file, and the tool provides detailed logging and error messages to help troubleshoot any issues.

For best results, ensure your website has clear content about your products/services, and include relevant seed keywords in your configuration.

## License and Usage

This tool is designed for professional SEM campaign planning and can be used for commercial purposes. All generated campaign plans and keyword lists are yours to use in any Google Ads campaigns.
