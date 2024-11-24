import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

st.set_page_config(
    page_title="Aplikasi Pencatat Pengeluaran",  # Judul halaman yang akan muncul di tab browser
    page_icon=":moneybag:",  # Ikon halaman (gunakan emoji atau path ke file gambar)
    layout="wide",  # Layout lebar, bisa juga "centered" untuk layout lebih sempit
    initial_sidebar_state="expanded"  # Status awal sidebar, bisa "expanded" atau "collapsed"
)

# Inisialisasi state
if 'current_budget' not in st.session_state:
    st.session_state.current_budget = 0

if 'remaining_budget' not in st.session_state:
    st.session_state.remaining_budget = 0

if 'transactions' not in st.session_state:
    st.session_state.transactions = pd.DataFrame(columns=['Hari', 'Budget Harian', 'Pengeluaran', 'Pemasukan'])

# Judul aplikasi
st.title("Aplikasi Pencatat Pengeluaran dan Pemasukan Harian")

# Layout dua kolom
col1, col2 = st.columns(2)

with col1:
    # Pilihan budget harian
    daily_budget = st.selectbox(
        "Pilih budget harian (Rp):",
        options=[50000, 55000, 60000, 65000, 70000],
        format_func=lambda x: f"Rp{x:,}"
    )

    # Tombol untuk mengatur budget awal
    if st.button("Set Budget Awal"):
        st.session_state.current_budget = daily_budget + st.session_state.remaining_budget
        st.session_state.remaining_budget = 0
        st.success(f"Budget harian Anda telah diatur menjadi Rp{st.session_state.current_budget:,}")

    # Opsi untuk menampilkan input pemasukan
    show_income_input = st.checkbox("Tambah pemasukan harian")

    # Input pemasukan harian (hanya jika checkbox diaktifkan)
    if show_income_input:
        daily_income = st.number_input("Masukkan pemasukan harian (Rp):", min_value=0, value=0, step=1000)
        if st.button("Catat Pemasukan"):
            st.session_state.current_budget += daily_income
            st.success(f"Pemasukan Rp{daily_income:,} berhasil dicatat.")
            st.info(f"Budget Anda saat ini: Rp{st.session_state.current_budget:,}")

with col2:
    # Input pengeluaran harian
    daily_expense = st.number_input("Masukkan pengeluaran harian (Rp):", min_value=0, value=0, step=1000)

    # Tombol untuk mencatat pengeluaran
    if st.button("Catat Pengeluaran"):
        day = len(st.session_state.transactions) + 1
        new_transaction = pd.DataFrame({
            'Hari': [day],
            'Budget Harian': [st.session_state.current_budget],
            'Pengeluaran': [daily_expense],
            'Pemasukan': [daily_income if show_income_input else 0]
        })
        st.session_state.transactions = pd.concat([st.session_state.transactions, new_transaction], ignore_index=True)
        st.session_state.current_budget -= daily_expense
        st.session_state.remaining_budget = st.session_state.current_budget
        st.success(f"Pengeluaran Rp{daily_expense:,} berhasil dicatat.")
        st.info(f"Sisa budget hari ini: Rp{st.session_state.remaining_budget:,}")

show_table = st.checkbox("Tampilkan tabel transaksi")

# Menampilkan tabel transaksi
if show_table and not st.session_state.transactions.empty:
    st.write("### Tabel Transaksi Harian")
    st.dataframe(st.session_state.transactions)

# Opsi untuk menampilkan fitur edit transaksi
show_edit_transactions = st.checkbox("Tampilkan fitur edit transaksi")

if show_edit_transactions and not st.session_state.transactions.empty:
    st.write("### Edit Transaksi")
    
    # Pilih hari untuk diedit
    edit_day = st.selectbox(
        "Pilih hari untuk diedit:",
        st.session_state.transactions['Hari']
    )

    if edit_day:
        # Ambil data hari yang dipilih
        transaction_to_edit = st.session_state.transactions[st.session_state.transactions['Hari'] == edit_day].iloc[0]

        # Form untuk mengedit data
        new_budget = st.number_input("Budget Harian Baru (Rp):", min_value=0, value=int(transaction_to_edit['Budget Harian']), step=1000)
        new_expense = st.number_input("Pengeluaran Baru (Rp):", min_value=0, value=int(transaction_to_edit['Pengeluaran']), step=1000)
        new_income = st.number_input("Pemasukan Baru (Rp):", min_value=0, value=int(transaction_to_edit['Pemasukan']), step=1000)

        # Tombol untuk menyimpan perubahan
        if st.button("Simpan Perubahan"):
            idx = st.session_state.transactions[st.session_state.transactions['Hari'] == edit_day].index[0]
            st.session_state.transactions.at[idx, 'Budget Harian'] = new_budget
            st.session_state.transactions.at[idx, 'Pengeluaran'] = new_expense
            st.session_state.transactions.at[idx, 'Pemasukan'] = new_income
            st.success("Data berhasil diperbarui.")

show_graph = st.checkbox("Tampilkan grafik transaksi")

if show_graph and not st.session_state.transactions.empty:
    st.write("### Grafik Transaksi Harian")

    # Plot menggunakan Matplotlib
    plt.figure(figsize=(10, 5))

    # Budget Harian (warna hijau)
    plt.plot(st.session_state.transactions['Hari'], st.session_state.transactions['Budget Harian'], 
            label='Budget Harian', marker='o', color='green')

    # Pengeluaran (warna merah)
    plt.plot(st.session_state.transactions['Hari'], st.session_state.transactions['Pengeluaran'], 
            label='Pengeluaran', marker='x', color='red')

    # Pemasukan (warna biru)
    plt.bar(st.session_state.transactions['Hari'], st.session_state.transactions['Pemasukan'], 
            label='Pemasukan', color='blue', alpha=0.6)

    # Mengatur interval sumbu x (horizontal) ke 1
    plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(1))  # Mengatur jarak setiap tick pada sumbu x menjadi 1
    plt.gca().xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x)}'))  # Format label agar menjadi integer

    # Menyesuaikan label dan judul grafik
    plt.xlabel("Hari")
    plt.ylabel("Rp")
    plt.title("Grafik Budget Harian, Pengeluaran, dan Pemasukan")
    plt.legend()
    plt.grid(True)

    # Menampilkan grafik
    st.pyplot(plt)
