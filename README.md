# Desafio Engenharia de Dados - Ponta Agro com Apache Airflow + Python (Pandas)

Este projeto consiste em um pipeline de ETL para o desafio de Engenharia de Dados da Ponta Agro, utilizando **Airflow + Docker Compose**, arquivos locais e API externa para realizar um processo ETL completo.

---

## ✅ Objetivo

Realizar um ETL a partir de:

- Um arquivo `.xlsx` com dados de preço do boi gordo (CEPEA)
- Uma API do Banco Central para obter o IPCA

Com os seguintes passos:

1. Extração (arquivos e API)
2. Limpeza e imputação de dados
3. Enriquecimento com IPCA
4. Cálculo de valor corrigido (valor real) e variação percentual
5. Upsert no CSV final
6. Carga final em formato Parquet

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
├── logs/             # Gerado automaticamente pelo Airflow (ignorado no Git)
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

1. Clone o repositório:
2. git clone https://github.com/MateusMacoriniAlves/desafio-engenharia-dados-ponta.git
3. docker compose build
4. docker compose up (Pode levar alguns segundos)
5. Após subir o container, entre em: http://localhost:8080
- Usuário: airflow
- Senha: airflow

## 🧪 Testes e execução
- Verifique no painel se a DAG (etl_boi_gordo) existe.
- Execute a DAG manualmente para testar seu funcionamento

## 🧹 Parar e limpar o ambiente
- docker-compose down
- docker-compose down --volumes --rmi all

## 📌 Observações
- Este projeto foi desenvolvido em Ubuntu 24.04 com Python 3.11.9 dentro dos containers.
- Caso queira testar localmente, existe um arquivo chamado "api.py" na raiz que executa o código fora do airflow
  - Esse arquivo foi colocado aí para testes e futuras execuções, caso o usuário queira executar fora do aiflow.
- Alguns diretório são criados automaticamente. Eles estão ignorados pelo .gitignore

## 👨‍💻 Autor
- Mateus Macorini Alves
- Linkedin: https://www.linkedin.com/in/mateus-macorini-alves-9398761a9/
- email: mmatmt1@gmail.com