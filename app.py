from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import psycopg2
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objs as go
import plotly.utils
import io
import base64
import json
from datetime import datetime, timedelta
import os

app = Flask(__name__)
CORS(app)

# Configuração do banco de dados
DATABASE_CONFIG = {
    'host': 'localhost',
    'database': 'ldb',
    'user': 'gym_user',
    'password': 'gym_password',
    'port': '5432'
}

def get_db_connection():
    """Estabelece conexão com o banco de dados PostgreSQL"""
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

def execute_query(query, params=None):
    """Executa uma query e retorna os resultados como DataFrame"""
    conn = get_db_connection()
    if conn is None:
        return None
    
    try:
        df = pd.read_sql_query(query, conn, params=params)
        return df
    except Exception as e:
        print(f"Erro ao executar query: {e}")
        return None
    finally:
        conn.close()

def create_plotly_chart(df, chart_type, x_col, y_col, title):
    """Cria gráfico usando Plotly"""
    if df is None or df.empty:
        return None
    
    if chart_type == 'bar':
        fig = go.Figure(data=[go.Bar(x=df[x_col], y=df[y_col])])
    elif chart_type == 'line':
        fig = go.Figure(data=[go.Scatter(x=df[x_col], y=df[y_col], mode='lines+markers')])
    else:
        fig = go.Figure(data=[go.Bar(x=df[x_col], y=df[y_col])])
    
    fig.update_layout(
        title=title,
        xaxis_title=x_col,
        yaxis_title=y_col,
        template='plotly_white'
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/api/checkins-rede-diario')
def checkins_rede_diario():
    """Consulta 1: Check-ins diários de usuários"""
    query = """
    SELECT
        c.data_checkin,
        COUNT(c.id_checkin) AS total_checkins
    FROM
        ldb.public.checkin c
    JOIN
        ldb.public.unidade u ON c.id_unidade = u.id_unidade
    JOIN
        ldb.public.assinatura a ON c.id_aluno = a.id_aluno AND c.id_unidade = a.id_unidade
    JOIN
        ldb.public.plano p ON a.id_plano = p.id_plano
    GROUP BY
        c.data_checkin
    ORDER BY
        c.data_checkin;
    """
    
    df = execute_query(query)
    if df is not None and not df.empty:
        df["ano_mes"] = pd.to_datetime(df["data_checkin"]).dt.strftime("%Y-%m-%d")
        return jsonify({'success': True, 'data': df.to_dict(orient='records')})
    else:
        return jsonify({'success': False, 'message': 'Nenhum dado encontrado'})

@app.route('/api/checkins-rede-mensal')
def checkins_rede_mensal():
    """Consulta 2: Check-ins mensais de usuários"""
    query = """
    SELECT
        DATE_TRUNC('month' , c.data_checkin) AS ano_mes,
        COUNT(c.id_checkin) AS total_checkins
    FROM
        ldb.public.checkin c
    GROUP BY
        ano_mes
    ORDER BY
        ano_mes;
    """
    
    df = execute_query(query)
    if df is not None and not df.empty:
        df["ano_mes"] = pd.to_datetime(df["ano_mes"]).dt.strftime("%Y-%m")
        return jsonify({'success': True, 'data': df.to_dict(orient='records')})
    else:
        return jsonify({'success': False, 'message': 'Nenhum dado encontrado'})

@app.route('/api/mau-comparison')
def mau_comparison():
    """Consulta 3: MAU vs Usuários Assinados"""
    query = """
    WITH expanded_subscriptions AS (
        SELECT
            a.id_aluno,
            generate_series(
                date_trunc('month', a.data_criacao),
                date_trunc('month', a.data_vigencia),
                '1 month'::interval
            )::date AS mes_de_vigencia
        FROM
            ldb.public.assinatura a
        WHERE
            a.id_status_assinatura = 1
    ),

    subscribed_users AS (
        SELECT
            mes_de_vigencia AS mes,
            COUNT(DISTINCT id_aluno) AS monthly_subscribed_users
        FROM
            expanded_subscriptions
        GROUP BY
            mes_de_vigencia
    ),

    active_users AS (
        SELECT
            date_trunc('month', data_checkin)::date AS mes,
            COUNT(DISTINCT id_aluno) AS monthly_active_users
        FROM
            ldb.public.checkin
        GROUP BY
            mes
    ),

    monthly_timeline AS (
        SELECT mes FROM subscribed_users
        UNION
        SELECT mes FROM active_users
    )

    SELECT
        DATE_TRUNC('month', mt.mes) AS ano_mes,
        COALESCE(au.monthly_active_users, 0) AS monthly_active_users,
        COALESCE(su.monthly_subscribed_users, 0) AS monthly_subscribed_users
    FROM
        monthly_timeline mt
    LEFT JOIN active_users au ON mt.mes = au.mes
    LEFT JOIN subscribed_users su ON mt.mes = su.mes
    WHERE
        mt.mes IS NOT NULL
    ORDER BY
    mt.mes;
    """
    
    df = execute_query(query)
    if df is not None and not df.empty:
        df["ano_mes"] = pd.to_datetime(df["ano_mes"]).dt.strftime("%Y-%m")
        return jsonify({'success': True, 'data': df.to_dict(orient='records')})
    else:
        return jsonify({'success': False, 'message': 'Nenhum dado encontrado'})

@app.route('/api/cancelamentos-motivo')
def cancelamentos_motivo():
    """Consulta 4: Cancelamentos por motivo"""
    query = """
    SELECT
        mc.descricao_motivo_cancelamento,
        COUNT(sc.id_solicitacao_cancelamento) AS total_cancelamentos
    FROM
        ldb.public.solicitacao_cancelamento sc
    JOIN
        ldb.public.motivo_cancelamento mc ON sc.id_motivo_cancelamento = mc.id_motivo_cancelamento
    GROUP BY
        mc.descricao_motivo_cancelamento
    ORDER BY
        total_cancelamentos DESC;
    """
    
    df = execute_query(query)
    if df is not None and not df.empty:
        return jsonify({'success': True, 'data': df.to_dict(orient='records')})
    else:
        return jsonify({'success': False, 'message': 'Nenhum dado encontrado'})

@app.route('/api/top-unidades-checkins')
def top_unidades_checkins():
    """Consulta 5: Top unidades com mais check-ins"""
    query = """
    SELECT
        CONCAT('Unidade ', u.id_unidade) as nome_unidade,
        COUNT(c.id_checkin) AS total_checkins
    FROM
        ldb.public.checkin c
    JOIN
        ldb.public.unidade u ON c.id_unidade = u.id_unidade
    GROUP BY
        u.id_unidade
    ORDER BY
        total_checkins DESC
    LIMIT 10;
    """
    
    df = execute_query(query)
    if df is not None and not df.empty:
        return jsonify({'success': True, 'data': df.to_dict(orient='records')})
    else:
        return jsonify({'success': False, 'message': 'Nenhum dado encontrado'})
    
@app.route('/api/bottom-unidades-checkins')
def bottom_unidades_checkins():
    """Consulta 6: Top unidades com mais check-ins"""
    query = """
    SELECT
        CONCAT('Unidade ', u.id_unidade) as nome_unidade,
        COUNT(c.id_checkin) AS total_checkins
    FROM
        ldb.public.checkin c
    JOIN
        ldb.public.unidade u ON c.id_unidade = u.id_unidade
    GROUP BY
        u.id_unidade
    ORDER BY
        total_checkins
    LIMIT 10;
    """
    
    df = execute_query(query)
    if df is not None and not df.empty:
        chart = create_plotly_chart(df, 'bar', 'nome_unidade', 'total_checkins', 
                                  'Top 10 Unidades com menos Check-ins')
        return jsonify({'success': True, 'chart': chart, 'data': df.to_dict('records')})
    else:
        return jsonify({'success': False, 'message': 'Nenhum dado encontrado'})
        
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

