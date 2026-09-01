# streamlit run app.py

import ast

import streamlit as st

import conversor

OPCOES = {
    "dict -> JSON": ("dict", conversor.dict_para_json, "saida.json"),
    "dict -> CSV": ("dict", conversor.dict_para_csv, "saida.csv"),
    "JSON -> CSV": ("json", conversor.json_para_csv, "saida.csv"),
    "CSV -> JSON": ("csv", conversor.csv_para_json, "saida.json"),
    "XLSX -> CSV": ("xlsx", conversor.xlsx_para_csv, "saida.csv"),
    "CSV -> XLSX": ("csv", conversor.csv_para_xlsx, "saida.xlsx"),
}

st.title("Conversor de Arquivos")

opcao = st.sidebar.radio("Conversao:", list(OPCOES))
entrada, converter, nome_saida = OPCOES[opcao]

if entrada == "dict":
    dado = st.text_area("Digite o dict:", '{"nome": "Ana", "idade": 20}')
else:
    dado = st.file_uploader(f"Envie um arquivo .{entrada}", type=entrada)

if dado and st.button("Converter"):
    try:
        if entrada == "dict":
            dado = ast.literal_eval(dado)
        elif entrada != "xlsx":
            dado = dado.read().decode("utf-8")

        saida = converter(dado)

        if isinstance(saida, str):
            st.code(saida)
        else:
            st.success("Planilha gerada.")
        st.download_button("Baixar", saida, nome_saida)
    except Exception as erro:
        st.error(f"Deu erro: {erro}")
