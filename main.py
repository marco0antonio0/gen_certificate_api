from flask import Flask, request, send_file, jsonify
from flasgger import Swagger
from PIL import Image, ImageDraw, ImageFont
import os
import uuid
import base64
import io
import zipfile
from flask_cors import CORS
from rembg import remove


app = Flask(__name__)
CORS(app)

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Gerador de Certificados",
        "description": "API para gerar certificados personalizados com nome, fundo, assinatura e textos opcionais.",
        "version": "1.0.0"
    },
    "basePath": "/",
    "schemes": ["http", "https"]
}

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec_1",
            "route": "/apispec_1.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}

Swagger(app, template=swagger_template, config=swagger_config)

ESCALA = 1
PASTA_FUNDOS = "./images/fundo"
CAMINHO_FONTE_NOME = "./fonts/GreatVibes-Regular.ttf"
CAMINHO_FONTE_TEXTO = "./fonts/Merriweather-VariableFont_opsz,wdth,wght.ttf"

TAM_NOME = 80 * ESCALA
TAM_TEXTO = 26 * ESCALA
TAM_SUBTITULO = 22 * ESCALA
TAM_LINHA = 4 * ESCALA
LARGURA_TEXTO = 700 * ESCALA
LARGURA_ASSINATURA = 300 * ESCALA
MARGEM_TEXTO_ASSINATURA = 80 * ESCALA

COR_NOME = (164, 120, 58)
COR_TEXTO = (0, 0, 0)


def remover_fundo(caminho_entrada, caminho_saida):
    try:
        with open(caminho_entrada, 'rb') as img_file:
            imagem_bytes = img_file.read()
            resultado = remove(imagem_bytes)

        imagem_sem_fundo = Image.open(io.BytesIO(resultado)).convert("RGBA")
        imagem_sem_fundo.save(caminho_saida)
        print(f"✅ Fundo removido com sucesso: {caminho_saida}")
    except Exception as e:
        print(f"❌ Erro ao remover fundo: {e}")


def gerar_certificado(nome, fundo="modelo_0", texto_personalizado=None, orgao_emissor=None, assinatura_b64=None):
    caminho_fundo = os.path.join(PASTA_FUNDOS, fundo+".png")
    if not os.path.exists(caminho_fundo):
        raise FileNotFoundError(f"Fundo '{fundo}' não encontrado.")

    img = Image.open(caminho_fundo).convert("RGBA")
    draw = ImageDraw.Draw(img)
    largura_img, altura_img = img.size
    y_cursor = 100 * ESCALA

    fonte_nome = ImageFont.truetype(CAMINHO_FONTE_NOME, TAM_NOME)
    fonte_texto = ImageFont.truetype(CAMINHO_FONTE_TEXTO, TAM_TEXTO)
    fonte_subtitulo = ImageFont.truetype(CAMINHO_FONTE_TEXTO, TAM_SUBTITULO)
    fonte_titulo = ImageFont.truetype(CAMINHO_FONTE_TEXTO, 100 * ESCALA)

    TEXTO_TITULO = "Este certificado atesta que"
    TEXTO_PADRAO = texto_personalizado or (
        "concluiu com êxito o curso de Administração oferecido por Borcelle, "
        "no período compreendido entre 02/08/2019 e 07/05/2023..."
    )
    ORGAO = orgao_emissor or "Instituto de Formação Borcelle"

    def margem_y(pixels=20):
        nonlocal y_cursor
        y_cursor += pixels * ESCALA

    def texto(conteudo, fonte, cor=COR_TEXTO):
        nonlocal y_cursor
        bbox = draw.textbbox((0, 0), conteudo, font=fonte)
        largura = bbox[2] - bbox[0]
        x = (largura_img - largura) // 2
        draw.text((x, y_cursor), conteudo, font=fonte, fill=cor)
        y_cursor += fonte.size + 10 * ESCALA

    def linha(proporcao_inicio=0.25, proporcao_fim=0.75, cor=COR_TEXTO):
        nonlocal y_cursor
        x1 = largura_img * proporcao_inicio
        x2 = largura_img * proporcao_fim
        draw.line([(x1, y_cursor), (x2, y_cursor)], fill=cor, width=TAM_LINHA)
        y_cursor += TAM_LINHA + 10 * ESCALA

    def quebrar_texto(texto_base, fonte):
        palavras = texto_base.split()
        linhas = []
        linha_atual = ""
        for palavra in palavras:
            teste = linha_atual + " " + palavra if linha_atual else palavra
            largura = draw.textbbox((0, 0), teste, font=fonte)[2]
            if largura <= LARGURA_TEXTO:
                linha_atual = teste
            else:
                linhas.append(linha_atual)
                linha_atual = palavra
        if linha_atual:
            linhas.append(linha_atual)
        return linhas

    def bloco_texto(texto_base, fonte=None, cor=COR_TEXTO):
        linhas = quebrar_texto(texto_base, fonte or fonte_texto)
        for linha_txt in linhas:
            texto(linha_txt, fonte or fonte_texto, cor)

    def assinatura():
        nonlocal y_cursor
        if not assinatura_b64:
            return

        try:
            if assinatura_b64.startswith("data:image"):
                assinatura_base64_clean = assinatura_b64.split(",")[1]
            else:
                assinatura_base64_clean = assinatura_b64

            image_data = base64.b64decode(assinatura_base64_clean)
            imagem_sem_fundo = remove(image_data)
            assinatura_img = Image.open(io.BytesIO(imagem_sem_fundo)).convert("RGBA")
        except Exception as e:
            raise ValueError(f"Assinatura inválida: {str(e)}")

        largura_ass, altura_ass = assinatura_img.size
        nova_altura = int(altura_ass * (LARGURA_ASSINATURA / largura_ass))
        assinatura_img = assinatura_img.resize((LARGURA_ASSINATURA, nova_altura))
        x = (largura_img - LARGURA_ASSINATURA) // 2
        img.paste(assinatura_img, (x, y_cursor), assinatura_img)
        y_cursor += nova_altura + 10 * ESCALA

    margem_y(200)
    texto("CERTIFICADO", fonte_titulo, cor=COR_NOME)
    margem_y(90)
    texto(TEXTO_TITULO, fonte_texto)
    margem_y(20)
    texto(nome, fonte_nome, COR_NOME)
    linha()
    margem_y(30)
    bloco_texto(TEXTO_PADRAO)
    margem_y(MARGEM_TEXTO_ASSINATURA // ESCALA)
    assinatura()
    linha(proporcao_inicio=0.35, proporcao_fim=0.65)
    texto(ORGAO, fonte_subtitulo)

    output = io.BytesIO()
    img.save(output, format="PNG")
    output.seek(0)
    return output

@app.route("/gerar_certificado", methods=["POST"])
def gerar_certificado_api():
    """
    Gera um certificado personalizado.
    ---
    consumes:
      - multipart/form-data
    parameters:
      - name: nome
        in: formData
        type: string
        required: true
        description: "Nome para o certificado"
      - name: tipo_certificado
        in: formData
        type: string
        required: false
        description: "Nome do arquivo de fundo (ex: modelo_0)"
      - name: texto_personalizado
        in: formData
        type: string
        required: false
        description: "Texto do certificado (substitui o padrão)"
      - name: orgao_emissor
        in: formData
        type: string
        required: false
        description: "Nome do órgão emissor"
      - name: assinatura_b64
        in: formData
        type: string
        required: false
        description: "Imagem da assinatura em base64 (formato PNG)"
    responses:
      200:
        description: Certificado gerado com sucesso
        content:
          image/png:
            schema:
              type: string
              format: binary
    """
    nome = request.form.get("nome")
    tipo = request.form.get("tipo_certificado", "modelo_1")
    texto = request.form.get("texto_personalizado")
    orgao = request.form.get("orgao_emissor")
    assinatura = request.form.get("assinatura_b64")

    if not nome:
        return jsonify({"erro": "Parâmetro 'nome' é obrigatório"}), 400

    try:
        output = gerar_certificado(nome, tipo, texto, orgao, assinatura)
        return send_file(output, mimetype='image/png', as_attachment=True, download_name=f"certificado_{nome}.png")
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route("/tipos_certificados", methods=["GET"])
def listar_fundos():
    """
    Lista os fundos de certificado disponíveis (sem extensão).
    ---
    responses:
      200:
        description: Lista de arquivos de fundo
        schema:
          type: array
          items:
            type: string
    """
    arquivos = [
        os.path.splitext(f)[0] for f in os.listdir(PASTA_FUNDOS)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]
    return jsonify(arquivos)


@app.route("/gerar_certificados_zip", methods=["POST"])
def gerar_certificados_zip():
    """
    Gera vários certificados e retorna um arquivo zip.
    ---
    consumes:
      - multipart/form-data
    parameters:
      - name: nomes
        in: formData
        type: string
        required: true
        description: "Lista de nomes separados por vírgula"
      - name: tipo_certificado
        in: formData
        type: string
        required: false
        description: "Nome do fundo (ex: modelo_1)"
      - name: texto_personalizado
        in: formData
        type: string
        required: false
        description: "Texto opcional personalizado"
      - name: orgao_emissor
        in: formData
        type: string
        required: false
        description: "Nome do órgão emissor"
      - name: assinatura_b64
        in: formData
        type: string
        required: false
        description: "Imagem da assinatura em base64 (formato PNG)"
    responses:
      200:
        description: Arquivo ZIP com certificados
        content:
          application/zip:
            schema:
              type: string
              format: binary
    """
    nomes_str = request.form.get("nomes", "")
    tipo = request.form.get("tipo_certificado", "modelo_1")
    texto = request.form.get("texto_personalizado")
    orgao = request.form.get("orgao_emissor")
    assinatura = request.form.get("assinatura_b64")

    nomes = [n.strip() for n in nomes_str.split(",") if n.strip()]
    if not nomes:
        return jsonify({"erro": "Informe ao menos um nome no parâmetro 'nomes'"}), 400

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for nome in nomes:
            try:
                certificado = gerar_certificado(nome, tipo, texto, orgao, assinatura)
                zip_file.writestr(f"certificado_{nome}.png", certificado.read())
            except Exception as e:
                return jsonify({"erro": f"Erro ao gerar certificado para '{nome}': {str(e)}"}), 500

    zip_buffer.seek(0)
    return send_file(
        zip_buffer,
        mimetype="application/zip",
        as_attachment=True,
        download_name="certificados.zip"
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=False, port=3000)
