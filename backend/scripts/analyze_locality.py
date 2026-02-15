"""
Simple Locality Analyzer
Just edit the locality name and run!
"""

from data_collection_guide import collect_all_data, load_config
from locality_rating_system import rate_locality
import json
import os

# ============================================================================
# ✏️  EDIT THESE TWO LINES TO ANALYZE ANY LOCALITY
# ============================================================================

LOCALITY = "Connaught Place"
CITY = "DELHI"

# ============================================================================
# Don't edit anything below this line (unless you know what you're doing!)
# ============================================================================

def main():
    print("\n" + "="*70)
    print("🏘️  LOCALITY RATING SYSTEM")
    print("="*70)
    
    # Check if config file exists
    if not os.path.exists('config.json'):
        print("\n❌ ERROR: config.json not found!")
        print("\n📝 What to do:")
        print("   1. Copy 'config_template.json' to 'config.json'")
        print("   2. Edit config.json and add your API keys")
        print("   3. Run this script again")
        print("\n💡 TIP: You can run the example without API keys:")
        print("   python locality_rating_system.py")
        print("\n" + "="*70)
        return
    
    try:
        print("\n📍 Analyzing: {}, {}".format(LOCALITY, CITY))
        print("⏳ Loading API keys...")
        config = load_config()
        
        print("\n🔍 Collecting data...")
        print("   This will take 2-5 minutes. Please wait...")
        print("   (You'll see progress messages below)")
        print("")
        
        # Collect all data
        data = collect_all_data(LOCALITY, CITY, config)
        
        print("\n📊 Calculating rating...")
        report = rate_locality(f"{LOCALITY}, {CITY}", data)
        
        # Display results
        print("\n" + "="*70)
        print("📋 LOCALITY RATING REPORT: {}".format(report['locality']))
        print("="*70)
        
        print(f"\n🎯 Final Score: {report['final_score']}/100")
        print(f"💪 Confidence: {report['confidence']}% ({report['confidence_level']})")
        
        # Color-coded recommendation
        rec = report['recommendation']
        if rec == "BUY":
            emoji = "✅"
        elif rec == "HOLD":
            emoji = "⏸️"
        else:
            emoji = "❌"
        
        print(f"\n{emoji} RECOMMENDATION: {rec}")
        print(f"💡 Reasoning: {report['reasoning']}")
        
        print(f"\n📊 Component Scores:")
        print("-" * 50)
        for component, score in report['component_scores'].items():
            # Visual bar
            bars = int(score / 5)  # 20 bars max
            bar_visual = "█" * bars + "░" * (20 - bars)
            print(f"{component.title():<20} {bar_visual} {score:>5.1f}/100")
        
        print(f"\n✨ Key Insights:")
        print("-" * 50)
        for i, insight in enumerate(report['key_insights'], 1):
            print(f"  {i}. {insight}")
        
        if report.get('risks'):
            print(f"\n⚠️  Risks/Concerns:")
            print("-" * 50)
            for i, risk in enumerate(report['risks'], 1):
                print(f"  {i}. {risk}")
        
        # Save to file
        filename = f"{LOCALITY}_{CITY}_report.json".replace(" ", "_")
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print("\n" + "="*70)
        print(f"💾 Full report saved to: {filename}")
        print("="*70)
        print("\n🎉 Analysis complete!")
        
        # Tips
        print("\n💡 What to do next:")
        print("   • Open the JSON file to see all details")
        print("   • Compare with other localities")
        print("   • Add manual real estate data for better accuracy")
        print("   • Share results with friends/family")
        print("")
        
    except FileNotFoundError as e:
        print(f"\n❌ ERROR: {e}")
        print("\n💡 Make sure config.json exists and has your API keys!")
    except KeyError as e:
        print(f"\n❌ ERROR: Missing API key: {e}")
        print("\n💡 Check your config.json file has all required keys")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\n💡 Check your internet connection and API keys")
        print("💡 See BEGINNER_GUIDE.md for troubleshooting")

if __name__ == "__main__":
    main()
