from flask import Flask, render_template, request, redirect
import csv
from datetime import datetime
import time
import pandas as pd
import os
import traceback


app = Flask(__name__)
current_date_time = datetime.now()
planilha_principal = "dataset/dataset.csv"
planilha_diaria = f"dataset/{current_date_time.strftime('%Y%m%d')}-dados.csv"
planilha_backup = f"dataset/{current_date_time.strftime('%Y%m%d')}-backup.csv"
csv2 = f"dataset/{current_date_time.strftime('%Y%m%d')}-dados - copia.csv"
csv_combinado = f"dataset/{current_date_time.strftime('%Y%m%d')}-combinado.csv"
dataset_dict = {}

cont_alunos = 0
cont_servidores = 0
cont_total = 0

def prepare_dataset():
    global current_date_time, dataset_dict
    # ler csv em um dicionário
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
                    entrada = line[8]
                    periodo = line[9]
                    email_inst = line[7]
                    dataset_dict[ra] = {
                        'Nome': nome,
                        'Campus': campus,
                        'Curso': curso,
                        'Situação': situacao,
                        'Entrada': entrada,
                        'Periodo': periodo,
                        'E-mail Inst.': email_inst,
                        'Data Retirada': [],
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
                    entrada = line[8]
                    periodo = line[9]
                    email_inst = line[7]
                    dataset_dict[ra] = {
                        'Nome': nome,
                        'Campus': campus,
                        'Curso': curso,
                        'Situação': situacao,
                        'Entrada': entrada,
                        'Periodo': periodo,
                        'E-mail Inst.': email_inst,
                        'Data Retirada': [],
                        'Tentativas': []
                    }

    update_dataset_csv(dataset_dict)

def update_dataset_csv(dataset_dict, file_path=None):
    if file_path is None:
        file_path = planilha_diaria

    with open(file_path, mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'RA', 'Nome', 'Campus', 'Curso', 'Situação',
            'Entrada', 'Periodo', 'E-mail Inst.',
            'Data Retirada', 'Tentativas'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for ra, dados in dataset_dict.items():
            writer.writerow({
                'RA': ra,
                'Nome': dados['Nome'],
                'Campus': dados['Campus'],
                'Curso': dados['Curso'],
                'Situação': dados['Situação'],
                'Entrada': dados['Entrada'],
                'Periodo': dados['Periodo'],
                'E-mail Inst.': dados['E-mail Inst.'],
                'Data Retirada': ", ".join(dados['Data Retirada']),
                'Tentativas': ", ".join(dados['Tentativas'])
            })

def combine_sheets():
    df_diaria = pd.read_csv(planilha_diaria)

    df_csv2 = pd.read_csv(csv2)

    df_diaria['RA'] = df_diaria['RA'].astype(str)
    df_csv2['RA'] = df_csv2['RA'].astype(str)

    df_combined = pd.merge(df_diaria, df_csv2[['RA', 'Data Retirada', 'Tentativas']], on='RA', how='outer', suffixes=('', '_csv2'))

    df_combined['Data Retirada'].fillna(df_combined['Data Retirada_csv2'], inplace=True)
    df_combined['Tentativas'].fillna(df_combined['Tentativas_csv2'], inplace=True)

    df_combined.drop(['Data Retirada_csv2', 'Tentativas_csv2'], axis=1, inplace=True)
    df_combined.to_csv(csv_combinado, index=False, encoding='utf-8')

@app.route('/')
def index_start_page():
    prepare_dataset()
    return render_template('index.html', cont_total=cont_alunos+cont_servidores, cont_alunos=cont_alunos, cont_servidores=cont_servidores)

@app.route('/start')
def start_page():
    prepare_dataset()
    return render_template('index.html', cont_total=cont_alunos+cont_servidores, cont_alunos=cont_alunos, cont_servidores=cont_servidores)

@app.route('/check.mita', methods=["GET","POST"])
def check_access():
    global cont_alunos, cont_servidores
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
            count_access = len(dados_aluno['Data Retirada'])

            # verificar se já teve registro de retirada de merenda
            if count_access == 0:
                current_date_time = datetime.now()
                dados_aluno['Data Retirada'].append(current_date_time.strftime(' %d/%m/%Y %H:%M:%S '))
                update_dataset_csv(dataset_dict)
                if ra_code == '162636':
                    cont_servidores += 1 
                    return render_template('permitido.html')
                else:
                    cont_alunos += 1
                    return render_template('permitido.html')
            else:
                # Pega a data e hora atual para a tentativa
                current_date_time = datetime.now()
                tentativas = dados_aluno['Tentativas']
                # Coloca a data e hora atual - lista de tentativa
                tentativas.append(current_date_time.strftime(' %d/%m/%Y %H:%M:%S '))
                update_dataset_csv(dataset_dict)
                if ra_code == '162636':
                    cont_servidores += 1 
                    return render_template('permitido.html')
                return render_template('negado.html')
            
@app.route('/remover', methods=["GET", "POST"])
def remover_servidor():
    if request.method == 'GET':
        return render_template('remover.html')
    elif request.method == 'POST':
        ra_servidor = request.form['ra_servidor']

        if ra_servidor == '162636':
            # Remover 1 merenda do contador de servidores
            global cont_servidores
            if cont_servidores > 0:
                cont_servidores -= 1

        return redirect('/')

@app.route('/dados.mita')
def push_data():
    # Filtra os RAs que tiveram a merenda retirada
    ras_retirada = [ra for ra, dados in dataset_dict.items() if len(dados['Data Retirada']) > 0]

    # Cria um novo dicionário apenas com os RAs filtrados
    dataset_push = {ra: dataset_dict[ra] for ra in ras_retirada}

    # Define o nome da nova planilha
    current_date = current_date_time.strftime('%Y%m%d')
    planilha_push = f"dataset/{current_date}-relatorio.csv"

    # Atualiza o novo dataset na planilha
    update_dataset_csv(dataset_push, planilha_push)

    return render_template('push.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)