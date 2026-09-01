import io

import pytesseract
from PIL import Image

IDIOMAS = "por+eng"


def imagem_para_texto(dados: bytes) -> str:
    """Extrai o texto de uma imagem usando o Tesseract."""
    imagem = Image.open(io.BytesIO(dados))
    return pytesseract.image_to_string(imagem, lang=IDIOMAS).strip()


def versao():
    """Levanta excecao se o binario do tesseract nao estiver instalado."""
    return pytesseract.get_tesseract_version()
