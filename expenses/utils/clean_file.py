import pandas as pd
import sys
import os
import chardet
import warnings


def clean_excel(input_file):
    output_file = 'expense_out.csv'
    try:
        # Check if input file exists
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file '{input_file}' not found.")
        
        # Handle Excel file (.xlsx) or CSV file (.csv)
        if input_file.lower().endswith('.xlsx'):
            print("Reading Excel file...")
            df = pd.read_excel(input_file, header=None)  # Load without assuming headers
        elif input_file.lower().endswith('.csv'):
            print("Reading CSV file...")
            df = pd.read_csv(input_file, header=None)  # Load without assuming headers
        else:
            raise ValueError("Unsupported file format. Only .xlsx and .csv are supported.")
        
        # Dynamically detect the header row
        header_row_index = df[df.apply(lambda row: row.astype(str).str.contains("Operazione").any(), axis=1)].index[0]
        
        # Re-read the data starting from the header row
        if input_file.lower().endswith('.xlsx'):
            df_cleaned = pd.read_excel(input_file, header=header_row_index)
        else:
            df_cleaned = pd.read_csv(input_file, header=header_row_index)
        
        # Drop specific columns if they exist
        columns_to_drop = ['Contabilizzazione']  # Add any column names to drop
        for col in columns_to_drop:
            if col in df_cleaned.columns:
                df_cleaned = df_cleaned.drop(columns=[col])
        
        # Dynamically drop third and fourth columns if they exist
        if len(df_cleaned.columns) > 3:
            df_cleaned = df_cleaned.drop(df_cleaned.columns[[2, 3]], axis=1)
        
        # Save the cleaned data to the output CSV file
        df_cleaned.to_csv(output_file, index=False)
        print(f"Cleaned file saved to: {output_file}")

    except Exception as e:
        print(f"Error: {e}")
    return output_file


def transform_file_to_prova(input_file, output_file):
    """
    Transforms an expense file into the format of prova.csv.

    Args:
        input_file (str): Path to the input CSV file.
        output_file (str): Path to save the transformed CSV file.

    Returns:
        pd.DataFrame: Transformed DataFrame.


    """

    # Detect encoding (optional)
    with open(input_file, 'rb') as f:
        encoding = chardet.detect(f.read())['encoding']

    # Load the input file
    df = pd.read_csv(input_file,encoding=encoding)

    # Strip column names to handle any trailing spaces
    df.columns = df.columns.str.strip()

    # Rename columns to match the format of prova.csv
    df.rename(columns={
        'Data': 'date',
        'Operazione': 'description',
        'Categoria': 'category',
        'Importo': 'amount'
    }, inplace=True)

    # Analyze the amount column to determine the type
    df['type'] = df['amount'].apply(lambda x: 'expense' if x < 0 else 'income')

    # Convert the amounts to positive values
    df['amount'] = df['amount'].abs()

    # Clean up the category column (strip any extra spaces)
    df['category'] = ''

    # Reorder columns to match prova.csv
    df = df[['amount', 'type', 'date', 'category', 'description']]

    # Save the transformed DataFrame to the output file
    df.to_csv(output_file, index=False)

    return output_file

def clean_and_transform_file(input_file):
    output_file = input_file.replace('.csv', '_cleaned.csv')
    transform_file_to_prova(input_file, output_file)
    return output_file

def clean_and_transform_file(input_file):
    output_file = input_file.replace('.csv', '_cleaned.csv')
    transform_file_to_prova(input_file, output_file)
    return output_file