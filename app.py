import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from abc import ABC, abstractmethod

st.set_page_config(page_title="Personal Finance Tracker", layout="wide")

# =======================
# ABSTRACT BASE CLASS (ABSTRACTION)
# =======================
class Transaction(ABC):
    def __init__(self, date, category, amount):
        self._date = date          # Encapsulation
        self._category = category
        self._amount = amount

    @abstractmethod
    def apply(self):
        pass

    @abstractmethod
    def get_type(self):
        pass


# =======================
# INHERITANCE – Income
# =======================
class Income(Transaction):
    def apply(self):
        return self._amount

    def get_type(self):
        return "Income"


# =======================
# INHERITANCE – Expense
# =======================
class Expense(Transaction):
    def apply(self):
        return -self._amount

    def get_type(self):
        return "Expense"


# =======================
# FINANCE TRACKER (ENCAPSULATION)
# =======================
class FinanceTracker:
    def __init__(self):
        if "data" not in st.session_state:
            st.session_state.data = []

    def add_transaction(self, transaction):
        if transaction._amount <= 0:
            raise ValueError("Amount must be positive")
        st.session_state.data.append(transaction)

    def to_dataframe(self):
        return pd.DataFrame([{
            "date": t._date,
            "t_type": t.get_type(),
            "category": t._category,
            "amount": t._amount
        } for t in st.session_state.data])


# =======================
# REPORT GENERATOR (ABSTRACTION)
# =======================
class ReportGenerator:
    @staticmethod
    def generate_report(df):
        income = df[df["t_type"] == "Income"]["amount"].sum()
        expense = df[df["t_type"] == "Expense"]["amount"].sum()
        balance = income - expense

        return f"""PERSONAL FINANCE REPORT
------------------------
Total Income  : ₹ {income}
Total Expense : ₹ {expense}
Savings/Loss  : ₹ {balance}

Generated on  : {datetime.now().strftime('%d-%m-%Y %H:%M')}
"""


# =======================
# STREAMLIT UI
# =======================
st.title("Personal Finance Tracker")

tracker = FinanceTracker()

with st.sidebar:
    st.header("➕ Add Transaction")
    date = st.date_input("Date")
    t_type = st.selectbox("Type", ["Income", "Expense"])
    category = st.selectbox("Category", ["Salary", "Food", "Rent", "Shopping", "Travel", "Others"])
    amount = st.number_input("Amount", min_value=0.0)

    if st.button("Add"):
        try:
            if t_type == "Income":
                txn = Income(date, category, amount)
            else:
                txn = Expense(date, category, amount)

            tracker.add_transaction(txn)
            st.success("Transaction Added")
        except ValueError as e:
            st.error(str(e))

df = tracker.to_dataframe()

if not df.empty:
    st.subheader("📋 Transactions")
    st.dataframe(df)

    income = df[df["t_type"] == "Income"]["amount"].sum()
    expense = df[df["t_type"] == "Expense"]["amount"].sum()
    balance = income - expense

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Income", f"₹ {income}")
    col2.metric("Total Expense", f"₹ {expense}")
    col3.metric("Savings", f"₹ {balance}")

    if expense > income:
        st.error("⚠️ Warning: Expenses exceed Income!")

    # ---------- CHARTS ----------
    st.subheader("📊 Analysis")

    col4, col5 = st.columns(2)

    with col4:
        fig, ax = plt.subplots()
        ax.bar(["Income", "Expense"], [income, expense])
        st.pyplot(fig)

    with col5:
        exp_df = df[df["t_type"] == "Expense"]
        if not exp_df.empty:
            fig2, ax2 = plt.subplots()
            exp_df.groupby("category")["amount"].sum().plot.pie(autopct='%1.1f%%', ax=ax2)
            ax2.set_ylabel("")
            st.pyplot(fig2)

    # ---------- REPORT ----------
    st.subheader("📄 Generate Report")
    report_text = ReportGenerator.generate_report(df)
    st.text(report_text)

    st.download_button(
        label="⬇️ Download Report",
        data=report_text,
        file_name="Finance_Report.txt",
        mime="text/plain"
    )
else:
    st.info("No transactions added yet.")

