

import psycopg2
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker('pt_BR')

# Configurações do banco de dados
DB_HOST = 'localhost'
DB_NAME = 'ldb'
DB_USER = 'gym_user'
DB_PASSWORD = 'gym_password'

# Quantidade de dados a serem gerados
NUM_UNIDADES = 100
NUM_ALUNOS = 100000
NUM_ASSINATURAS = 50000
NUM_CHECKINS = 1000000
NUM_COBRANCAS = 100000
NUM_PAGAMENTOS = 90000
NUM_SOLICITACOES_CANCELAMENTO = 5000

def generate_unidades(cursor, num_unidades):
    print(f'Gerando {num_unidades} unidades...')
    unidades = []
    for i in range(1, num_unidades + 1):
        cep = fake.postcode().replace('-', '')
        logradouro = fake.street_name()
        numero = str(random.randint(1, 2000))
        complemento = fake.city_suffix() if random.random() > 0.5 else None
        cidade = fake.city()
        estado = fake.state_abbr()
        cursor.execute(
            "INSERT INTO ldb.public.unidade (id_unidade, cep, logradouro, numero, complemento, cidade, estado) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (i, cep, logradouro, numero, complemento, cidade, estado)
        )
        unidades.append(i)
    print(f'{num_unidades} unidades geradas.')
    return unidades

def generate_atividades(cursor):
    print('Gerando atividades...')
    atividades_nomes = ['Musculação', 'Natação', 'Crossfit', 'Yoga', 'Pilates', 'Dança', 'Spinning', 'Lutas', 'Funcional', 'Zumba']
    atividades_ids = []
    for i, nome in enumerate(atividades_nomes, 1):
        cursor.execute("INSERT INTO ldb.public.atividade (id_atividade, nome_atividade) VALUES (%s, %s)", (i, nome))
        atividades_ids.append(i)
    print(f'{len(atividades_nomes)} atividades geradas.')
    return atividades_ids

def generate_facilidades(cursor):
    print('Gerando facilidades...')
    facilidades_nomes = ['Piscina', 'Estacionamento', 'Vestiário', 'Armários', 'Cafeteria', 'Wi-Fi', 'Ar Condicionado', 'Acessibilidade', 'Quadra', 'Sauna']
    facilidades_ids = []
    for i, nome in enumerate(facilidades_nomes, 1):
        cursor.execute("INSERT INTO ldb.public.facilidade (id_facilidade, nome_facilidade) VALUES (%s, %s)", (i, nome))
        facilidades_ids.append(i)
    print(f'{len(facilidades_nomes)} facilidades geradas.')
    return facilidades_ids

def generate_unidade_atividade(cursor, unidades_ids, atividades_ids):
    print('Gerando unidade_atividade...')
    for unidade_id in unidades_ids:
        num_atividades = random.randint(1, len(atividades_ids))
        selected_atividades = random.sample(atividades_ids, num_atividades)
        for atividade_id in selected_atividades:
            cursor.execute("INSERT INTO ldb.public.unidade_atividade (id_unidade, id_atividade) VALUES (%s, %s)", (unidade_id, atividade_id))
    print('unidade_atividade gerada.')

def generate_unidade_facilidade(cursor, unidades_ids, facilidades_ids):
    print('Gerando unidade_facilidade...')
    for unidade_id in unidades_ids:
        num_facilidades = random.randint(1, len(facilidades_ids))
        selected_facilidades = random.sample(facilidades_ids, num_facilidades)
        for facilidade_id in selected_facilidades:
            cursor.execute("INSERT INTO ldb.public.unidade_facilidade (id_unidade, id_facilidade) VALUES (%s, %s)", (unidade_id, facilidade_id))
    print('unidade_facilidade gerada.')

def generate_alunos(cursor, num_alunos):
    print(f'Gerando {num_alunos} alunos...')
    alunos = []
    for i in range(1, num_alunos + 1):
        cpf = fake.cpf().replace('.', '').replace('-', '')
        nome = fake.name()
        cursor.execute("INSERT INTO ldb.public.aluno (id_aluno, cpf, nome) VALUES (%s, %s, %s)", (i, cpf, nome))
        alunos.append(i)
    print(f'{num_alunos} alunos gerados.')
    return alunos

def generate_status_assinatura(cursor):
    print('Gerando status_assinatura...')
    status_nomes = ['Ativa', 'Cancelada', 'Pendente']
    status_ids = []
    for i, nome in enumerate(status_nomes, 1):
        cursor.execute("INSERT INTO ldb.public.status_assinatura (id_status_assinatura, nome_status_assinatura) VALUES (%s, %s)", (i, nome))
        status_ids.append(i)
    print(f'{len(status_nomes)} status_assinatura gerados.')
    return status_ids

def generate_motivo_cancelamento(cursor):
    print('Gerando motivo_cancelamento...')
    motivos_nomes = ['Mudança de cidade', 'Problemas financeiros', 'Insatisfação com o serviço', 'Falta de tempo', 'Lesão', 'Outros']
    motivos_ids = []
    for i, nome in enumerate(motivos_nomes, 1):
        cursor.execute("INSERT INTO ldb.public.motivo_cancelamento (id_motivo_cancelamento, descricao_motivo_cancelamento) VALUES (%s, %s)", (i, nome))
        motivos_ids.append(i)
    print(f'{len(motivos_nomes)} motivos_cancelamento gerados.')
    return motivos_ids

def generate_planos(cursor):
    print('Gerando planos...')
    planos_nomes = ['Mensal', 'Trimestral', 'Semestral', 'Anual']
    planos_ids = []
    for i, nome in enumerate(planos_nomes, 1):
        cursor.execute("INSERT INTO ldb.public.plano (id_plano, nome_plano) VALUES (%s, %s)", (i, nome))
        planos_ids.append(i)
    print(f'{len(planos_nomes)} planos gerados.')
    return planos_ids

def generate_assinaturas(cursor, num_assinaturas, unidades_ids, alunos_ids, planos_ids, status_assinatura_ids):
    print(f'Gerando {num_assinaturas} assinaturas...')
    assinaturas = []
    for i in range(1, num_assinaturas + 1):
        id_unidade = random.choice(unidades_ids)
        id_aluno = random.choice(alunos_ids)
        id_plano = random.choice(planos_ids)
        id_status_assinatura = random.choice(status_assinatura_ids) # 1: Ativa, 2: Cancelada, 3: Pendente
        data_criacao = fake.date_between(start_date='-2y', end_date='today')
        
        if id_plano == 1: # Mensal
            data_vigencia = data_criacao + timedelta(days=30)
        elif id_plano == 2: # Trimestral
            data_vigencia = data_criacao + timedelta(days=90)
        elif id_plano == 3: # Semestral
            data_vigencia = data_criacao + timedelta(days=180)
        else: # Anual
            data_vigencia = data_criacao + timedelta(days=365)

        cursor.execute(
            "INSERT INTO ldb.public.assinatura (id_assinatura, id_unidade, id_aluno, id_plano, id_status_assinatura, data_criacao, data_vigencia) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (i, id_unidade, id_aluno, id_plano, id_status_assinatura, data_criacao, data_vigencia)
        )
        assinaturas.append({'id_assinatura': i, 'id_unidade': id_unidade, 'id_aluno': id_aluno, 'data_criacao': data_criacao, 'data_vigencia': data_vigencia, 'id_status_assinatura': id_status_assinatura})
    print(f'{num_assinaturas} assinaturas geradas.')
    return assinaturas

def generate_checkins(cursor, num_checkins, assinaturas):
    print(f'Gerando {num_checkins} checkins...')
    # Filtrar assinaturas ativas para gerar checkins válidos
    assinaturas_ativas = [a for a in assinaturas if a['id_status_assinatura'] == 1 and a['data_vigencia'] >= datetime.now().date()]

    for i in range(1, num_checkins + 1):
        if not assinaturas_ativas:
            print("Não há assinaturas ativas para gerar checkins.")
            break
        
        assinatura = random.choice(assinaturas_ativas)
        id_unidade = assinatura['id_unidade']
        id_aluno = assinatura['id_aluno']
        
        # Garantir que a data do checkin esteja dentro da vigência da assinatura
        start_date = max(assinatura['data_criacao'], datetime.now().date() - timedelta(days=365)) # Checkins de no máximo 1 ano atrás
        end_date = min(assinatura['data_vigencia'], datetime.now().date())

        if start_date > end_date:
            continue # Assinatura já expirou ou ainda não começou

        data_checkin = fake.date_between(start_date=start_date, end_date=end_date)

        cursor.execute(
            "INSERT INTO ldb.public.checkin (id_checkin, id_unidade, id_aluno, data_checkin) VALUES (%s, %s, %s, %s)",
            (i, id_unidade, id_aluno, data_checkin)
        )
    print(f'{num_checkins} checkins gerados.')

def generate_status_cobranca(cursor):
    print('Gerando status_cobranca...')
    status_nomes = ['Pendente', 'Paga', 'Atrasada']
    status_ids = []
    for i, nome in enumerate(status_nomes, 1):
        cursor.execute("INSERT INTO ldb.public.status_cobranca (id_status_cobranca, nome_status_cobranca) VALUES (%s, %s)", (i, nome))
        status_ids.append(i)
    print(f'{len(status_nomes)} status_cobranca gerados.')
    return status_ids

def generate_cobrancas(cursor, num_cobrancas, assinaturas, status_cobranca_ids):
    print(f'Gerando {num_cobrancas} cobranças...')
    cobrancas = []
    for i in range(1, num_cobrancas + 1):
        assinatura = random.choice(assinaturas)
        id_assinatura = assinatura['id_assinatura']
        data_criacao = fake.date_between(start_date=assinatura['data_criacao'], end_date='today')
        data_vencimento = data_criacao + timedelta(days=random.randint(5, 30))
        valor = round(random.uniform(50.0, 300.0), 2)
        id_status_cobranca = random.choice(status_cobranca_ids) # 1: Pendente, 2: Paga, 3: Atrasada

        cursor.execute(
            "INSERT INTO ldb.public.cobranca (id_cobranca, id_assinatura, data_criacao, data_vencimento, valor, id_status_cobranca) VALUES (%s, %s, %s, %s, %s, %s)",
            (i, id_assinatura, data_criacao, data_vencimento, valor, id_status_cobranca)
        )
        cobrancas.append({'id_cobranca': i, 'id_assinatura': id_assinatura, 'id_status_cobranca': id_status_cobranca})
    print(f'{num_cobrancas} cobranças geradas.')
    return cobrancas

def generate_pagamentos(cursor, num_pagamentos, cobrancas):
    print(f'Gerando {num_pagamentos} pagamentos...')
    # Filtrar cobranças pendentes para gerar pagamentos válidos
    cobrancas_pendentes = [c for c in cobrancas if c['id_status_cobranca'] == 1] # 1: Pendente

    for i in range(1, num_pagamentos + 1):
        if not cobrancas_pendentes:
            print("Não há cobranças pendentes para gerar pagamentos.")
            break
        
        cobranca = random.choice(cobrancas_pendentes)
        id_cobranca = cobranca['id_cobranca']
        data_pagamento = fake.date_between(start_date='-1y', end_date='today')

        cursor.execute("INSERT INTO ldb.public.pagamento (id_pagamento, data_pagamento, id_cobranca) VALUES (%s, %s, %s)", (i, data_pagamento, id_cobranca))
        
        # Gerar pagamento de cartão de crédito ou pix aleatoriamente
        if random.random() > 0.5:
            final_cartao = ''.join(random.choices('0123456789', k=4))
            cursor.execute("INSERT INTO ldb.public.pagamento_cartao_credito (id_pagamento, final_cartao) VALUES (%s, %s)", (i, final_cartao))
        else:
            chave_pix = fake.bban()
            cursor.execute("INSERT INTO ldb.public.pagamento_pix (id_pagamento, chave_pix) VALUES (%s, %s)", (i, chave_pix))

        # Atualizar o status da cobrança para 'Paga' (ID 2)
        cursor.execute("UPDATE ldb.public.cobranca SET id_status_cobranca = 2 WHERE id_cobranca = %s", (id_cobranca,))

        # Remover a cobrança da lista de pendentes para evitar múltiplos pagamentos
        cobrancas_pendentes.remove(cobranca)

    print(f'{num_pagamentos} pagamentos gerados.')

def generate_solicitacoes_cancelamento(cursor, num_solicitacoes, assinaturas, motivos_cancelamento_ids):
    print(f'Gerando {num_solicitacoes} solicitações de cancelamento...')
    for i in range(1, num_solicitacoes + 1):
        assinatura = random.choice(assinaturas)
        id_assinatura = assinatura['id_assinatura']
        id_motivo_cancelamento = random.choice(motivos_cancelamento_ids)
        data_solicitacao = fake.date_between(start_date=assinatura['data_criacao'], end_date='today')

        cursor.execute(
            "INSERT INTO ldb.public.solicitacao_cancelamento (id_solicitacao_cancelamento, id_assinatura, id_motivo_cancelamento, data_solicitacao) VALUES (%s, %s, %s, %s)",
            (i, id_assinatura, id_motivo_cancelamento, data_solicitacao)
        )
    print(f'{num_solicitacoes} solicitações de cancelamento geradas.')

def main():
    conn = None
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
        cur = conn.cursor()

        # Gerar dados para tabelas sem dependências ou com dependências estáticas
        unidades_ids = generate_unidades(cur, NUM_UNIDADES)
        atividades_ids = generate_atividades(cur)
        facilidades_ids = generate_facilidades(cur)
        status_assinatura_ids = generate_status_assinatura(cur)
        motivos_cancelamento_ids = generate_motivo_cancelamento(cur)
        planos_ids = generate_planos(cur)
        status_cobranca_ids = generate_status_cobranca(cur)

        # Gerar dados para tabelas com dependências
        generate_unidade_atividade(cur, unidades_ids, atividades_ids)
        generate_unidade_facilidade(cur, unidades_ids, facilidades_ids)
        alunos_ids = generate_alunos(cur, NUM_ALUNOS)
        assinaturas = generate_assinaturas(cur, NUM_ASSINATURAS, unidades_ids, alunos_ids, planos_ids, status_assinatura_ids)
        generate_checkins(cur, NUM_CHECKINS, assinaturas)
        cobrancas = generate_cobrancas(cur, NUM_COBRANCAS, assinaturas, status_cobranca_ids)
        generate_pagamentos(cur, NUM_PAGAMENTOS, cobrancas)
        generate_solicitacoes_cancelamento(cur, NUM_SOLICITACOES_CANCELAMENTO, assinaturas, motivos_cancelamento_ids)

        conn.commit()
        print("População do banco de dados concluída com sucesso!")

    except Exception as e:
        print(f"Erro ao popular o banco de dados: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    main()


