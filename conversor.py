import io
import json

import pandas as pd


def dict_para_json(dados):
    if not isinstance(dados, dict):
        raise TypeError("A entrada precisa ser um dict.")
    return json.dumps(dados, indent=4, ensure_ascii=False)


def dict_para_csv(dados):
    if not isinstance(dados, dict):
        raise TypeError("A entrada precisa ser um dict.")
    return pd.DataFrame(dados.items(), columns=["chave", "valor"]).to_csv(index=False)


def json_para_csv(texto):
    dados = json.loads(texto)
    if isinstance(dados, dict):
        dados = [dados]
    return pd.json_normalize(dados).to_csv(index=False)


def csv_para_json(texto):
    tabela = pd.read_csv(io.StringIO(texto))
    return json.dumps(tabela.to_dict("records"), indent=4, ensure_ascii=False)


def xlsx_para_csv(arquivo):
    return pd.read_excel(arquivo).to_csv(index=False)


def csv_para_xlsx(texto):
    saida = io.BytesIO()
    pd.read_csv(io.StringIO(texto)).to_excel(saida, index=False)
    return saida.getvalue()
