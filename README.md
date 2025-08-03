# 🏆 gen_certificate

API Flask para gerar certificados personalizados com nome, texto, fundo, assinatura e exportação em lote via arquivo `.zip`.

> Repositório: [github.com/marco0antonio0/gen_certificate](https://github.com/marco0antonio0/gen_certificate)

---

## 🚀 Funcionalidades

- 🎓 Geração de certificado com nome centralizado
- 🖼️ Suporte a múltiplos modelos de fundo
- 📝 Texto personalizado e nome do órgão emissor
- ✍️ Inclusão de assinatura em PNG (base64)
- 📦 Exportação em lote para `.zip`
- 📚 Documentação Swagger interativa via Flasgger

---

## ⚙️ Instalação

```bash
git clone https://github.com/marco0antonio0/gen_certificate.git
cd gen_certificate
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## ▶️ Execução Local

```bash
python app.py
```

Acesse localmente via:
```
http://localhost:5000/apidocs/
```

---

## 🌐 Swagger Público

A documentação da API está disponível em:

🔗 [https://api.certificado.opengena.com](https://api.certificado.opengena.com)

---

## 📂 Estrutura

```
.
├── app.py                      # Código principal da API
├── fonts/                      # Fontes tipográficas (nome e texto)
├── images/
│   └── fundo/                  # Imagens de fundo dos certificados
├── requirements.txt            # Dependências
└── README.md                   # Este arquivo
```

---

## 🔌 Endpoints

### `POST /gerar_certificado`
Gera um único certificado.

**Parâmetros:**
- `nome` (obrigatório)
- `tipo_certificado` (opcional)
- `texto_personalizado` (opcional)
- `orgao_emissor` (opcional)
- `assinatura_b64` (opcional, base64 de imagem PNG)

**Retorno:** Imagem `.png`.

---

### `POST /gerar_certificados_zip`
Gera múltiplos certificados e retorna `.zip`.

**Parâmetros:**
- `nomes` (obrigatório, separados por vírgula)
- Demais campos iguais ao anterior

**Retorno:** Arquivo `.zip`.

---

### `GET /tipos_certificados`
Retorna os arquivos disponíveis como fundo.

---

## 🖼️ Formato da Assinatura Base64

Exemplo válido:

```
data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...
```

Ou apenas a string após a vírgula.

---

## 📦 Tecnologias

- Python 3.10+
- Flask
- Pillow (PIL)
- Flasgger (Swagger UI)

---

## 🧑‍💻 Autor

**Marco Antonio**  
[github.com/marco0antonio0](https://github.com/marco0antonio0)

---

## 📝 Licença

Código aberto para uso, modificação e melhoria. Contribuições são bem-vindas!