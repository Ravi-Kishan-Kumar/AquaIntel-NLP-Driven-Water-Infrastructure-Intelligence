"""
auth/db.py
----------
Database layer for the Water Complaint Analyzer.
Handles SQLite operations for users and complaints.
"""

import sqlite3
import bcrypt
import os
from datetime import datetime
import uuid

# ── Paths ──────────────────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, 'water_complaints.db')

# ── Authority secret code ──────────────────────────────────────────────────────
AUTHORITY_CODE = "WATER_AUTH_2024"

# ── Bangalore localities list ──────────────────────────────────────────────────
BANGALORE_REGIONS = sorted([
    "Jayanagar", "Koramangala", "Whitefield", "HSR Layout",
    "Indiranagar", "Marathahalli", "Rajajinagar", "Malleswaram",
    "Banashankari", "Electronic City", "Hebbal", "Yeshwanthpur",
    "JP Nagar", "BTM Layout", "Vijayanagar", "Basavanagudi",
    "Chamrajpet", "Shivajinagar", "Ulsoor", "Richmond Town",
    "MG Road", "Yelahanka", "Devanahalli", "KR Puram",
    "Bellandur", "Sarjapur", "Bommanahalli", "Domlur",
    "Frazer Town", "Vasanth Nagar", "Sadashivanagar", "RT Nagar",
    "Jalahalli", "Peenya", "Kengeri", "Uttarahalli",
    "Hulimavu", "Harlur", "Varthur", "Kadugodi",
    "Mahadevapura", "Krishnarajapuram", "Hoodi", "Brookefield",
    "Banaswadi", "Ramamurthy Nagar", "HBR Layout", "Kammanahalli",
    "Horamavu", "Kalyan Nagar", "Gottigere", "Hongasandra",
    "Carmelram", "Ejipura", "Cox Town", "Benson Town",
    "MS Ramaiah Nagar", "Magadi Road", "Mysore Road", "Tumkur Road",
    "Other / Not Listed"
])

# ── GPS coordinates for map visualisation ─────────────────────────────────────
REGION_COORDINATES = {
    "Jayanagar":         (12.9308, 77.5838),
    "Koramangala":       (12.9352, 77.6245),
    "Whitefield":        (12.9698, 77.7499),
    "HSR Layout":        (12.9116, 77.6389),
    "Indiranagar":       (12.9784, 77.6408),
    "Marathahalli":      (12.9591, 77.6974),
    "Rajajinagar":       (12.9913, 77.5555),
    "Malleswaram":       (13.0035, 77.5668),
    "Banashankari":      (12.9255, 77.5468),
    "Electronic City":   (12.8399, 77.6770),
    "Hebbal":            (13.0357, 77.5970),
    "Yeshwanthpur":      (13.0226, 77.5399),
    "JP Nagar":          (12.9074, 77.5870),
    "BTM Layout":        (12.9166, 77.6101),
    "Vijayanagar":       (12.9716, 77.5351),
    "Basavanagudi":      (12.9423, 77.5750),
    "Chamrajpet":        (12.9596, 77.5620),
    "Shivajinagar":      (12.9851, 77.6010),
    "Ulsoor":            (12.9778, 77.6223),
    "Richmond Town":     (12.9633, 77.6014),
    "MG Road":           (12.9757, 77.6101),
    "Yelahanka":         (13.1005, 77.5963),
    "Devanahalli":       (13.2480, 77.7115),
    "KR Puram":          (13.0023, 77.6936),
    "Bellandur":         (12.9262, 77.6750),
    "Sarjapur":          (12.9010, 77.7140),
    "Bommanahalli":      (12.8967, 77.6373),
    "Domlur":            (12.9608, 77.6401),
    "Frazer Town":       (12.9797, 77.6175),
    "Vasanth Nagar":     (12.9880, 77.5962),
    "Sadashivanagar":    (13.0068, 77.5850),
    "RT Nagar":          (13.0168, 77.5955),
    "Jalahalli":         (13.0377, 77.5250),
    "Peenya":            (13.0282, 77.5183),
    "Kengeri":           (12.9082, 77.4820),
    "Uttarahalli":       (12.8971, 77.5386),
    "Hulimavu":          (12.8860, 77.6160),
    "Harlur":            (12.9048, 77.6700),
    "Varthur":           (12.9374, 77.7361),
    "Kadugodi":          (12.9891, 77.7360),
    "Mahadevapura":      (12.9924, 77.7056),
    "Krishnarajapuram":  (13.0037, 77.6714),
    "Hoodi":             (12.9916, 77.7170),
    "Brookefield":       (12.9743, 77.7117),
    "Banaswadi":         (13.0121, 77.6489),
    "Ramamurthy Nagar":  (13.0155, 77.6681),
    "HBR Layout":        (13.0211, 77.6482),
    "Kammanahalli":      (13.0040, 77.6438),
    "Horamavu":          (13.0273, 77.6605),
    "Kalyan Nagar":      (13.0213, 77.6344),
    "Gottigere":         (12.8693, 77.5999),
    "Hongasandra":       (12.8989, 77.5997),
    "Carmelram":         (12.8985, 77.6881),
    "Ejipura":           (12.9501, 77.6239),
    "Cox Town":          (12.9861, 77.6115),
    "Benson Town":       (13.0023, 77.6093),
    "MS Ramaiah Nagar":  (13.0200, 77.5631),
    "Magadi Road":       (12.9720, 77.5265),
    "Mysore Road":       (12.9420, 77.5010),
    "Tumkur Road":       (13.0650, 77.5315),
    "Other / Not Listed":(12.9716, 77.5946),
}

# ── Connection ─────────────────────────────────────────────────────────────────
def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# ── Schema Initialisation ──────────────────────────────────────────────────────
def init_db():
    """Create tables if they don't exist."""
    conn = get_connection()
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name    TEXT    NOT NULL,
            email        TEXT    UNIQUE NOT NULL,
            password_hash TEXT   NOT NULL,
            role         TEXT    NOT NULL CHECK(role IN ('citizen', 'authority')),
            phone        TEXT    DEFAULT '',
            created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS complaints (
            id                   INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id            TEXT    UNIQUE NOT NULL,
            user_id              INTEGER NOT NULL,
            complaint_text       TEXT    NOT NULL,
            location             TEXT    NOT NULL,
            category             TEXT,
            priority             TEXT,
            confidence_category  REAL    DEFAULT 0.0,
            confidence_priority  REAL    DEFAULT 0.0,
            status               TEXT    DEFAULT 'Pending',
            resolution_note      TEXT    DEFAULT '',
            submitted_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved_at          TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()

# ── Helpers ────────────────────────────────────────────────────────────────────
def generate_ticket_id():
    date_str = datetime.now().strftime('%Y%m%d')
    suffix   = str(uuid.uuid4())[:6].upper()
    return f"WC-{date_str}-{suffix}"

# ── User CRUD ──────────────────────────────────────────────────────────────────
def create_user(full_name, email, password, role, phone=""):
    """Register a new user. Returns (success: bool, message: str)."""
    conn = get_connection()
    c    = conn.cursor()
    try:
        pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        c.execute(
            'INSERT INTO users (full_name, email, password_hash, role, phone) VALUES (?,?,?,?,?)',
            (full_name, email, pw_hash, role, phone)
        )
        conn.commit()
        return True, "Account created successfully! Please log in."
    except sqlite3.IntegrityError:
        return False, "This email address is already registered."
    finally:
        conn.close()

def get_user_by_email(email):
    """Return user dict or None."""
    conn = get_connection()
    c    = conn.cursor()
    c.execute('SELECT * FROM users WHERE email = ?', (email,))
    row  = c.fetchone()
    conn.close()
    return dict(row) if row else None

def verify_login(email, password):
    """Verify credentials. Returns user dict on success, else None."""
    user = get_user_by_email(email)
    if user and bcrypt.checkpw(password.encode(), user['password_hash'].encode()):
        return user
    return None

# ── Complaint CRUD ─────────────────────────────────────────────────────────────
def submit_complaint(user_id, complaint_text, location,
                     category, priority, conf_cat, conf_pri):
    """Insert a new complaint and return the ticket_id."""
    conn      = get_connection()
    c         = conn.cursor()
    ticket_id = generate_ticket_id()
    c.execute(
        '''INSERT INTO complaints
           (ticket_id, user_id, complaint_text, location,
            category, priority, confidence_category, confidence_priority)
           VALUES (?,?,?,?,?,?,?,?)''',
        (ticket_id, user_id, complaint_text, location,
         category, priority, conf_cat, conf_pri)
    )
    conn.commit()
    conn.close()
    return ticket_id

def get_complaints_by_user(user_id):
    """Return all complaints submitted by a specific citizen."""
    conn = get_connection()
    c    = conn.cursor()
    c.execute(
        'SELECT * FROM complaints WHERE user_id=? ORDER BY submitted_at DESC',
        (user_id,)
    )
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_complaints():
    """Return all complaints joined with user info (for authority)."""
    conn = get_connection()
    c    = conn.cursor()
    c.execute('''
        SELECT c.*, u.full_name, u.email AS citizen_email
        FROM   complaints c
        JOIN   users u ON c.user_id = u.id
        ORDER  BY c.submitted_at DESC
    ''')
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_complaints_by_region(location):
    """Return all complaints for a specific Bangalore locality."""
    conn = get_connection()
    c    = conn.cursor()
    c.execute(
        '''SELECT c.*, u.full_name FROM complaints c
           JOIN users u ON c.user_id=u.id
           WHERE c.location=? ORDER BY c.submitted_at DESC''',
        (location,)
    )
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_complaint_status(ticket_id, status, resolution_note=""):
    """Update status and optional resolution note (authority action)."""
    conn        = get_connection()
    c           = conn.cursor()
    resolved_at = datetime.now().isoformat() if status == 'Resolved' else None
    c.execute(
        '''UPDATE complaints
           SET status=?, resolution_note=?, resolved_at=?
           WHERE ticket_id=?''',
        (status, resolution_note, resolved_at, ticket_id)
    )
    conn.commit()
    conn.close()

def get_complaint_stats():
    """Return aggregate stats dict for the overview cards."""
    conn = get_connection()
    c    = conn.cursor()
    stats = {}
    c.execute('SELECT COUNT(*) FROM complaints')
    stats['total'] = c.fetchone()[0]
    for s in ('Pending', 'In Progress', 'Resolved'):
        c.execute('SELECT COUNT(*) FROM complaints WHERE status=?', (s,))
        stats[s.lower().replace(' ', '_')] = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM complaints WHERE priority='High' AND status!='Resolved'")
    stats['high_priority_open'] = c.fetchone()[0]
    conn.close()
    return stats
