import io
import json

import pandas as pd

FORMATOS = ("csv", "json", "xlsx")


def _ler_json(dados):
    obj = json.loads(dados)
    return pd.json_normalize(obj if isinstance(obj, list) else [obj])


def _escrever_xlsx(tabela):
    saida = io.BytesIO()
    tabela.to_excel(saida, index=False)
    return saida.getvalue()


LEITORES = {
    "csv": lambda dados: pd.read_csv(io.BytesIO(dados)),
    "json": _ler_json,
    "xlsx": lambda dados: pd.read_excel(io.BytesIO(dados)),
}

ESCRITORES = {
    "csv": lambda tabela: tabela.to_csv(index=False).encode("utf-8"),
    "json": lambda tabela: json.dumps(
        tabela.to_dict("records"), indent=4, ensure_ascii=False, default=str
    ).encode("utf-8"),
    "xlsx": _escrever_xlsx,
}


def ler(dados: bytes, origem: str) -> pd.DataFrame:
    """Le os bytes de um arquivo no formato de origem e devolve uma tabela."""
    if origem not in LEITORES:
        raise ValueError(f"Formato nao suportado: {origem}")
    return LEITORES[origem](dados)


def escrever(tabela: pd.DataFrame, destino: str) -> bytes:
    """Serializa a tabela no formato de destino."""
    if destino not in ESCRITORES:
        raise ValueError(f"Formato nao suportado: {destino}")
    return ESCRITORES[destino](tabela)


def converter(dados: bytes, origem: str, destino: str) -> bytes:
    return escrever(ler(dados, origem), destino)
