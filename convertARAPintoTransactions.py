import streamlit as st
import pandas as pd

def process_ARAP(file):
    ARAP_data = pd.read_excel(file, header=4)
    ARAP_cleaned = ARAP_data.drop(ARAP_data.columns[0], axis=1)
    ARAP_cleaned = ARAP_cleaned.dropna(axis=1, how='all')
    ARAP_cleaned = ARAP_cleaned.dropna(how='all')
    AP = True if ARAP_cleaned['Transaction Type'].str.contains('Bill').any() else False
    ARAP_cleaned = ARAP_cleaned[['Due Date', 'Currency', 'Foreign Amount']] 
    ARAP_cleaned = ARAP_cleaned.dropna(subset=['Due Date'])

    ARAP_grouped = ARAP_cleaned.groupby(['Due Date', 'Currency']).agg({'Foreign Amount': 'sum'})
    ARAP_grouped = ARAP_grouped.reset_index()
    ARAP_grouped.rename(columns={'Foreign Amount': 'Sum of Foreign Amount'}, inplace=True)
    ARAP_grouped['Reference'] = f"FYE2023 Conversion: {'AP' if AP else 'AR'} Balance Transfer"
    ARAP_grouped['Item / Description'] = "FYE2023 Conversion: " + ARAP_grouped['Currency'] + " Ageing Total Due on " + ARAP_grouped['Due Date']
    ARAP_grouped['Bill Account'] = 'Conversion Clearing Account'
    ARAP_grouped['FX Rate'] = 'FYE Rate'

    pivot_table = ARAP_grouped[['Due Date', 'Currency', 'Sum of Foreign Amount', 'Reference', 'Item / Description', 'Bill Account', 'FX Rate']]
    pivot_table.rename(columns={'Item / Description': 'Bill Reference'}, inplace=True)
    pivot_table.rename(columns={'Reference': 'Item / Description'}, inplace=True)
    pivot_table.rename(columns={'Due Date': 'Date'}, inplace=True)
    pivot_table.rename(columns={'Sum of Foreign Amount': 'Total Amount (SGD)'}, inplace=True)
    pivot_table[['Supplier', 'Tax Included in Amount', 'Internal Notes', 'Amount Paid', 'Payment Method', 'Payment Account', 'Payment Ref #', 'Transaction Fee Included (SGD)', 'Tax Included in Transaction Fees (SGD)', 'Transaction Fee Expense Account', 'Amount Withholding', 'Withholding Ref #']] = ''

    final_data = pivot_table[['Bill Reference', 'Supplier', 'Date', 'Item / Description', 'Bill Account', 'Tax Included in Amount', 'Total Amount (SGD)', 'Internal Notes', 'Amount Paid', 'Payment Method', 'Payment Account', 'Payment Ref #', 'Transaction Fee Included (SGD)', 'Tax Included in Transaction Fees (SGD)', 'Transaction Fee Expense Account', 'Amount Withholding', 'Withholding Ref #', 'Currency']]

    return final_data

def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

st.title('Convert AR and AP Reports into Transactions Tool')

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    processed_data = process_ARAP(uploaded_file)
    st.write("Processed Data", processed_data)
    csv = convert_df_to_csv(processed_data)
    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name='Transactions.csv',
        mime='text/csv',
    )