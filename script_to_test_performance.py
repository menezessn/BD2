import psycopg2
import time
import os

# --- Configuração da Conexão (mantenha a sua) ---
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "ldb")
DB_USER = os.getenv("DB_USER", "gym_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "gym_password")

# --- Lista de Queries (mantenha a sua) ---
QUERIES = [
    {
        "name": "Q1: Receita Mensal Recorrente (MRR)",
        "sql": """
            SELECT TO_CHAR(p.data_pagamento, 'YYYY-MM') AS ano_mes, SUM(c.valor) AS receita_mensal
            FROM ldb.public.pagamento p JOIN ldb.public.cobranca c ON p.id_cobranca = c.id_cobranca
            GROUP BY ano_mes ORDER BY ano_mes;
        """
    },
    {
        "name": "Q2: Taxa de Churn Mensal",
        "sql": """
            WITH assinaturas_ativas_inicio_mes AS (
                SELECT DATE_TRUNC('month', s.data_criacao) AS mes, COUNT(DISTINCT s.id_aluno) AS total_ativos_inicio
                FROM ldb.public.assinatura s WHERE s.id_status_assinatura = 1 GROUP BY 1
            ), cancelamentos_por_mes AS (
                SELECT DATE_TRUNC('month', sc.data_solicitacao) AS mes, COUNT(DISTINCT a.id_aluno) AS total_cancelados
                FROM ldb.public.solicitacao_cancelamento sc JOIN ldb.public.assinatura a ON sc.id_assinatura = a.id_assinatura GROUP BY 1
            )
            SELECT TO_CHAR(a.mes, 'YYYY-MM') AS ano_mes, a.total_ativos_inicio, COALESCE(c.total_cancelados, 0) AS total_cancelados,
            (COALESCE(c.total_cancelados, 0)::FLOAT / a.total_ativos_inicio) * 100 AS taxa_churn_percentual
            FROM assinaturas_ativas_inicio_mes a LEFT JOIN cancelamentos_por_mes c ON a.mes = c.mes ORDER BY a.mes;
        """
    },
    {
        "name": "Q3: LTV Médio por Aluno",
        "sql": """
            WITH ltv_por_aluno AS (
                SELECT a.id_aluno, SUM(c.valor) AS valor_total_gasto
                FROM ldb.public.aluno a
                JOIN ldb.public.assinatura ass ON a.id_aluno = ass.id_aluno
                JOIN ldb.public.cobranca c ON ass.id_assinatura = c.id_assinatura
                JOIN ldb.public.pagamento p ON c.id_cobranca = p.id_cobranca
                GROUP BY a.id_aluno
            )
            SELECT AVG(valor_total_gasto) AS ltv_medio_por_aluno FROM ltv_por_aluno;
        """
    },
    {
        "name": "Q4: Top 5 Unidades Mais Populares",
        "sql": """
            WITH contagem_checkins AS (
                SELECT u.id_unidade, u.cidade, COUNT(c.id_checkin) AS total_checkins,
                RANK() OVER (ORDER BY COUNT(c.id_checkin) DESC) as ranking
                FROM ldb.public.unidade u JOIN ldb.public.checkin c ON u.id_unidade = c.id_unidade
                GROUP BY u.id_unidade, u.cidade
            )
            SELECT id_unidade, cidade, total_checkins, ranking FROM contagem_checkins WHERE ranking <= 5;
        """
    },
    {
        "name": "Q5: Análise: Motivo de Cancelamento vs. Plano",
        "sql": """
            SELECT p.nome_plano, mc.descricao_motivo_cancelamento, COUNT(*) AS total_ocorrencias
            FROM ldb.public.solicitacao_cancelamento sc
            JOIN ldb.public.assinatura a ON sc.id_assinatura = a.id_assinatura
            JOIN ldb.public.plano p ON a.id_plano = p.id_plano
            JOIN ldb.public.motivo_cancelamento mc ON sc.id_motivo_cancelamento = mc.id_motivo_cancelamento
            GROUP BY p.nome_plano, mc.descricao_motivo_cancelamento ORDER BY total_ocorrencias DESC LIMIT 20;
        """
    },
    {
        "name": "Q6: Inadimplência por Unidade",
        "sql": """
            SELECT u.id_unidade, u.cidade, COUNT(c.id_cobranca) AS quantidade_cobrancas_vencidas, SUM(c.valor) AS valor_total_devido
            FROM ldb.public.cobranca c
            JOIN ldb.public.assinatura a ON c.id_assinatura = a.id_assinatura
            JOIN ldb.public.unidade u ON a.id_unidade = u.id_unidade
            WHERE c.id_status_cobranca = 3 AND c.data_vencimento < CURRENT_DATE
            GROUP BY u.id_unidade, u.cidade ORDER BY valor_total_devido DESC;
        """
    },
    {
        "name": "Q7: Top 10 Alunos Mais Leais",
        "sql": """
            SELECT a.id_aluno, a.nome, SUM(ass.data_vigencia - ass.data_criacao) AS dias_totais_assinado
            FROM ldb.public.aluno a JOIN ldb.public.assinatura ass ON a.id_aluno = ass.id_aluno
            WHERE ass.id_status_assinatura = 1 GROUP BY a.id_aluno, a.nome ORDER BY dias_totais_assinado DESC LIMIT 10;
        """
    },
    {
        "name": "Q8: Receita por Método de Pagamento",
        "sql": """
            SELECT CASE WHEN pc.id_pagamento IS NOT NULL THEN 'Cartão de Crédito' WHEN pp.id_pagamento IS NOT NULL THEN 'PIX' ELSE 'Outro' END AS metodo_pagamento,
            COUNT(p.id_pagamento) AS quantidade_transacoes, SUM(c.valor) AS valor_total
            FROM ldb.public.pagamento p JOIN ldb.public.cobranca c ON p.id_cobranca = c.id_cobranca
            LEFT JOIN ldb.public.pagamento_cartao_credito pc ON p.id_pagamento = pc.id_pagamento
            LEFT JOIN ldb.public.pagamento_pix pp ON p.id_pagamento = pp.id_pagamento
            GROUP BY metodo_pagamento ORDER BY valor_total DESC;
        """
    },
    {
        "name": "Q9: Análise de Atividade vs. Estrutura da Unidade",
        "sql": """
            WITH facilidades_por_unidade AS (SELECT id_unidade, COUNT(id_facilidade) as total_facilidades FROM ldb.public.unidade_facilidade GROUP BY id_unidade),
            atividades_por_unidade AS (SELECT id_unidade, COUNT(id_atividade) as total_atividades FROM ldb.public.unidade_atividade GROUP BY id_unidade),
            checkins_por_unidade AS (SELECT id_unidade, COUNT(id_checkin) as total_checkins FROM ldb.public.checkin GROUP BY id_unidade)
            SELECT u.id_unidade, COALESCE(f.total_facilidades, 0) AS total_facilidades, COALESCE(a.total_atividades, 0) AS total_atividades, COALESCE(c.total_checkins, 0) AS total_checkins
            FROM ldb.public.unidade u
            LEFT JOIN facilidades_por_unidade f ON u.id_unidade = f.id_unidade
            LEFT JOIN atividades_por_unidade a ON u.id_unidade = a.id_unidade
            LEFT JOIN checkins_por_unidade c ON u.id_unidade = c.id_unidade ORDER BY total_checkins DESC;
        """
    },
    {
        "name": "Q10: Funil de Conversão de Planos",
        "sql": """
            SELECT p.nome_plano, COUNT(DISTINCT a.id_aluno) AS total_alunos_inscritos, AVG(c.valor) AS valor_medio_cobranca
            FROM ldb.public.plano p JOIN ldb.public.assinatura a ON p.id_plano = a.id_plano
            JOIN ldb.public.cobranca c ON a.id_assinatura = c.id_assinatura
            GROUP BY p.nome_plano ORDER BY total_alunos_inscritos DESC;
        """
    }
]

def get_explain_plan(cursor, sql_query):
    """Executa EXPLAIN (ANALYZE, BUFFERS) e retorna o plano de execução formatado."""
    try:
        # Prepara a query com EXPLAIN
        explain_query = f"EXPLAIN (ANALYZE, BUFFERS) {sql_query}"
        cursor.execute(explain_query)
        plan = cursor.fetchall()
        
        # Formata o plano para melhor leitura
        formatted_plan = "\n".join([f"    {line[0]}" for line in plan])
        return formatted_plan
    except psycopg2.Error as e:
        return f"    ERRO ao gerar o plano: {e}"

def run_benchmarks():
    """
    Conecta-se ao banco de dados e executa uma lista de queries,
    medindo tempo e obtendo o plano de execução detalhado.
    """
    conn = None
    try:
        print(f"Conectando ao banco de dados '{DB_NAME}' em {DB_HOST}...")
        conn = psycopg2.connect(
            host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
        )
        print("Conexão bem-sucedida.\n")

        cur = conn.cursor()

        for query_info in QUERIES:
            print(f"--- Executando: {query_info['name']} ---")
            
            # 1. Medição de tempo de execução normal
            try:
                start_time = time.time()
                cur.execute(query_info["sql"])
                results = cur.fetchall()
                end_time = time.time()
                duration = end_time - start_time
                
                print(f"  -> Tempo de Execução Total: {duration:.4f} segundos")
                print(f"  -> Linhas Retornadas: {len(results)}")
                
            except psycopg2.Error as e:
                print(f"  -> ERRO na execução normal: {e}")
                conn.rollback()
                continue # Pula para a próxima query em caso de erro

            # 2. Obtenção do Plano de Execução Detalhado
            print("  -> Plano de Execução (EXPLAIN ANALYZE BUFFERS):")
            plan = get_explain_plan(cur, query_info["sql"])
            print(plan)

            print("-" * (len(query_info['name']) + 20) + "\n")

    except psycopg2.OperationalError as e:
        print(f"ERRO DE CONEXÃO: {e}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
    finally:
        if conn is not None:
            conn.close()
            print("Conexão com o banco de dados fechada.")

if __name__ == "__main__":
    run_benchmarks()