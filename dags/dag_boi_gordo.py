import pandas as pd
import requests
import datetime
import json

from airflow.decorators import dag, task

#These dates will be used to save the file names later.
data_saved = datetime.datetime.now().strftime("%y-%m-%d_%H:%M:%S")
data_etl = datetime.datetime.now().strftime('%Y-%m-%d')

@task
def extract_xlsx(filepath = "/opt/airflow/dags/files/xlsx/CEPEA-20250416134013.xlsx"):
    #Reads the CEPEA spreadsheet and returns a dataframe.
    return pd.read_excel(filepath, skiprows=3, names=["Data", "Valor"])

@task
def extract_csv(filepath = "/opt/airflow/dags/files/csv/boi_gordo_base.csv"):
    #Reads the BOI_GORDO csv and returns a dataframe.
    return pd.read_csv(filepath)

@task
def extract_bcb(code_bcb, date_init, date_final, save_csv=True):
    """
    This function retrieves values from the BCB API for extraction and analysis.
    Params:
    -----------
        code_bcb: This code references the BCB documentation for Time Series Management System lookup values.
        date_init: Initial data for searching in the API. The default data is DD/MM/YYYY.
        date_final: Final data for searching in the API. The default data is DD/MM/YYYY.
        save_csv: This parameter defines whether the API response will be saved in csv. Default is TRUE
    """

    #Set the url variable. This url is used to standardize the function parameters, it will receive what the user types when calling the function.
    url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{code_bcb}/dados?formato=json&dataInicial={date_init}&dataFinal={date_final}"

    #The path_save_json variable will be used to save the default path to save the file.
    #Depending on the execution method, it would be better to put the entire path, but in this example it will be saved in the project root.
    path_save_json = "/opt/airflow/dags/files/json/"
    path_save_csv = "/opt/airflow/dags/files/csv/"

    #makes the request with the requests library
    response = requests.get(url)

    #Check that the API response was 200 (success)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        df['data'] = pd.to_datetime(df['data'], dayfirst=True)
        df['valor'] = df['valor'].astype(float)

        #Save the API response json
        with open(f"{path_save_json}resposta_api_{data_saved}.json", 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        #Check if it will save the json
        if save_csv:
            df.to_csv(f'{path_save_csv}DATA_BCB_{data_saved}.csv', index=False, sep=';', encoding='utf-8')

        return df
    else:
        print(f"[ERRO] Código HTTP: {response.status_code}")
        print(f"[DETALHE] {response.text}")
        return None

@task
def transform(api_data, df_xlsx, df_csv):
    """
    This function performs the required transformations
    Params:
    -----------
        api_data: Receive the API file for processing
        df_xlsx: Receive the XLSX file for processing
        df_csv: Receive the CSV file for processing
    """
    #Transform the date field of the excel file to datetime
    df_xlsx['Data'] = pd.to_datetime(df_xlsx['Data'], format="%m/%Y", errors='coerce')

    #makes a loop to check if there is a month in the zero date field, takes the previous month and adds 1, the output is when there are no more blank cells
    while df_xlsx['Data'].isna().any():
        df_xlsx['Data'] = df_xlsx['Data'].fillna(df_xlsx['Data'].shift(1)+pd.DateOffset(months=1))

    #If there is a missing value in the value column, it is filled with the value from the previous month.
    df_xlsx['Valor'] = df_xlsx['Valor'].ffill()

    #Merged excel file with api data file
    merged = df_xlsx.merge(api_data, left_on='Data', right_on='data', how='left')

    #Remove the date column to avoid conflict later. This date comes from the API.
    merged = merged.drop(['data'], axis=1)
    merged.rename(columns={"valor": "IPCA"}, inplace=True)

    #Creates the column 'IPCA_ACUMULADO' with the .cumsum() method.
    merged['IPCA_ACUMULADO'] = merged['IPCA'].cumsum()

    #Change "," to "." and then convert the field to numeric.
    merged['Valor'] = merged['Valor'].str.replace(',', '.', regex=False)
    merged['Valor'] = pd.to_numeric(merged['Valor'])

    #Set the ipca_acum variable with the calculated accumulated value.
    ipca_acum = merged.loc[merged['Data'] == '2025-03-01', 'IPCA_ACUMULADO'].values[0]

    #Perform the calculation as described in the demand. After that, rounds the field to two decimal places.
    merged['Valor_real'] = merged['Valor'] + (
        merged['Valor'] * ((ipca_acum - merged['IPCA_ACUMULADO']) / 100)
    )
    merged['Valor_real'] = merged['Valor_real'].round(2)

    # Transform the dt_cmdty field of the CSV file to datetime
    df_csv['dt_cmdty'] = pd.to_datetime(df_csv['dt_cmdty'])

    #Merge to perform upsert.
    boi_novo = merged.merge(df_csv, left_on='Data', right_on='dt_cmdty', how="left")

    #The 'dt_cmdty' field will receive the value of the 'Data' field.
    boi_novo['dt_cmdty'] = boi_novo['Data']

    #The 'cmdty_vl_rs_um_new' field will receive the value of the 'Valor_real' field.
    boi_novo['cmdty_vl_rs_um_new'] = boi_novo['Valor_real']

    #The field 'cmdty_var_mes_perc_new' will receive the value from the formula below.
    boi_novo['cmdty_var_mes_perc_new'] = (boi_novo['Valor_real'] - boi_novo['cmdty_vl_rs_um'])/ boi_novo['cmdty_vl_rs_um']

    return boi_novo

@task
def load_parquet(boi_novo):

    #Constructs the structure of the output dataframe.
    df_final = pd.DataFrame({
        'dt_cmdty': boi_novo['dt_cmdty'],
        'nome_cmdty': 'Boi_Gordo',
        'tipo_cmdty': 'Indicador do Boi Gordo CEPEA/B3',
        'cmdty_um': '15 Kg/carcaça',
        'cmdty_vl_rs_um': boi_novo['cmdty_vl_rs_um_new'],
        'cmdty_var_mes_perc': boi_novo['cmdty_var_mes_perc_new'],
        'dt_elt': data_etl
    })
    #Saves the file in parquet.
    df_final.to_parquet('/opt/airflow/dags/files/parquet/boi_gordo_saida.parquet', index=False)

@dag(
    schedule=None,
    start_date=datetime.datetime(2025, 5, 19),
    catchup=False,
    tags=['boi_gordo']
)
def etl_boi_gordo():
    bcb_data = extract_bcb(433, '01/01/2023', '31/05/2025')
    df_xlsx = extract_xlsx()
    df_csv = extract_csv()
    transformed_data = transform(bcb_data, df_xlsx, df_csv)
    load_parquet(transformed_data)

etl_boi_gordo()