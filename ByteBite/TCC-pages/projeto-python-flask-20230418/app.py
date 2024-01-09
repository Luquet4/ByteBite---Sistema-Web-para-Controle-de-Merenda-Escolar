from flask import Flask, render_template, request, url_for
import numpy as np
import csv
from tqdm import tqdm
from datetime import datetime
import pandas as pd
import os
import ast

app = Flask(__name__)

current_date_time = datetime.now()
dataset_name = "dataset/dataset.csv"
dataset_name_day = f"dataset/{current_date_time.strftime('%Y%m%d')}-dataset.csv"
dataset_dict = {}

def prepare_dateset():
    # ler csv em uma lista
    cont_line = 0
    if os.path.exists(dataset_name_day):
        with open(dataset_name_day, encoding='utf8') as data:
            for line in tqdm(csv.reader(data)):
                cont_line = cont_line + 1
                if cont_line > 1: # pular a primeira linha por ser o cabeçalho
                    list_frequency = ast.literal_eval(line[2])
                    dataset_dict[line[1]] = list_frequency
    else:
        with open(dataset_name, encoding='utf8') as data:
            for line in tqdm(csv.reader(data)):
                cont_line = cont_line + 1
                if cont_line > 1: # pular a primeira linha por ser o cabeçalho
                    list_frequency = []
                    list_frequency.append(line[4])
                    dataset_dict[line[10]] = list_frequency
        update_dataset(dataset_dict)
        

def update_dataset(dataset_dict):
    dict = {}
    list_keys = []
    list_data = []
    for key in tqdm(dataset_dict):
        list_keys.append(key)
        list_data.append(dataset_dict[key])
    
    dict = {'RA': list_keys, 'DADOS': list_data}
    df = pd.DataFrame(dict) 
    df.to_csv(dataset_name_day)
    
@app.route('/start')
def start_page():
    prepare_dateset()
    return render_template('index.html')

@app.route('/check_access.mita', methods=['POST'])
def check_access():
    if request.method == 'POST':
        ra_code = request.form['ra']
        # verificar se existe o RA no dataset
        if ra_code not in dataset_dict:
            return render_template('user.html')
        
        # caso o RA esteja cadastrado no dataset 
        #ra_student = ra_code
        list_data = dataset_dict[ra_code]
        #name_student = list_data[0]
        count_access = len(list_data)
        
        # verificar se ja teve registro de retirada de merenda
        if count_access <= 1:
            current_date_time = datetime.now()
            list_data.append(current_date_time.strftime('%Y%m%d%H%M%S'))
            update_dataset(dataset_dict)
            return render_template('permitido.html')
        else:
            return render_template('negado.html')

if __name__ == '__main__':
  app.run()
