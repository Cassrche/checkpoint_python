# python test_conversor.py
import pathlib

import conversor

EXEMPLOS = pathlib.Path(__file__).parent / "exemplos"


def test_todos_os_pares():
    for origem in conversor.FORMATOS:
        dados = (EXEMPLOS / f"dados.{origem}").read_bytes()
        base = conversor.ler(dados, origem)
        for destino in conversor.FORMATOS:
            convertido = conversor.converter(dados, origem, destino)
            volta = conversor.ler(convertido, destino)
            assert list(volta.columns) == list(base.columns), (origem, destino)
            assert len(volta) == len(base), (origem, destino)


if __name__ == "__main__":
    test_todos_os_pares()
    print("ok")
