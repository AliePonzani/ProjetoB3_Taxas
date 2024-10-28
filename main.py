from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
from datetime import datetime

app = Flask(__name__)

# Função do tipo POST para enviar os dados do formulário para obter os dados de taxa
def post_form(slcTaxa_request, date, date1):
    try:
        url = 'https://www2.bmf.com.br/pages/portal/bmfbovespa/lumis/lum-taxas-referenciais-bmf-enUS.asp'

        # Configurações do formulário
        form_data = {
            "slcTaxa": slcTaxa_request,
            "Data": date,
            "Data1": date1,
            "IDIOMA": "2"
        }

        # Faz a requisição do tipo POST para o site externo
        response = requests.post(url, data=form_data)
        response.raise_for_status()  # Verifica se houve erro na requisição

        # Parseando o HTML da resposta
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extraindo o cabeçalho e o corpo da tabela
        header = [th.text.strip() for th in soup.find_all("th", {"class": "text-center"})]
        if len(header) > 2:
            header.pop(1)  # Ajuste do cabeçalho para tirar o th referente a taxa escolhida

        body = [td.text.strip() for td in soup.find_all("td")]

        # Organiza os dados da tabela em um formato de lista de dicionários
        table = []
        for i in range(0, len(body), len(header)):
            linha = {header[j]: body[i + j] for j in range(len(header)) if i + j < len(body)}
            table.append(linha)

        return table  # Retorna a tabela processada

    except requests.RequestException as e:
        # Captura e registra erros de requisição
        print(f"Erro na requisição: {str(e)}")
        return None
    
# Definindo a rota para a busca
@app.route('/slcTaxa')

def get_data():
    # Captura os parâmetros da requisição
    slcTaxa_request = request.args.get('slcTaxa')
    required_date = request.args.get('date')

    if not slcTaxa_request:
        return jsonify({"error": "Por favor, forneça o valor do parâmetro slcTaxa."}), 400

    if not required_date:
        return jsonify({"error": "Por favor, forneça uma data no formato mm/dd/aaaa."}), 400

    try:
        # Convertendo a data para os formatos necessários
        date = datetime.strptime(required_date, "%d/%m/%Y").strftime("%m/%d/%Y")
        date1 = datetime.strptime(required_date, "%d/%m/%Y").strftime("%Y%m%d")

        # Chama a função que faz a requisição do tipo POST
        table = post_form(slcTaxa_request, date, date1)

        if table is None:
            return jsonify({"error": "Erro ao obter dados da taxa."}), 500

        if not table:
            return jsonify({"error": "Nenhum dado encontrado para a data fornecida."}), 404

        # Retorna um Json
        return jsonify({"Required_date": required_date, "slcTaxa": slcTaxa_request, "Data": table})
    
    except Exception as e:
        return jsonify({"error": f"Erro inesperado: {str(e)}"}), 500

app.run()
