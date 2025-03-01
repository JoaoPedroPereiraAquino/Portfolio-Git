import pandas as pd
from datetime import datetime

# Função para gerar email aleatório com base no nome
def gerar_email(nome):
    nome_formatado = nome.replace(" ", "").lower()
    return nome_formatado + "@sappens.com"

# Função para alterar o formato da data de nascimento
def formatar_data(data):
    try:
        return datetime.strptime(data, "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError:
        return data  # Retorna a data original se o formato não for válido

# Função para processar o CSV
def processar_csv(input_file, output_file):
    df = pd.read_csv(input_file)

    # Corrige o nome das colunas: remove espaços e caracteres especiais
    df.columns = df.columns.str.replace(' ', '').str.replace(r'[^\w\s]', '', regex=True)

    # Altera o nome da coluna "ano 1" para "ano" e deleta a coluna "ano 2"
    if 'ano1' in df.columns:
        df.rename(columns={'ano1': 'ano'}, inplace=True)
    if 'ano2' in df.columns:
        df.drop(columns=['ano2'], inplace=True)

    # Gera email aleatório para os registros sem email
    for index, row in df.iterrows():
        if pd.isna(row['email']) or row['email'] == '':
            nome = row['display_name']
            df.at[index, 'email'] = gerar_email(nome)
        
        # Altera "Estudante" para "Aluno" no campo "nivel"
        if row['nivel'] == 'Estudante':
            df.at[index, 'nivel'] = 'aluno'

        # Define o campo "status" como True
        df.at[index, 'status'] = True

        # Formata a data de nascimento
        if pd.notna(row['datanascimento']):
            df.at[index, 'datanascimento'] = formatar_data(row['datanascimento'])

        # Remove o caractere "°" da coluna "ano" e converte para int
        if 'ano' in row and pd.notna(row['ano']):
            ano = str(row['ano']).replace('°', '')  # Remove o "°"
            try:
                df.at[index, 'ano'] = int(ano)  # Converte para int
            except ValueError:
                df.at[index, 'ano'] = None  # Caso não seja um número válido

    # Salva o DataFrame modificado em um novo arquivo CSV
    df.to_csv(output_file, index=False, sep=',', encoding='utf-8')

# Exemplo de uso
input_file = "C:\\Users\\norma\\Downloads\\Planilha Usuarios - Alunos - Página1.csv"  # Caminho do arquivo CSV de entrada
output_file = r"C:\\Users\\norma\\Downloads\\Planilha Usuarios - Alunos - Formatada.csv"  # Caminho do arquivo CSV de saída

processar_csv(input_file, output_file)
