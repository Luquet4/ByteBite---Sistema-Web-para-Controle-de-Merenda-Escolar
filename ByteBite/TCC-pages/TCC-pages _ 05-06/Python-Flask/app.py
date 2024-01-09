from flask import Flask, render_template, request
import csv
from datetime import datetime
import pandas as pd
import os

app = Flask(__name__)

current_date_time = datetime.now()
planilha_principal = "dataset/dataset.csv"
planilha_diaria = f"dataset/{current_date_time.strftime('%Y%m%d')}-dataset.csv"
dataset_dict = {}

def prepare_dataset():
    # ler csv em um dicionário
    cont_line = 0
    if os.path.exists(planilha_diaria):
        with open(planilha_diaria, encoding='utf8') as planilha:
            csv_reader = csv.reader(planilha)
            next(csv_reader)  # pular a primeira linha por ser o cabeçalho
            for line in csv_reader:
                if len(line) >= 11:
                    ra = line[10]
                    nome = line[4]
                    campus = line[0]
                    curso = line[3]
                    situacao = line[5]
                    email_inst = line[7]
                    dataset_dict[ra] = {
                        'Nome': nome,
                        'Campus': campus,
                        'Curso': curso,
                        'Situação': situacao,
                        'E-mail Inst.': email_inst,
                        'Data': [],
                        'Tentativas': []
                    }
    else:
        with open(planilha_principal, encoding='utf8') as planilha:
            csv_reader = csv.reader(planilha)
            next(csv_reader)  # pular a primeira linha por ser o cabeçalho
            for line in csv_reader:
                if len(line) >= 11:
                    ra = line[10]
                    nome = line[4]
                    campus = line[0]
                    curso = line[3]
                    situacao = line[5]
                    email_inst = line[7]
                    dataset_dict[ra] = {
                        'Nome': nome,
                        'Campus': campus,
                        'Curso': curso,
                        'Situação': situacao,
                        'E-mail Inst.': email_inst,
                        'Data': [],
                        'Tentativas': []
                    }

        update_dataset(dataset_dict)

def update_dataset(dataset_dict):
    dict = {
        'RA': [],
        'Nome': [],
        'Campus': [],
        'Curso': [],
        'Situação': [],
        'E-mail Inst.': [],
        'Data': [],
        'Tentativas': []
    }

    for ra, dados in dataset_dict.items():
        dict['RA'].append(ra)
        dict['Nome'].append(dados['Nome'])
        dict['Campus'].append(dados['Campus'])
        dict['Curso'].append(dados['Curso'])
        dict['Situação'].append(dados['Situação'])
        dict['E-mail Inst.'].append(dados['E-mail Inst.'])
        dict['Data'].append(", ".join(dados['Data']))
        dict['Tentativas'].append(", ".join(dados['Tentativas'])) 

    df = pd.DataFrame(dict)
    df.to_csv(planilha_diaria, index=False)

@app.route('/')
def index_start_page():
    prepare_dataset()
    return render_template('index.html')

@app.route('/start')
def start_page():
    prepare_dataset()
    return render_template('index.html')

@app.route('/check', methods=["GET","POST"])
def check_access():
    global current_date_time
    if request.method == 'GET':
        return render_template('access.html')
    else:
        if request.method == 'POST':
            ra_code = request.form['ra']

            # verificar se existe o RA no dataset

            if ra_code not in dataset_dict:
                return render_template('user.html')

            # caso o RA esteja cadastrado no dataset

            dados_aluno = dataset_dict[ra_code]
            nome_aluno = dados_aluno['Nome']
            count_access = len(dados_aluno['Data'])

            # verificar se já teve registro de retirada de merenda

            if count_access == 0:
                current_date_time = datetime.now()
                dados_aluno['Data'].append(current_date_time.strftime(' %d/%m/%Y %H:%M:%S '))
                update_dataset(dataset_dict)
                return render_template('permitido.html')
            else:

                # Pega a data e hora atual para a tentativa

                current_date_time = datetime.now()  
                tentativas = dados_aluno['Tentativas']

                 # Coloca a data e hora atual como uma nova lista de tentativa

                tentativas.append(current_date_time.strftime(' %d/%m/%Y %H:%M:%S ')) 
                update_dataset(dataset_dict)
                return render_template('negado.html')

if __name__ == '__main__':
    prepare_dataset()
    app.run(debug=True)
