# Locality Rating System 🏘️

A Python-based data-driven system to evaluate localities for real estate investment decisions using multiple data sources, sentiment analysis, and a weighted scoring algorithm.

## 🎯 What It Does

The system collects data from multiple sources and provides:
- **Rating Score** (0-100): Comprehensive evaluation of the locality
- **Confidence Level** (High/Medium/Low): How reliable the rating is
- **Recommendation** (BUY/HOLD/AVOID): Investment decision guidance
- **Detailed Insights**: What makes the locality good or risky

## 📊 Evaluation Criteria

| Component | Weight | Data Sources |
|-----------|--------|--------------|
| **User Sentiment** | 20% | Reddit, Twitter, Google Reviews |
| **Infrastructure** | 25% | Google Maps (metro, hospitals, schools) |
| **Real Estate Trends** | 20% | Price appreciation, rental yield |
| **Developer Presence** | 15% | RERA data, reputed builders |
| **Major Projects** | 10% | News articles, govt announcements |
| **Amenities** | 8% | Restaurants, gyms, parks, entertainment |
| **Crime Stats** | 2% | Police data, news reports |

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.9+
pip install pandas numpy requests beautifulsoup4 selenium
pip install praw tweepy googlemaps vaderSentiment textblob
pip install plotly matplotlib seaborn newsapi-python
```

### Setup

1. **Get API Keys**
   - [Google Maps API](https://console.cloud.google.com/) - For places, distances
   - [Reddit API](https://www.reddit.com/prefs/apps) - For sentiment analysis
   - [NewsAPI](https://newsapi.org/) - For project news
   - [Twitter API](https://developer.twitter.com/) - Optional

2. **Configure**
   ```bash
   cp config_template.json config.json
   # Edit config.json with your API keys
   ```

3. **Run Example**
   ```bash
   python locality_rating_system.py
   ```

## 📁 Project Structure

```
locality-rating-system/
├── locality_rating_system.py      # Main scoring engine
├── data_collection_guide.py       # Data collection functions
├── locality_rating_design.md      # Detailed design document
├── config_template.json           # API key template
├── manual_data_template.json      # Manual data entry template
└── README.md                      # This file
```

## 💻 Usage

### Basic Usage

```python
from locality_rating_system import rate_locality

# Your collected data
data = {
    'sentiment': {
        'avg_sentiment': 0.35,
        'mention_count': 245,
        'recent_sentiment': 0.45
    },
    'infrastructure': {
        'metro_distance_km': 2.5,
        'hospitals_5km': 4,
        'schools_3km': 8,
        'connectivity': 'good',
        'shopping_density': 'high'
    },
    # ... more data
}

# Get rating
report = rate_locality("Whitefield, Bangalore", data)

print(f"Score: {report['final_score']}/100")
print(f"Recommendation: {report['recommendation']}")
```

### Data Collection

```python
from data_collection_guide import collect_all_data, load_config

# Load API keys
config = load_config()

# Collect data for a locality
data = collect_all_data("Koramangala", "Bangalore", config)

# Rate it
report = rate_locality("Koramangala, Bangalore", data)
```

## 📈 Example Output

```
======================================================================
LOCALITY RATING REPORT: Whitefield, Bangalore
======================================================================

Final Score: 70.16/100
Confidence: 93.5% (High)

RECOMMENDATION: HOLD
Reasoning: Decent potential but monitor trends

Component Scores:             
--------------------------------------------------
Sentiment                   70.8/100  (weight: 20%)
Infrastructure              80.0/100  (weight: 25%)
Real_Estate                 65.0/100  (weight: 20%)
Developers                  80.0/100  (weight: 15%)
Projects                    78.0/100  (weight: 10%)
Amenities                   21.2/100  (weight: 8%)
Crime                       75.0/100  (weight: 2%)

Key Insights:                 
--------------------------------------------------
1. Good user engagement (245 mentions)
2. Improving sentiment trend
3. Good metro connectivity (2.5km)
4. Multiple hospitals nearby (4)
5. Good educational infrastructure (8 schools)
6. Good price appreciation (12.5% YoY)
7. Strong developer presence (4 reputed brands)
8. Metro planned (construction)

Risks/Concerns:               
--------------------------------------------------
1. Above city average pricing
```

## 🎨 Scoring Algorithm

### Formula
```
Final Score = Σ(Component Score × Weight)
```

### Component Calculations

**Infrastructure Score** (0-100)
- Metro proximity: <1km (25pts), 1-3km (15pts), 3-5km (5pts)
- Hospitals (5km): 3+ (15pts), 2 (10pts), 1 (5pts)
- Schools (3km): 5+ (15pts), 3-4 (10pts), 1-2 (5pts)
- Connectivity: Excellent (25pts), Good (15pts), Average (10pts)
- Shopping: High (20pts), Medium (10pts), Low (5pts)

**Real Estate Score** (0-100)
- Price appreciation: >15% (30pts), 10-15% (25pts), 5-10% (20pts)
- Rental yield: >4% (25pts), 3-4% (20pts), 2-3% (15pts)
- Inventory turnover: <90 days (20pts), <180 (15pts), <365 (10pts)
- Price competitiveness: Below avg (25pts), At avg (15pts), Above (5pts)

### Recommendation Logic

```python
if score >= 75 and confidence >= 70:
    → BUY (Strong fundamentals)
    
elif score >= 60 and confidence >= 60:
    → HOLD (Monitor trends)
    
else:
    → AVOID (Weak fundamentals or insufficient data)
```

**Safety Rules:**
- Crime score < 30 → Downgrade to HOLD
- Real estate trend < 20 → Downgrade to HOLD

## 📊 Data Sources

### Automated Collection
- **Google Maps API**: Infrastructure, amenities, distances
- **Reddit API**: User sentiment, community feedback
- **NewsAPI**: Major projects, development news
- **OpenStreetMap**: Additional infrastructure data

### Manual Entry Required
- **Real Estate Trends**: 99acres, MagicBricks, Housing.com
- **Developer Data**: RERA website, project track records
- **Crime Statistics**: NCRB, local police data

## 🔧 Customization

### Adjust Weights

```python
# In locality_rating_system.py
WEIGHTS = {
    'sentiment': 0.15,        # Reduce sentiment weight
    'infrastructure': 0.30,   # Increase infrastructure
    'real_estate': 0.25,      # Increase real estate
    'developers': 0.15,
    'projects': 0.10,
    'amenities': 0.05,
    'crime': 0.00            # Disable if no data
}
```

### Change Thresholds

```python
RECOMMENDATION_THRESHOLDS = {
    'buy': {'score': 80, 'confidence': 75},   # More conservative
    'hold': {'score': 60, 'confidence': 60},
    'avoid': {'score': 0, 'confidence': 0}
}
```

## 📝 Implementation Phases

### Phase 1: MVP ✅
- [x] Basic scoring algorithm
- [x] Manual data entry support
- [x] Example implementation
- [x] Console output

### Phase 2: Automation (Next)
- [ ] Automated API data collection
- [ ] Sentiment analysis pipeline
- [ ] CSV/JSON export
- [ ] Batch processing

### Phase 3: Enhancement
- [ ] Historical tracking
- [ ] Comparative analysis
- [ ] Visualization dashboard
- [ ] Predictive trends

### Phase 4: Production
- [ ] Web interface
- [ ] Database storage
- [ ] Scheduled updates
- [ ] User authentication

## 🎯 Use Cases

1. **Real Estate Investment**: Identify promising localities for property purchase
2. **Rental Analysis**: Find areas with good rental yield potential
3. **Comparative Study**: Compare multiple localities side-by-side
4. **Trend Monitoring**: Track locality development over time
5. **Due Diligence**: Validate broker recommendations with data

## ⚠️ Limitations & Disclaimers

- **Not Financial Advice**: This tool provides data-driven insights, not investment advice
- **Data Quality**: Output quality depends on input data accuracy
- **API Limits**: Free tier APIs have rate limits
- **Manual Data**: Some components require manual research
- **Local Expertise**: Should be combined with local market knowledge

## 🤝 Contributing

Ways to improve this project:
- Add more data sources (Zomato, Swiggy, local govt APIs)
- Improve sentiment analysis with ML models
- Build web scraping for real estate portals
- Create visualization dashboard
- Add historical data tracking
- Implement machine learning for predictions

## 📚 Resources

- [Google Maps API Documentation](https://developers.google.com/maps/documentation)
- [Reddit API (PRAW) Guide](https://praw.readthedocs.io/)
- [VADER Sentiment Analysis](https://github.com/cjhutto/vaderSentiment)
- [99acres](https://www.99acres.com/) - Real estate data
- [RERA State Websites](https://rera.karnataka.gov.in/) - Developer info

## 📄 License

This project is for educational and research purposes. Please ensure compliance with API terms of service and respect website scraping policies.

---

**Built with ❤️ for data-driven real estate decisions**

For questions or suggestions, feel free to open an issue or contribute!
