import pandas as pd
import random
import datetime

# Massive Complaint templates with diverse phrasing (English, Transliterated Kannada, Native Kannada)
templates = {
    'Leakage': [
        # English
        "Water is leaking from the main pipe near {location}.",
        "Huge water leak at {location}.",
        "Pipe burst in {location}, water is everywhere.",
        "Continuous water leakage in our area {location}.",
        "Taps are leaking continuously.",
        "There is a severe water leak at the intersection in {location}.",
        "Broken pipe causing flooding near {location}.",
        "Water wastage due to a leak at {location}, please fix immediately.",
        "Minor leak, only drops coming out from the pipe at {location}.",
        "No leakage, just a few drops coming out in {location}.",
        "Water dripping from the street valve near {location}.",
        "Pipe is cracked and leaking water at {location}.",
        
        # Transliterated Kannada (Kanglish)
        "neeru leak agthide {location} hatra.",
        "water pipe odedide {location} nalli.",
        "watr lekng frm pip {location}.",
        "pype brst at {location}.",
        "leakage problem since 2 days in {location}.",
        "tumba neeru waste agthide {location} nalli due to leak.",
        "main pipe break agide, neeru raste mele bartide {location}.",
        "swalpa leak agtide, just drops {location} hatra.",
        
        # Native Kannada
        "{location} ಹತ್ತಿರ ಮುಖ್ಯ ಪೈಪ್‌ನಿಂದ ನೀರು ಸೋರುತ್ತಿದೆ.",
        "{location} ನಲ್ಲಿ ಪೈಪ್ ಒಡೆದಿದೆ, ನೀರು ಪೋಲಾಗುತ್ತಿದೆ.",
        "{location} ನಲ್ಲಿ ನಿರಂತರ ನೀರು ಸೋರಿಕೆ.",
        "ಪೈಪ್ ಒಡೆದು ನೀರು ರಸ್ತೆಯಲ್ಲಿ ಹರಿಯುತ್ತಿದೆ {location}.",
        "ಕೇವಲ ಹನಿಗಳು ಮಾತ್ರ ಬರುತ್ತಿವೆ, ದೊಡ್ಡ ಸೋರಿಕೆ ಇಲ್ಲ {location}.",
        "ಟ್ಯಾಪ್ ಸೋರುತ್ತಿದೆ, ದಯವಿಟ್ಟು ಸರಿಪಡಿಸಿ."
    ],
    'Supply': [
        # English
        "No water supply since {time}.",
        "We are not getting water in {location}.",
        "Low water pressure today.",
        "Water timing is not followed, please fix.",
        "When will water come today? No supply.",
        "Completely dry taps in {location} since {time}.",
        "Water supply is very erratic in our area.",
        "Not enough water pressure to reach the overhead tank.",
        "We have been waiting for water since {time}.",
        "No supply at all in {location}.",
        
        # Transliterated Kannada (Kanglish)
        "Water supply illa {time} inda.",
        "neeru barthilla nam manege.",
        "watr suply is vry bad in {location}.",
        "no suply of watr since {time}.",
        "Kaveri neeru bandilla.",
        "pressure tumba low ide {location} nalli.",
        "yaavaga neeru bartade? {time} inda kawtidivi.",
        "neeru sari yagi supply agthilla.",
        
        # Native Kannada
        "{time} ಇಂದ ನೀರು ಬಂದಿಲ್ಲ.",
        "{location} ನಲ್ಲಿ ನೀರಿನ ಸರಬರಾಜು ಇಲ್ಲ.",
        "ಕಾವೇರಿ ನೀರು ಬರುತ್ತಿಲ್ಲ.",
        "ಇಂದು ನೀರಿನ ಒತ್ತಡ ತುಂಬಾ ಕಡಿಮೆಯಾಗಿದೆ.",
        "ನೀರಿನ ಸಮಯ ಸರಿಯಾಗಿ ಪಾಲಿಸುತ್ತಿಲ್ಲ.",
        "ನಮ್ಮ ಮನೆಗೆ ನೀರು ಬರುತ್ತಿಲ್ಲ, ದಯವಿಟ್ಟು ಗಮನಿಸಿ."
    ],
    'Contamination': [
        # English
        "Water smells bad and is yellowish.",
        "Drinking water is contaminated in {location}.",
        "bad smll wter cming frm tap.",
        "Water is muddy and unhygienic.",
        "getting dirty water for drinking.",
        "water colour is black.",
        "drnking watr is nt gud, it is plluted.",
        "Sewage mixed with drinking water.",
        "The water is brown and has particles in it.",
        "Foul odor coming from the supplied water.",
        "Water is not safe for drinking today.",
        
        # Transliterated Kannada (Kanglish)
        "Neeru galiju agide, kadi neeru barthide.",
        "neeralli kachara barthide.",
        "vasane bartide neerinda {location}.",
        "kudiyoke agalla, neeru halagide.",
        "sewage mix agide neeru jote.",
        "neeru full black agide {location} nalli.",
        
        # Native Kannada
        "ನೀರು ಕೆಟ್ಟ ವಾಸನೆ ಬರುತ್ತಿದೆ ಮತ್ತು ಹಳದಿಯಾಗಿದೆ.",
        "{location} ನಲ್ಲಿ ಕುಡಿಯುವ ನೀರು ಕಲುಷಿತಗೊಂಡಿದೆ.",
        "ಕೊಳಚೆ ನೀರು ಕುಡಿಯುವ ನೀರಿನೊಂದಿಗೆ ಬೆರೆತಿದೆ.",
        "ಕುಡಿಯಲು ನೀರು ಯೋಗ್ಯವಾಗಿಲ್ಲ.",
        "ನೀರಿನಲ್ಲಿ ಕಸ ಮತ್ತು ಮಣ್ಣು ಬರುತ್ತಿದೆ."
    ],
    'Drainage': [
        # English
        "Drainage is blocked and overflowing in {location}.",
        "drinage blok in frnt of house.",
        "Manhole is open and overflowing.",
        "Sewage water entering the road.",
        "Gutter is blocked, very bad smell.",
        "drain is flul of grabage.",
        "water stagnation due to blocked drainage.",
        "Mosquitoes increasing because of drainage leak.",
        "The public drain is choked and overflowing heavily.",
        "Please clear the blocked drainage near {location}.",
        
        # Transliterated Kannada (Kanglish)
        "Drainage block agide, vasane barthide {location}.",
        "charandi block agide {location} nalli.",
        "manhole open ide mattu overflow agthide.",
        "sewage neeru rastege bartide.",
        "full kachara tumbide drain nalli.",
        "sೊಳ್ಳೆ ಕಾಟ ಹೆಚ್ಚಾಗಿದೆ, drainage clean madi.",
        
        # Native Kannada
        "{location} ನಲ್ಲಿ ಒಳಚರಂಡಿ ಕಟ್ಟಿಕೊಂಡಿದೆ ಮತ್ತು ಉಕ್ಕಿ ಹರಿಯುತ್ತಿದೆ.",
        "ಮ್ಯಾನ್‌ಹೋಲ್ ತೆರೆದಿದೆ ಮತ್ತು ಕೊಳಚೆ ನೀರು ಹೊರಬರುತ್ತಿದೆ.",
        "ಚರಂಡಿ ಕಟ್ಟಿಕೊಂಡು ಕೆಟ್ಟ ವಾಸನೆ ಬರುತ್ತಿದೆ.",
        "ರಸ್ತೆಗೆ ಕೊಳಚೆ ನೀರು ಹರಿಯುತ್ತಿದೆ.",
        "ಕಸದಿಂದ ಚರಂಡಿ ಕಟ್ಟಿಕೊಂಡಿದೆ, ದಯವಿಟ್ಟು ಸ್ವಚ್ಛಗೊಳಿಸಿ."
    ]
}

locations = [
    "Whitefield", "KR Puram", "Marathahalli", "Electronic City", "HSR Layout",
    "Indiranagar", "Yelahanka", "Rajajinagar", "Jayanagar", "Hebbal"
]

# Date range: past 3–6 months from script execution date
_today = datetime.date.today()
_date_range_start = _today - datetime.timedelta(days=180)  # ~6 months back
_date_range_end   = _today - datetime.timedelta(days=90)   # ~3 months back
_date_range_days  = (_date_range_end - _date_range_start).days

def generate_random_date():
    """Return a random date string (YYYY-MM-DD) within the past 3–6 months."""
    offset = random.randint(0, _date_range_days)
    return (_date_range_start + datetime.timedelta(days=offset)).strftime('%Y-%m-%d')
times = ["morning", "yesterday", "2 days", "last night", "1 week", "3 days", "today"]

def generate_priority(category, text):
    text_lower = text.lower()
    
    # Extensive bilingual heuristic for realistic ground-truth labels
    high_keywords = [
        'burst', 'sewage mixed', 'yellowish', 'overflowing', 'since 2 days', 'since 1 week', 
        'since 3 days', 'no water', 'illa', 'odedide', 'everywhere', 'black', 'immediately', 
        'emergency', 'halagide', 'kudiyoke agalla', 'rastege bartide', 'ಉಕ್ಕಿ', 'ಒಡೆದಿದೆ', 
        'ಬಂದಿಲ್ಲ', 'ಕಲುಷಿತ', 'ತುರ್ತು', 'ಕೊಳಚೆ'
    ]
    low_keywords = [
        'low pressure', 'timing', 'smell', 'vasane', 'pressure', 'bad smll', 'no leakage', 
        'drops coming out', 'minor leak', 'few drops', 'swalpa', 'ಹನಿಗಳು', 'ಸಣ್ಣ', 'ವಾಸನೆ'
    ]
    
    if any(k in text_lower for k in high_keywords):
        return 'High'
    elif any(k in text_lower for k in low_keywords):
        return 'Low'
    else:
        return 'Medium'

data = []

# Generate 15,000 robust records for a deployable scale app
for _ in range(15000):
    category = random.choice(list(templates.keys()))
    template = random.choice(templates[category])
    
    chosen_location = random.choice(locations)
    complaint_text = template.format(
        location=chosen_location,
        time=random.choice(times)
    )
    
    priority = generate_priority(category, complaint_text)
    
    # Add 5% noise for robustness so the model doesn't overfit to pure logic
    if random.random() < 0.05:
        priority = random.choice(['High', 'Medium', 'Low'])
        
    data.append({
        'complaint_text': complaint_text,
        'category': category,
        'priority': priority,
        'location': chosen_location,
        'date': generate_random_date()
    })

df = pd.DataFrame(data)
df = df.sample(frac=1).reset_index(drop=True)

df.to_csv('large_water_complaints_dataset.csv', index=False)
print(f"Generated large_water_complaints_dataset.csv with {len(df)} rows.")
print(f"Columns: {list(df.columns)}")
print("\nCategory Distribution:")
print(df['category'].value_counts())
print("\nPriority Distribution:")
print(df['priority'].value_counts())
print("\nLocation Distribution:")
print(df['location'].value_counts())
print("\nDate Range:")
print(f"  From: {df['date'].min()}")
print(f"  To:   {df['date'].max()}")
