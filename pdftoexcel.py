import os
import argparse
# import pathlib
import camelot
import pandas as pd

parser = argparse.ArgumentParser(description = 'Convert the PDF file')
parser.add_argument('-i','--input', type = str, metavar= '', help='Enter here your input file path')

args = parser.parse_args()

def pdf_to_csv(filename):
	print_header(filename)

	data_df = detuct_table(filename)

	data_fixed = (data_df
		.pipe(remove_unwanted_rows)
		.pipe(clean_columns)
		.pipe(merge_rows)
		.pipe(change_dtype)
		)
	convert_to_excel(data_fixed, filename)

	print("Conpleted \nTHANK YOU")

def print_header(filename):
    print("|----------------------------------------|")
    print("|---------PDF to Excel Converter-----------|")
    print("|----------------------------------------|\n\n")
    print("Processing your PDF.................................\n\n")



def detuct_table(filename):
	stream_tables = camelot.read_pdf(filename, flavor='stream', pages='all')

	print(stream_tables.n,"Table found\n\n")
	panda_df = stream_tables[0].df
	return panda_df

def remove_unwanted_rows(dataframe):
	print("Removing Unwanted Headers\n\n")

	dataframe = dataframe[3:-1]
	dataframe = dataframe.reset_index(drop=True)
	return dataframe


def clean_columns(dataframe):
	print("Cleaning columns..............\n\n")

	dataframe.columns = dataframe.columns.astype(str)
	dataframe.columns = dataframe.iloc[0]
	dataframe = dataframe[1:]
	return dataframe

def merge_rows(dataframe):
	print("Merge Similar rows.......................\n\n")
	dataframe = (dataframe.groupby((dataframe['Balance'] != '').cumsum()).agg(dict(dict.fromkeys(dataframe,'first'), **{'Booking Text':', '.join})))
	return dataframe


def change_dtype(dataframe):
    dataframe['Booking Date'] = dataframe['Booking Date'].str.replace("\nE","")
    print("Converting date to YYYY/MM/DD\n\n")

    dataframe['Booking Date'] = pd.to_datetime(dataframe['Booking Date'], format='%d.%m.%Y', errors='coerce').dt.strftime('%Y/%m/%d')
    dataframe['Txn Date'] = pd.to_datetime(dataframe['Txn Date'], format='%d.%m.%Y', errors='coerce').dt.strftime('%Y/%m/%d')
    dataframe['Value Date'] = pd.to_datetime(dataframe['Value Date'], format='%d.%m.%Y', errors='coerce').dt.strftime('%Y/%m/%d')
    print("Converting money to ###.##\n\n")

    dataframe['Debit'] = dataframe['Debit'].str.replace(',','')
    dataframe['Credit'] = dataframe['Credit'].str.replace(',','')
    dataframe['Balance'] = dataframe['Balance'].str.replace(',','')
    
    return dataframe


# def get_path_of_source(filename):
#     p = pathlib.Path(filename)
#     return p

def convert_to_excel(dataframe, filename):
	print("Converting to Excel............\n\n")
	outputfile = filename.split('.')[0]
	dataframe.to_excel(outputfile+".xlsx", index=False)


if __name__ == '__main__':    
    pdf_to_csv(args.input)