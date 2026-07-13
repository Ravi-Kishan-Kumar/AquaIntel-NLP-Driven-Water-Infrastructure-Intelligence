import pandas as pd

def detect_recurring_issues(df, time_window_days=30, threshold=5):
    """
    Detects recurring issues based on Location + Category within a time window
    relative to the latest date in the dataset.
    
    Parameters:
    -----------
    df : pd.DataFrame
        The water complaint dataset containing columns: location, category, date, priority, complaint_text
    time_window_days : int
        The size of the time window in days
    threshold : int
        The minimum number of complaints required to flag a recurring issue
        
    Returns:
    --------
    pd.DataFrame
        A DataFrame of detected recurring issues sorted by complaint count descending.
    """
    if df.empty:
        return pd.DataFrame(columns=['location', 'category', 'complaint_count', 'status', 'latest_date'])
        
    df_copy = df.copy()
    
    # Ensure date column is parsed as datetime
    df_copy['date'] = pd.to_datetime(df_copy['date'])
    
    # Identify the latest date in the dataset to define our window anchor
    latest_date = df_copy['date'].max()
    start_date = latest_date - pd.Timedelta(days=time_window_days)
    
    # Filter dataset for complaints within the time window
    df_window = df_copy[df_copy['date'] >= start_date]
    
    # Group by location and category, and compute metrics
    grouped = df_window.groupby(['location', 'category']).agg(
        complaint_count=('complaint_text', 'count'),
        latest_date=('date', 'max')
    ).reset_index()
    
    # Filter for recurring issues based on threshold
    recurring = grouped[grouped['complaint_count'] >= threshold].copy()
    
    # Assign status
    recurring['status'] = "Recurring Issue Detected"
    
    # Sort by count (highest first)
    recurring = recurring.sort_values(by='complaint_count', ascending=False).reset_index(drop=True)
    
    return recurring

def get_recurring_details(df, location, category, time_window_days=30):
    """
    Retrieves the raw complaints for a specific recurring issue group.
    
    Parameters:
    -----------
    df : pd.DataFrame
        The water complaint dataset
    location : str
        The location of the issue
    category : str
        The category of the issue
    time_window_days : int
        The size of the time window in days
        
    Returns:
    --------
    pd.DataFrame
        Filtered subset of complaints
    """
    if df.empty:
        return pd.DataFrame()
        
    df_copy = df.copy()
    df_copy['date'] = pd.to_datetime(df_copy['date'])
    
    latest_date = df_copy['date'].max()
    start_date = latest_date - pd.Timedelta(days=time_window_days)
    
    # Filter by location, category, and date range
    filtered = df_copy[
        (df_copy['location'] == location) &
        (df_copy['category'] == category) &
        (df_copy['date'] >= start_date)
    ].sort_values(by='date', ascending=False).reset_index(drop=True)
    
    return filtered
