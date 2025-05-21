# Desafio Engenharia de Dados - Ponta Agro

Este projeto consiste em um pipeline de ETL desenvolvido para o desafio técnico da **Ponta Agro**, utilizando **Apache Airflow + Docker Compose**, com arquivos locais e integração com API externa para realizar um processo ETL completo.

---

## ✅ Objetivo

Realizar um um pipeline de ETL com as seguintes fontes de dados:

- Um arquivo `.xlsx` com dados de preço do boi gordo (CEPEA)
- Uma API do Banco Central para obter o IPCA

### Etapas do processo:

1. Extração (arquivos e API)
2. Limpeza e imputação de dados
3. Enriquecimento com IPCA
4. Cálculo de valor corrigido (valor real) e variação percentual
5. Upsert no CSV final
6. Carga final em formato Parquet

---

## 📦 Tecnologias e bibliotecas
- Apache Airflow
- pandas
- openpyxl
- requests
- pyarrow
- Docker + Docker Compose

---

## 📂 Estrutura de diretórios
```
.
├── dags/             # DAGs do Airflow
│   └── files/        # Scripts Python, funções auxiliares, etc.
├── files/            # Arquivos de entrada para processamento
│   ├── csv/          # Contém arquivos .csv
│   ├── json/         # Contém arquivos .json
│   ├── parquet/      # Contém arquivos .parquet
│   └── xlsx/         # Contém arquivos .xlsx
├── config/           # Configurações extras do projeto
├── plugins/          # Plugins personalizados do Airflow
├── logs/             # Logs das execuções
├── docker-compose.yml
├── .gitignore
└── README.md
```
---

## 🚀 Como executar

### Pré-requisitos

- Docker + Docker Compose
- Git

### Passos
- Clone o repositório: ```git clone https://github.com/MateusMacoriniAlves/desafio-engenharia-dados-ponta.git```
- Construa os containers: ```docker compose build```
- Suba o ambiente: ```docker compose up``` (Pode levar alguns segundos)
- Após subir o container, entre em: http://localhost:8080
- Usuário: ```airflow```
- Senha: ```airflow```

### Possíveis erros
- Pode acontecer alguns erros com o WSL, em testes foi preciso executar esse comando ```mkdir -p ./dags ./logs ./plugins ./config                                                                                                                                                   ──(Wed,May21)─┘
echo -e "AIRFLOW_UID=$(id -u)" > .env``` antes do comando  ```docker compose up```
- Outro erro pode ser na configuração do arquivo dockerfile. Na documentação oficial tem um modelo, que foi utilizado nesse projeto. Porém pode ser necessário alterar o conteúdo para ```FROM apache/airflow:3.0.1

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt ```

## 🧪 Testes e execução
- Verifique no painel se a DAG ```etl_boi_gordo``` existe.
- Execute a DAG manualmente para testar seu funcionamento

## 🧹 Parar e limpar o ambiente
- ```docker-compose down```
- ```docker-compose down --volumes --rmi all```

## 📌 Observações
- Este projeto foi desenvolvido em Ubuntu 24.04 com Python 3.11.9 dentro dos containers.
- Um arquivo chamado api.py foi incluído na raiz do projeto para permitir testes fora do Airflow, caso desejado.
- Os diretórios como logs/, __pycache__/ e outros arquivos temporários estão devidamente ignorados no .gitignore.

## 👨‍💻 Autor
- Mateus Macorini Alves
- Linkedin: https://www.linkedin.com/in/mateus-macorini-alves-9398761a9/
- email: mmatmt1@gmail.com