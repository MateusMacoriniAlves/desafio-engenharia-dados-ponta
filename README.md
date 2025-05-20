# Desafio Engenharia de Dados - Ponta Agro

Este projeto é uma solução para o desafio de Engenharia de Dados da Ponta Agro, utilizando **Airflow + Docker Compose**, arquivos locais e API externa para realizar um processo ETL completo.

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

## 📂 Estrutura

