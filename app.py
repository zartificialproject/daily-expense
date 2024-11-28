import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt

# Path file untuk menyimpan transaksi
TRANSACTION_FILE = "transactions.csv"

st.set_page_config(
    page_title="Daily Expense Tracker",
    page_icon=":moneybag:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Fungsi untuk memuat data dari file
def load_transactions():
    if os.path.exists(TRANSACTION_FILE):
        return pd.read_csv(TRANSACTION_FILE)
    else:
        return pd.DataFrame(columns=['Hari', 'Budget Harian', 'Pengeluaran', 'Pemasukan', 'Catatan'])

# Fungsi untuk menyimpan data ke file
def save_transactions(transactions):
    transactions.to_csv(TRANSACTION_FILE, index=False)

# Inisialisasi state
if 'current_budget' not in st.session_state:
    st.session_state.current_budget = 0

if 'remaining_budget' not in st.session_state:
    st.session_state.remaining_budget = 0

if 'transactions' not in st.session_state:
    st.session_state.transactions = load_transactions()

# Sidebar Navigation
st.sidebar.title("Navigation")
show_table = st.sidebar.checkbox("Show Transaction Table", value=True)
show_edit_transactions = st.sidebar.checkbox("Enable Transaction Editing")
show_graph = st.sidebar.checkbox("Show Transaction Graph", value=True)

# Judul aplikasi
st.title(":moneybag: Daily Expense Tracker")

# Main Section: Input Form
st.subheader("Log Your Daily Budget and Transactions")
st.markdown("Easily track your daily expenses, income, and remaining budget.")

col1, col2 = st.columns([2, 3])

with col1:
    daily_budget = st.selectbox(
        "Set Default Daily Budget (Rp):",
        options=[50000, 55000, 60000, 65000, 70000],
        format_func=lambda x: f"Rp{x:,}",
        help="Choose your default daily budget."
    )
    if st.button("Set Initial Budget"):
        st.session_state.current_budget = daily_budget + st.session_state.remaining_budget
        st.session_state.remaining_budget = 0
        st.success(f"Your daily budget is set to Rp{st.session_state.current_budget:,}.")

with col2:
    income_amount = st.number_input("Enter Income (Rp):", min_value=0, value=0, step=1000)
    expense_amount = st.number_input("Enter Expense (Rp):", min_value=0, value=0, step=1000)
    transaction_note = st.text_area("Add a Note (Optional):", placeholder="Describe your transaction...")

    if st.button("Log Transactions"):
        if income_amount > 0 or expense_amount > 0:
            day = len(st.session_state.transactions) + 1
            st.session_state.current_budget += income_amount - expense_amount

            new_transaction = pd.DataFrame({
                'Hari': [day],
                'Budget Harian': [st.session_state.current_budget],
                'Pengeluaran': [expense_amount],
                'Pemasukan': [income_amount],
                'Catatan': [transaction_note]
            })
            st.session_state.transactions = pd.concat([st.session_state.transactions, new_transaction], ignore_index=True)
            st.session_state.remaining_budget = st.session_state.current_budget
            save_transactions(st.session_state.transactions)

            st.success(f"Transaction logged successfully!")
        else:
            st.warning("Please enter either an income or expense amount.")

# Section: Transaction Table
if show_table and not st.session_state.transactions.empty:
    st.subheader(":clipboard: Daily Transaction Table")
    st.dataframe(
        st.session_state.transactions.style.format({"Budget Harian": "Rp{:,}", "Pengeluaran": "Rp{:,}", "Pemasukan": "Rp{:,}"})
    )

# Section: Transaction Editing
if show_edit_transactions and not st.session_state.transactions.empty:
    st.subheader("Edit Transaction")
    edit_day = st.selectbox(
        "Select Day to Edit:",
        st.session_state.transactions['Hari']
    )
    if edit_day:
        transaction_to_edit = st.session_state.transactions[st.session_state.transactions['Hari'] == edit_day].iloc[0]
        new_budget = st.number_input("New Daily Budget (Rp):", min_value=0, value=int(transaction_to_edit['Budget Harian']), step=1000)
        new_expense = st.number_input("New Expense (Rp):", min_value=0, value=int(transaction_to_edit['Pengeluaran']), step=1000)
        new_income = st.number_input("New Income (Rp):", min_value=0, value=int(transaction_to_edit['Pemasukan']), step=1000)
        new_note = st.text_area("Update Note:", value=transaction_to_edit['Catatan'])
        if st.button("Save Changes"):
            idx = st.session_state.transactions[st.session_state.transactions['Hari'] == edit_day].index[0]
            st.session_state.transactions.at[idx, 'Budget Harian'] = new_budget
            st.session_state.transactions.at[idx, 'Pengeluaran'] = new_expense
            st.session_state.transactions.at[idx, 'Pemasukan'] = new_income
            st.session_state.transactions.at[idx, 'Catatan'] = new_note
            save_transactions(st.session_state.transactions)
            st.success("Transaction updated successfully.")

# Section: Transaction Graph
if show_graph and not st.session_state.transactions.empty:
    st.subheader("Daily Transaction Graph")
    plt.figure(figsize=(10, 5))
    plt.plot(st.session_state.transactions['Hari'], st.session_state.transactions['Budget Harian'], label='Daily Budget', marker='o', color='green')
    plt.plot(st.session_state.transactions['Hari'], st.session_state.transactions['Pengeluaran'], label='Expense', marker='x', color='red')
    plt.plot(st.session_state.transactions['Hari'], st.session_state.transactions['Pemasukan'], label='Income', marker='s', color='blue')

    plt.xlabel("Day")
    plt.ylabel("Amount (Rp)")
    plt.title("Daily Budget, Expenses, and Income")
    plt.legend()
    plt.grid(True)
    st.pyplot(plt)
