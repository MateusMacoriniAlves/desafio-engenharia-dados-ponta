import pandas as pd
import requests
import datetime
import json

data_saved = datetime.datetime.now().strftime("%y-%m-%d_%H:%M:%S")
data_etl = datetime.datetime.now().strftime('%Y-%m-%d')

def extract_xlsx(filepath = "./files/xlsx/CEPEA-20250416134013.xlsx"):
    #Reads the CEPEA spreadsheet and returns a dataframe.
    return pd.read_excel(filepath, skiprows=3, names=["Data", "Valor"])

def extract_csv(filepath = "./files/csv/boi_gordo_base.csv"):
    #Reads the BOI_GORDO csv and returns a dataframe.
    return pd.read_csv(filepath)

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
    path_save_json = "./files/json/"
    path_save_csv = "./files/csv/"

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
    
api = extract_bcb(433, '01/01/2023', '31/05/2025')

def transform():
    teste = extract_xlsx()
    teste['Data'] = pd.to_datetime(teste['Data'], format="%m/%Y", errors='coerce')

    while teste['Data'].isna().any():
        teste['Data'] = teste['Data'].fillna(teste['Data'].shift(1)+pd.DateOffset(months=1))
    #teste['Data'] = teste['Data'].fillna(teste['Data'].shift(1)+pd.DateOffset(months=1))

    teste['Valor'] = teste['Valor'].ffill()

    merged = teste.merge(api, left_on='Data', right_on='data', how='left')
    merged = merged.drop(['data'], axis=1)
    merged.rename(columns={"valor": "IPCA"}, inplace=True)

    merged['IPCA_ACUMULADO'] = merged['IPCA'].cumsum()
    merged['Valor'] = merged['Valor'].str.replace(',', '.', regex=False)
    merged['Valor'] = pd.to_numeric(merged['Valor'])

    ipca_acum = merged.loc[merged['Data'] == '2025-03-01', 'IPCA_ACUMULADO'].values[0]

    merged['Valor_real'] = merged['Valor'] + (
        merged['Valor'] * ((ipca_acum - merged['IPCA_ACUMULADO']) / 100)
    )
    merged['Valor_real'] = merged['Valor_real'].round(2)
    boi = extract_csv()
    boi['dt_cmdty'] = pd.to_datetime(boi['dt_cmdty'])

    boi_novo = merged.merge(boi, left_on='Data', right_on='dt_cmdty', how="left")

    boi_novo['dt_cmdty'] = boi_novo['Data']
    boi_novo['cmdty_vl_rs_um_new'] = boi_novo['Valor_real']
    boi_novo['cmdty_var_mes_perc_new'] = (boi_novo['Valor_real'] - boi_novo['cmdty_vl_rs_um'])/ boi_novo['cmdty_vl_rs_um']

    return boi_novo


def load_parquet(boi_novo):
    df_final = pd.DataFrame({
        'dt_cmdty': boi_novo['dt_cmdty'],
        'nome_cmdty': 'Boi_Gordo',
        'tipo_cmdty': 'Indicador do Boi Gordo CEPEA/B3',
        'cmdty_um': '15 Kg/carcaça',
        'cmdty_vl_rs_um': boi_novo['cmdty_vl_rs_um_new'],
        'cmdty_var_mes_perc': boi_novo['cmdty_var_mes_perc_new'],
        'dt_elt': data_etl
    })
    df_final.to_parquet('./files/parquet/boi_gordo_saida.parquet', index=False)

if __name__ == "__main__":
    api = extract_bcb(433, '01/01/2023', '31/05/2025')
    boi_novo = transform()
    load_parquet(boi_novo)
    print("ETL finalizado com sucesso!")