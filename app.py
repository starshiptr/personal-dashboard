import streamlit as st
import sqlite3

def get_connection():
    return sqlite3.connect("dashboard.db")    
def init_db():
    conn = get_connection()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS spending (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    note TEXT
    )
""")
    conn.commit()
    conn.close()
def add_spending(date, amount, category, note):
    conn = get_connection()
    conn.execute(
    "INSERT INTO spending (date, amount, category, note) VALUES (?, ?, ?, ?)",
    (date, amount, category, note)   
    )
    conn.commit()
    conn.close()

init_db()

st.title("Personal Dashboard")
with st.form("spending_form"):
    date = st.date_input("Date")
    amount = st.number_input("Amount (₹)", min_value=0.0, step=10.0)
    category = st.selectbox("Category", ["Food & Dining", "Transport", "Shopping", "Personal Care",
 "Entertainment", "Health", "Subscriptions", "Misc"] )
    note = st.text_input("Note")
    submitted = st.form_submit_button("Add expense")

if submitted:
    add_spending(date.isoformat(), amount, category, note)
    st.success("Saved!")
