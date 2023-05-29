import pdfplumber
import re
from flask import Flask, render_template, request
from tabulate import tabulate

app = Flask(__name__, template_folder='templates')

def converter_pdf_para_texto(caminho_arquivo_pdf):
    texto = ""
    with pdfplumber.open(caminho_arquivo_pdf) as pdf:
        for page in pdf.pages:
            texto += page.extract_text()
    return texto

def buscar_valores_debitos(texto_pdf, arquivo_nomes_debitos):
    with open(arquivo_nomes_debitos, "r", encoding="utf-8") as arquivo_nomes:
        nomes_debitos = arquivo_nomes.readlines()
    
    resultados = {}

    for linha in texto_pdf.splitlines():
        for nome_debito in nomes_debitos:
            nome_debito = nome_debito.strip()
            padrao_busca = r"\b{}\b".format(re.escape(nome_debito))
            match = re.search(padrao_busca, linha, re.IGNORECASE)
            if match:
                padrao_valor = r"(\d{1,3}(?:\.\d{3})*,\d{2})"
                resultado_valor = re.search(padrao_valor, linha)
                if resultado_valor:
                    valor = resultado_valor.group(0)
                    valor = valor.replace(".", "").replace(",", ".")
                    valor = float(valor)
                    if nome_debito in resultados:
                        resultados[nome_debito] += valor
                    else:
                        resultados[nome_debito] = valor

    resultados = {nome: round(valor, 2) for nome, valor in resultados.items()}

    return resultados

@app.route("/", methods=["GET", "POST"])
def extrair_debitos():
    if request.method == "POST":
        arquivo_pdf = request.files["arquivo_pdf"]
        nomes_debitos = request.files["nomes_debitos"]

        texto_pdf = converter_pdf_para_texto(arquivo_pdf)
        debitos = buscar_valores_debitos(texto_pdf, nomes_debitos)

        tabela = []
        for nome, valor in debitos.items():
            tabela.append([nome, valor])

        headers = ["Nome do Débito", "Valor"]
        resultado_table = tabulate(tabela, headers, tablefmt="html", colalign=("left", "right"))

        return render_template("templates/resultado.html", tabela=resultado_table)
    return render_template("templates/index.html")

if __name__ == "__main__":
    app.run()