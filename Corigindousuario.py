import firebase_admin
from firebase_admin import credentials, auth, firestore
import csv
import io
from datetime import datetime

# Inicializa o Firebase
cred = credentials.Certificate(r'C:\Users\norma\Downloads\sappens-firebase2-firebase-adminsdk-fbsvc-3cb108dd1e.json')  # Caminho para sua chave privada do Firebase
firebase_admin.initialize_app(cred)
db = firestore.client()

# Senha padrão
SENHA_PADRAO = 'Sappens@2025'

# Função para exibir prévia dos dados
def mostrar_previa(dados):
    print("Prévia dos dados a serem enviados:")
    for dado in dados:
        print(dado)
    print("\n")

# Função para cadastrar usuários a partir do CSV
def cadastrar_usuarios_csv(arquivo_csv):
    try:
        resultados = []
        arquivo = io.StringIO(arquivo_csv.decode('utf-8'))  # Usa StringIO para tratar o CSV
        leitor = csv.DictReader(arquivo)
        dados_para_exibir = []

        if not leitor.fieldnames:
            return 'Erro: Arquivo CSV inválido ou vazio'

        for linha in leitor:
            email = linha.get('email', '').strip()
            nome = linha.get('display_name', '').strip()
            escola = linha.get('escola', '').strip()
            telefone = linha.get('phone_number', '').strip()
            nivel = linha.get('nivel', '').strip()
            turma = linha.get('turma', '').strip()
            data_nascimento_str = linha.get('datanascimento', '').strip()
            ano = int(linha.get('ano', '0').strip())
            genero = linha.get('genero', '').strip()
            matricula = linha.get('matricula', '').strip()
            turno = linha.get('turno', '').strip()
            status = True

            if not email:
                resultados.append(f'Erro: Email obrigatório para {nome}')
                continue

            # Converte a data de nascimento para datetime e define o horário fixo de 10:00 PM
            try:
                data_nascimento = datetime.strptime(data_nascimento_str, '%Y-%m-%d')
                # Define o horário fixo de 10:00 PM (22:00)
                data_nascimento = data_nascimento.replace(hour=22, minute=0, second=0)
            except ValueError:
                resultados.append(f'Erro: Data de nascimento inválida para {nome}')
                continue

            dados_para_exibir.append({
                'email': email,
                'nome': nome,
                'telefone': telefone,
                'escola': escola,
                'nivel': nivel,
                'turma': turma,
                'datanascimento': data_nascimento,
                'ano': ano,
                'genero': genero,
                'matricula': matricula,
                'turno': turno,
                'senha': SENHA_PADRAO,
                'status': status
            })

        mostrar_previa(dados_para_exibir)
        confirmar = input("Deseja enviar esses dados para o banco de dados? (Y/N): ").strip().upper()
        if confirmar != 'Y':
            return 'Operação cancelada pelo usuário'

        # Criando uma referência para o batch de operações
        batch = db.batch()
        batch_operations_count = 0

        for dado in dados_para_exibir:
            try:
                # Verifica se o usuário já existe no Firebase Authentication
                try:
                    user = auth.get_user_by_email(dado['email'])
                    # Se o usuário existir, prosseguir sem excluir
                    resultados.append(f'⚠️ Usuário já existe: {dado["email"]}')
                except auth.UserNotFoundError:
                    # Usuário não existe, prosseguir para cadastro
                    pass

                # Criando usuário no Firebase Authentication
                user = auth.create_user(
                    email=dado['email'],
                    password=SENHA_PADRAO
                )

                # Adicionando a operação de gravação no batch
                user_ref = db.collection('users').document(user.uid)
                batch.set(user_ref, {
                    'uid': user.uid,
                    'email': dado['email'],
                    'senha': SENHA_PADRAO,
                    'display_name': dado['nome'],
                    'phone_number': dado['telefone'],
                    'escola': dado['escola'],
                    'nivel': dado['nivel'],
                    'turma': dado['turma'],
                    'datanascimento': dado['datanascimento'],
                    'ano': dado['ano'],
                    'genero': dado['genero'],
                    'matricula': dado['matricula'],
                    'turno': dado['turno'],
                    'status': dado['status'],
                    'created_time': firestore.SERVER_TIMESTAMP
                })

                batch_operations_count += 1

                if batch_operations_count >= 500:  # Limite de operações por lote no Firestore
                    batch.commit()  # Envia o lote de operações
                    batch = db.batch()  # Reinicia o batch
                    batch_operations_count = 0

                resultados.append(f'✅ Usuário cadastrado: {dado["email"]}')
            except Exception as e:
                resultados.append(f'Erro ao cadastrar {dado["email"]}: {str(e)}')

        # Se houver operações restantes no batch, envia elas
        if batch_operations_count > 0:
            batch.commit()

        return '\n'.join(resultados)

    except Exception as e:
        return f'Erro geral: {str(e)}'

# Exemplo de uso
caminho_arquivo = r'C:\Users\norma\Downloads\usuarios_ajustados.csv'  # Caminho do arquivo CSV

with open(caminho_arquivo, 'rb') as arquivo:
    resultado = cadastrar_usuarios_csv(arquivo.read())
    print(resultado)
