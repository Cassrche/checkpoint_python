import io
import os
import subprocess
import tempfile

import pillow_heif
from PIL import Image, ImageOps

pillow_heif.register_heif_opener()  # HEIC/HEIF do iPhone; AVIF ja e nativo no Pillow

FORMATOS = ["png", "jpg", "jpeg", "webp", "heic", "heif", "avif", "gif", "bmp", "tiff"]
LADO_MAX = 2000  # o limite de tamanho por imagem da API fica em ~5 MB

MODELO = "haiku"
TIMEOUT = 180

PROMPT = """Transcreva para Markdown o texto da imagem {caminho}.

Regras:
- Ignore elementos de interface: abas, numeros de linha, barras de ferramentas, menus, cursor.
- Transcreva apenas o conteudo escrito.
- Use # e ## para titulos conforme a hierarquia visual (tamanho e posicao). Se nao houver hierarquia clara, use # na primeira linha e paragrafos no resto.
- Preserve acentuacao, listas e tabelas.
- Responda SOMENTE com o Markdown, sem comentarios e sem cercas de codigo."""


def normalizar(dados: bytes) -> bytes:
    """Converte qualquer formato suportado para JPEG, ja rotacionado pelo EXIF."""
    imagem = ImageOps.exif_transpose(Image.open(io.BytesIO(dados)))
    imagem.thumbnail((LADO_MAX, LADO_MAX))
    saida = io.BytesIO()
    imagem.convert("RGB").save(saida, "JPEG", quality=90)
    return saida.getvalue()


def imagem_para_markdown(dados: bytes) -> str:
    """Transcreve a imagem para Markdown usando o Claude CLI local."""
    # roda fora do projeto: senao o CLI le o repositorio e comenta o codigo em vez de transcrever
    with tempfile.TemporaryDirectory() as pasta:
        caminho = os.path.join(pasta, "imagem.jpg")
        with open(caminho, "wb") as arquivo:
            arquivo.write(normalizar(dados))
        processo = subprocess.run(
            ["claude", "-p", PROMPT.format(caminho=caminho),
             "--model", MODELO, "--allowedTools", "Read"],
            capture_output=True, text=True, timeout=TIMEOUT, cwd=pasta,
        )

    if processo.returncode:
        raise RuntimeError(processo.stderr.strip() or "claude CLI falhou")
    return processo.stdout.strip()


def versao():
    """Levanta excecao se o Claude CLI nao estiver instalado."""
    return subprocess.run(
        ["claude", "--version"], capture_output=True, text=True, check=True
    ).stdout.strip()
