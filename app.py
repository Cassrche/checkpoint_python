# streamlit run app.py

import socket

import qrcode
import streamlit as st

import conversor

try:
    import ocr

    ocr.versao()
    OCR_ERRO = None
except Exception as erro:  # claude CLI ausente ou sem autenticacao
    ocr, OCR_ERRO = None, erro

MIMES = {
    "csv": "text/csv",
    "json": "application/json",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}

st.set_page_config(page_title="Conversor de Arquivos", page_icon=":arrows_counterclockwise:")

def url_da_rede():
    """Endereco da maquina na rede local, para abrir pelo celular."""
    conexao = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        conexao.connect(("8.8.8.8", 80))  # nao envia nada, so resolve a rota de saida
        ip = conexao.getsockname()[0]
    except OSError:
        return None  # sem rede
    finally:
        conexao.close()
    return f"http://{ip}:{st.get_option('server.port')}"


@st.cache_resource  # imprime uma vez por servidor, nao a cada rerun
def mostrar_qrcode(endereco):
    qr = qrcode.QRCode(border=1)
    qr.add_data(endereco)
    print(f"\n  Aponte a camera do celular:  {endereco}")
    qr.print_ascii(invert=True)
    return endereco


_endereco = url_da_rede()
if _endereco:
    mostrar_qrcode(_endereco)


st.title("Conversor de Arquivos")
st.caption("Arraste um arquivo para a caixa abaixo, ou cole o conteudo na aba ao lado.")

aba_arquivo, aba_colar, aba_imagem = st.tabs(
    ["Arrastar arquivo", "Colar conteudo", "Foto para Markdown"]
)

dados = nome = origem = None

with aba_arquivo:
    enviado = st.file_uploader(
        "Solte o arquivo aqui",
        type=list(conversor.FORMATOS),
        label_visibility="collapsed",
    )
    if enviado:
        dados = enviado.getvalue()
        nome = enviado.name.rsplit(".", 1)[0]
        origem = enviado.name.rsplit(".", 1)[-1].lower()

with aba_colar:
    with st.form("form_colar"):
        texto = st.text_area(
            "Cole aqui o conteudo (CSV ou JSON)",
            height=180,
            placeholder='{"nome": "Ana", "idade": 20}',
        )
        st.form_submit_button("Converter", type="primary")
    if texto.strip() and not dados:
        dados = texto.encode("utf-8")
        nome = "colado"
        origem = "json" if texto.lstrip()[0] in "{[" else "csv"

with aba_imagem:
    if OCR_ERRO:
        st.warning(f"Transcricao indisponivel: {OCR_ERRO}")
        st.code("npm install -g @anthropic-ai/claude-code   # instala o CLI\n"
                "claude                                     # autentica uma vez")
    else:
        foto = st.file_uploader("Envie uma imagem", type=ocr.FORMATOS)

        # a webcam so existe em https ou localhost; pelo IP da rede o navegador nem pergunta
        host = st.context.headers.get("host", "")
        if host.startswith(("localhost", "127.0.0.1")):
            if not foto:
                foto = st.camera_input("Ou tire uma foto agora")
        else:
            st.caption("No celular, use o botao acima e escolha Tirar Foto ou Fototeca.")

        if foto:
            with st.spinner("Transcrevendo..."):
                try:
                    texto_ocr = ocr.imagem_para_markdown(foto.getvalue())
                except Exception as erro:
                    st.error(f"Falhou: {erro}")
                    texto_ocr = ""

            if not texto_ocr:
                st.error("Nao encontrei texto nessa imagem.")
            else:
                texto_ocr = st.text_area(
                    "Markdown gerado (edite antes de baixar)", texto_ocr, height=300
                )
                st.download_button(
                    "Baixar .md",
                    texto_ocr.encode("utf-8"),
                    file_name="transcricao.md",
                    mime="text/markdown",
                    type="primary",
                )

if not dados:
    st.stop()

try:
    tabela = conversor.ler(dados, origem)
except Exception as erro:
    st.error(f"Nao consegui ler o arquivo como .{origem}: {erro}")
    st.stop()

st.success(f"Lido como **{origem.upper()}** - {len(tabela)} linhas, {len(tabela.columns)} colunas.")
st.dataframe(tabela.head(20), use_container_width=True)

destinos = [f for f in conversor.FORMATOS if f != origem]
destino = st.selectbox("Converter para:", destinos, format_func=str.upper)

try:
    saida = conversor.escrever(tabela, destino)
except Exception as erro:
    st.error(f"Erro ao gerar o .{destino}: {erro}")
    st.stop()

st.download_button(
    f"Baixar {nome}.{destino}",
    saida,
    file_name=f"{nome}.{destino}",
    mime=MIMES[destino],
    type="primary",
)
