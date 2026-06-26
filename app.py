import streamlit as st
import sqlite3
import pandas as pd 

VAULT_TASKS = r"C:\Users\temp-it.DESKTOP-8HTQT4S\claudexobsidian\think\todolist\active.md"

WORKOUTS = {
    "Push": ["Bench Press", "OHP", "Incline Bench", "Lateral Raise", "Tricep Pushdown"],
    "Pull":  ["Pull-ups", "Seated Row", "Lat Pulldown", "Face Pull", "Preacher Curl"],
    "Legs":  ["Squat", "Leg Press", "Leg Extension", "Leg Curl", "Calf Raise"],
    "Upper": ["Incline Bench", "Lat Pulldown", "Seated Row", "Lateral Raise", "Overhead Tricep Ext", "Preacher Curl"],
    "Lower": ["RDL", "Leg Press", "Leg Curl", "Leg Extension", "Calf Raise"],
}

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

def init_fitness_db():
    conn = get_connection()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS Fitness_Log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    workout_day TEXT NOT NULL,
    exercise TEXT NOT NULL,
    weight REAL NOT NULL,
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

def get_spending():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM spending ORDER BY date DESC", conn)
    conn.close()
    return df

def add_workout(date, workout_day, exercise, weight, note):
    conn = get_connection()
    conn.execute(
        "INSERT INTO Fitness_Log (date, workout_day, exercise, weight, note) VALUES (?, ?, ?, ?, ?)",
        (date, workout_day, exercise, weight, note)
    )
    conn.commit()
    conn.close()

def get_workout():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM Fitness_Log ORDER BY date", conn)
    conn.close()
    return df

init_db()

st.title("Personal Dashboard")

tab1, tab2, tab3 =st.tabs(["spending", "fitness", "tasks"])

with tab1: 
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

    st.header("Spending")
    df = get_spending()

    # --- month-to-date metric ---
    this_month = pd.Timestamp.now().strftime("%Y-%m")
    month_df = df[df["date"].str.startswith(this_month)]
    total = month_df["amount"].sum()
    st.metric("Spent this month", f"₹{total:,.0f}", delta=f"₹{10000 - total:,.0f} Left")
    st.subheader("By category")

    by_category = month_df.groupby("category")["amount"].sum()
    st.bar_chart(by_category)

    st.dataframe(df)

init_fitness_db()

with tab2:
    st.header("Fitness")
    day = st.selectbox("Workout day", list(WORKOUTS.keys()))

    with st.form("fitness_form"):
        date = st.date_input("Date")
        weights = {}
        for exercise in WORKOUTS[day]:
            weights[exercise] = st.number_input(exercise, min_value=0.0, step=2.5)
        note = st.text_input("Note")
        submitted = st.form_submit_button("Save workout")

    if submitted:
        for exercise, weight in weights.items():
            add_workout(date.isoformat(), day, exercise, weight, note)
        st.success("Workout saved!")

    st.subheader("Progress")
    fdf = get_workout()
    exercise_choice = st.selectbox("Track exercise", fdf["exercise"].unique())
    ex_df = fdf[fdf["exercise"] == exercise_choice]
    st.line_chart(ex_df, x="date", y="weight")

with tab3:
    st.header("Tasks & Goals")
    with open(VAULT_TASKS, encoding="utf-8") as f:
        text = f.read()
    st.markdown(text)
