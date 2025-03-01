import csv
import io
from collections import Counter

# Função para verificar os usuários e gerar o arquivo CSV com os usuários ajustados
def verificar_usuarios_csv(arquivo_csv, caminho_saida):
    try:
        arquivo = io.StringIO(arquivo_csv.decode('utf-8'))  # Usa StringIO para tratar o CSV
        leitor = csv.DictReader(arquivo)
        emails_csv = []
        nomes_csv = []
        dados_usuarios = []

        if not leitor.fieldnames:
            return 'Erro: Arquivo CSV inválido ou vazio'

        for linha in leitor:
            email = linha.get('email', '').strip()
            nome = linha.get('display_name', '').strip()
            if email:
                emails_csv.append(email)
            if nome:
                nomes_csv.append(nome)
            dados_usuarios.append(linha)  # Armazena os dados do usuário para depois escrever no novo arquivo

        if not emails_csv:
            return 'Nenhum email encontrado no CSV'

        # Identificar emails duplicados
        duplicados = [email for email, contagem in Counter(emails_csv).items() if contagem > 1]
        emails_ajustados = {}
        contador_emails = Counter(emails_csv)

        for email, contagem in contador_emails.items():
            if contagem > 1:
                indices = [i for i, e in enumerate(emails_csv) if e == email]
                for i, index in enumerate(indices[1:], start=1):
                    novo_email = f"{nomes_csv[index].replace(' ', '_').lower()}@sappens.com"
                    emails_csv[index] = novo_email
                    emails_ajustados[email] = novo_email

        # Criando novo arquivo CSV com os dados ajustados
        with open(caminho_saida, mode='w', newline='', encoding='utf-8') as arquivo_saida:
            campos = leitor.fieldnames  # Mantém os campos do CSV original
            escritor = csv.DictWriter(arquivo_saida, fieldnames=campos)

            escritor.writeheader()  # Escreve o cabeçalho no novo arquivo

            for linha, email in zip(dados_usuarios, emails_csv):
                if email in emails_ajustados.values():
                    linha['email'] = email  # Atualiza o email na linha
                    escritor.writerow(linha)  # Escreve a linha no arquivo CSV

        # Exibir a contagem dos usuários ajustados
        usuarios_ajustados_count = len(emails_ajustados)
        print(f'Total de usuários com e-mail ajustado devido à duplicação: {usuarios_ajustados_count}')

        return emails_ajustados

    except Exception as e:
        return f'Erro: {str(e)}'

# Exemplo de uso
caminho_arquivo = r'C:\Users\norma\Downloads\Planilha Usuarios - Alunos - Formatada.csv'  # Caminho do arquivo CSV
caminho_saida = r'C:\Users\norma\Downloads\usuarios_ajustados.csv'  # Caminho de saída para o novo arquivo CSV

with open(caminho_arquivo, 'rb') as arquivo:
    resultado = verificar_usuarios_csv(arquivo.read(), caminho_saida)
    print(resultado)
