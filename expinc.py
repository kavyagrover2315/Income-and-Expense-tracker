import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go

# ---------- DATABASE ----------
def create_table():
    conn = sqlite3.connect("money_data.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS money (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            amount REAL,
            note TEXT,
            date TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_entry(entry_type, amount, note, date):
    conn = sqlite3.connect("money_data.db")
    c = conn.cursor()
    c.execute("INSERT INTO money (type, amount, note, date) VALUES (?, ?, ?, ?)",
              (entry_type, amount, note, date))
    conn.commit()
    conn.close()

def get_data():
    conn = sqlite3.connect("money_data.db")
    df = pd.read_sql_query("SELECT * FROM money ORDER BY date DESC", conn)
    conn.close()
    return df

# ---------- MAIN ----------
def main():
    st.set_page_config(page_title="💸 Income & Expense Tracker", layout="centered")

    # ---------- CUSTOM STYLE ----------
    st.markdown("""
        <style>
            body {
                background-color: #f4f6f7;
            }
            .css-18e3th9 {
                background-color: #fefefe;
                border-radius: 12px;
                padding: 2rem;
            }
            .stButton>button {
                background-color: #4CAF50;
                color: white;
                border-radius: 8px;
                padding: 0.6rem 1.2rem;
            }
            .stTextInput>div>div>input {
                border-radius: 6px;
            }
        </style>
    """, unsafe_allow_html=True)

    st.title("💸 Personal Income & Expense Tracker")
    st.caption("Simple, clean & made with ❤️ using Streamlit")

    # Sidebar for adding entry
    st.sidebar.header("➕ Add Transaction")
    entry_type = st.sidebar.radio("Type", ["Income", "Expense", "Saving"])
    amount = st.sidebar.number_input("Amount (₹)", min_value=0.0, step=10.0, format="%.2f")
    note = st.sidebar.text_input("Note (e.g., Salary, Rent)")
    date = st.sidebar.date_input("Date")

    if st.sidebar.button("Add"):
        if amount > 0 and note.strip():
            add_entry(entry_type, amount, note, date.strftime("%Y-%m-%d"))
            st.sidebar.success(f"{entry_type} of ₹{amount:,.2f} added!")
        else:
            st.sidebar.warning("Please enter a valid amount and note.")

    # Fetch and display data
    df = get_data()

    if not df.empty:
        st.subheader("📋 Transaction History")
        st.dataframe(df[['date', 'type', 'amount', 'note']])

        # Totals
        total_income = df[df["type"] == "Income"]["amount"].sum()
        total_expense = df[df["type"] == "Expense"]["amount"].sum()
        total_saving = df[df["type"] == "Saving"]["amount"].sum()
        balance = total_income - total_expense

        st.subheader("💰 Overview")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Income", f"₹{total_income:,.2f}")
        col2.metric("Expense", f"₹{total_expense:,.2f}")
        col3.metric("Saving", f"₹{total_saving:,.2f}")
        col4.metric("Remaining", f"₹{balance:,.2f}")

        # Line graph
        st.subheader("📈 Trend Over Time")
        fig = go.Figure()
        colors = {"Income": "green", "Expense": "red", "Saving": "blue"}
        for t in ['Income', 'Expense', 'Saving']:
            filtered = df[df["type"] == t].groupby("date")["amount"].sum().reset_index()
            fig.add_trace(go.Scatter(
                x=filtered["date"], y=filtered["amount"],
                mode="lines+markers", name=t, line=dict(color=colors[t])
            ))

        fig.update_layout(title="Income, Expense & Saving Trends",
                          xaxis_title="Date",
                          yaxis_title="Amount (₹)",
                          template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No transactions yet. Add one from the sidebar!")

if __name__ == "__main__":
    create_table()
    main()
