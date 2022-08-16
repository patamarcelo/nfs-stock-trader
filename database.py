import os
import datetime
import psycopg2
from config import ELEPHANT_DATABASE_URL

from dotenv import load_dotenv


CREATE_NOTAS_TABLE = """CREATE TABLE IF NOT EXISTS notas (
    id SERIAL PRIMARY KEY,
    data DATE,
    corretora VARCHAR(30),
    notafiscal INTEGER,
    negociacoes_dia INTEGER,
    usuario TEXT,
    cpf VARCHAR(20),
    acao TEXT,    
    tipo TEXT,
    quantidade_negociada INTEGER,
    valor_negociado NUMERIC(4,2),
    valor_total NUMERIC(8,2)    
);"""

INSERT_NOTAS = """INSERT INTO notas 
( corretora, data, notafiscal, negociacoes_dia, usuario, cpf, acao, tipo, quantidade_negociada, valor_negociado, valor_total ) 
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
"""

SEARCH_NOTAS = "SELECT * FROM notas WHERE corretora = %s AND data = %s AND notafiscal = %s AND negociacoes_dia = %s AND usuario  = %s AND cpf = %s AND acao = %s AND tipo = %s AND quantidade_negociada = %s AND valor_negociado = %s AND valor_total = %s;"
# -----Formula para pegar tudo que foi comprado----##
# SUM_TIPO = "SELECT acao, SUM(quantidade_negociada) FROM notas WHERE tipo = 'C' GROUP BY acao;"

SELECT_ALL_NOTAS = "SELECT * FROM notas ORDER BY data ASC;"

# formula para filtrar os saldos no DBm ordem crescente de maior quantidade de ação.

SELECT_ACOES_SALDOS = """
SELECT acao, 
SUM(quantidade_negociada) as soma_acoes_compradas,
corretora, 
RANK() OVER(ORDER BY SUM(quantidade_negociada) DESC)
FROM notas as n
GROUP BY  acao, corretora
HAVING SUM(quantidade_negociada) > 0 
ORDER BY soma_acoes_compradas DESC;
"""

SELECT_ACOES_SALDOS_USER = """
SELECT acao,
SUM(quantidade_negociada) as soma_acoes_compradas,
corretora, 
usuario,
RANK() OVER(ORDER BY SUM(quantidade_negociada) DESC)
FROM notas as n
GROUP BY  acao, corretora, usuario
HAVING SUM(quantidade_negociada) > 0 
ORDER BY soma_acoes_compradas DESC;
"""


SELECT_EMPRESAS_NEGOCIADAS = "SELECT acao from notas GROUP BY acao;"
SELECT_CORRETORA = "SELECT corretora from notas GROUP BY corretora;"
SELECT_USUARIO = "SELECT usuario from notas GROUP BY usuario;"

# Elephant
DATABASE_URL = ELEPHANT_DATABASE_URL
connection = psycopg2.connect(DATABASE_URL)

# LOCAL CONECCTION
# connection = psycopg2.connect(
#     host="localhost", database="notas_bolsa", user="postgres", password="mopmop"
# )

CALENDARIO_MESES = {
    "01": "Janeiro",
    "02": "Fevereiro",
    "03": "Março",
    "04": "Abril",
    "05": "Maio",
    "06": "Junho",
    "07": "Julho",
    "08": "Agosto",
    "09": "Setembro",
    "10": "Outubro",
    "11": "Novembro",
    "12": "Dezembro",
}


def create_tables():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_NOTAS_TABLE)


def add_notas(
    corretora,
    data,
    notafiscal,
    negociacoes_dia,
    usuario,
    cpf,
    acao,
    tipo,
    quantidade_negociada,
    valor_negociado,
    valor_total,
):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                INSERT_NOTAS,
                (
                    corretora,
                    data,
                    notafiscal,
                    negociacoes_dia,
                    usuario,
                    cpf,
                    acao,
                    tipo,
                    quantidade_negociada,
                    valor_negociado,
                    valor_total,
                ),
            )


def search_notas(
    corretora,
    data,
    notafiscal,
    negociacoes_dia,
    usuario,
    cpf,
    acao,
    tipo,
    quantidade_negociada,
    valor_negociado,
    valor_total,
):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                SEARCH_NOTAS,
                (
                    corretora,
                    data,
                    notafiscal,
                    negociacoes_dia,
                    usuario,
                    cpf,
                    acao,
                    tipo,
                    quantidade_negociada,
                    valor_negociado,
                    valor_total,
                ),
            )
            return cursor.fetchone()


def select_all_notas():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_ALL_NOTAS)
            return cursor.fetchall()


def select_saldo_acoes():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_ACOES_SALDOS)
            return cursor.fetchall()


def select_saldo_acoes_user():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_ACOES_SALDOS_USER)
            return cursor.fetchall()


def select_empresas_negociadas():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_EMPRESAS_NEGOCIADAS)
            return cursor.fetchall()


def select_corretora():
    with connection:
        with connection.cursor() as cursor:
            corretoras = cursor.execute(SELECT_CORRETORA)
            return cursor.fetchall()


def select_usuario():
    with connection:
        with connection.cursor() as cursor:
            corretoras = cursor.execute(SELECT_USUARIO)
            return cursor.fetchall()
