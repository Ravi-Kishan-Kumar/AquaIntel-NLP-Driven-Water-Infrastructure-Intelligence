import pandas as pd
from recurring_detector import detect_recurring_issues, get_recurring_details

def run_tests():
    # Create mock data
    data = [
        # 5 complaints in Whitefield, Leakage category, within 30 days
        {"complaint_text": "leak 1", "category": "Leakage", "priority": "High", "location": "Whitefield", "date": "2026-03-01"},
        {"complaint_text": "leak 2", "category": "Leakage", "priority": "High", "location": "Whitefield", "date": "2026-03-05"},
        {"complaint_text": "leak 3", "category": "Leakage", "priority": "Medium", "location": "Whitefield", "date": "2026-03-10"},
        {"complaint_text": "leak 4", "category": "Leakage", "priority": "Low", "location": "Whitefield", "date": "2026-03-15"},
        {"complaint_text": "leak 5", "category": "Leakage", "priority": "High", "location": "Whitefield", "date": "2026-03-20"},
        
        # 4 complaints in Jayanagar, Supply category, within 30 days (should NOT be flagged since threshold is 5)
        {"complaint_text": "supply 1", "category": "Supply", "priority": "High", "location": "Jayanagar", "date": "2026-03-01"},
        {"complaint_text": "supply 2", "category": "Supply", "priority": "Medium", "location": "Jayanagar", "date": "2026-03-05"},
        {"complaint_text": "supply 3", "category": "Supply", "priority": "Low", "location": "Jayanagar", "date": "2026-03-10"},
        {"complaint_text": "supply 4", "category": "Supply", "priority": "High", "location": "Jayanagar", "date": "2026-03-15"},
        
        # 1 complaint in Whitefield, Leakage but outside 30 days window (latest date is 2026-03-20, so 30 days window starts 2026-02-18)
        {"complaint_text": "leak 0", "category": "Leakage", "priority": "High", "location": "Whitefield", "date": "2026-01-01"},
    ]

    df = pd.DataFrame(data)
    print("Mock DataFrame:")
    print(df)

    print("\nDetecting recurring issues (window=30, threshold=5):")
    recurring = detect_recurring_issues(df, time_window_days=30, threshold=5)
    print(recurring)

    assert len(recurring) == 1
    assert recurring.iloc[0]['location'] == "Whitefield"
    assert recurring.iloc[0]['category'] == "Leakage"
    assert recurring.iloc[0]['complaint_count'] == 5
    assert recurring.iloc[0]['status'] == "Recurring Issue Detected"

    print("\nGetting details for Whitefield - Leakage:")
    details = get_recurring_details(df, "Whitefield", "Leakage", time_window_days=30)
    print(details)
    assert len(details) == 5

    print("\nAll tests passed successfully!")

if __name__ == "__main__":
    run_tests()
