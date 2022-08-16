#!/usr/local/bin/python3

import pdfplumber
import os
from decimal import Decimal
import locale
import pyperclip as pc
from database import create_tables, add_notas, search_notas, select_saldo_acoes_user
from database import (
    CALENDARIO_MESES,
    select_all_notas,
    select_corretora,
    select_usuario,
)
import database
import datetime
from colors import bcolors
from dotenv import load_dotenv
from info_nf import dadosnf
from y_finance import ACOES_CODIGO, get_last_price
import shutil
from email_yag import send_email_yag

from reports import *
import webbrowser


load_dotenv()


locale.setlocale(locale.LC_MONETARY, "pt_BR.UTF-8")
locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")

today = datetime.datetime.now()
today_human = today.strftime("%d/%m/%Y")


# password = input("Qual a sua senha?: ")
password = "019"
quebrapagina = "\n\n"
x = "  "
x_s = " "

numero_nota = "Nr. nota"
notas_ja_importadas = "/notas_importadas/"
# pasta_notas_ja_importadas = (
#     "/Users/marcelopata/Dropbox/03 - Documentos Marcelo/Notas_rico/notas_importadas/"
# )
pasta_notas_ja_importadas = os.path.abspath(os.getcwd()) + '/notas_importadas/'

menu = f"""
Escolha a opcao abaixo:
{bcolors.AMARELO}1){bcolors.FIM} Saldo da Carteira
{bcolors.AMARELO}2){bcolors.FIM} Saldo por Usuário
{bcolors.AMARELO}3){bcolors.FIM} Listar Empresas Negociadas 
{bcolors.AMARELO}4){bcolors.FIM} Listar Notas importadas 
{bcolors.AMARELO}5){bcolors.FIM} Total de Compras e Vendas por usuário / Mês
{bcolors.AMARELO}6){bcolors.FIM} Importar notas da pasta 
{bcolors.AMARELO}7){bcolors.FIM} Enviar e-mail 
{bcolors.AMARELO}8){bcolors.FIM} Sair

Sua Escolha: 
"""


html = []

assunto_list = []


nome_arquivo_origem = gerar_nome_data_arquivo()



def print_notas(notas, entrada_usuario, filtro_corretora):
    corretora = database.select_corretora()
    corretoras = [x[0] for x in corretora]
    html.clear()
    assunto_list.clear()
    assunto = 'Resumo Notas Fiscais'
    assunto_list.append(assunto)
    print(assunto)
    calendario = set()
    lp_total_geral = 0
    for c in corretoras:
        for nota in notas:
            if c == nota[2]:                
                data_cal = nota[1].strftime("%m-%Y")
                calendario.add(data_cal)                
        print("\n")
        if filtro_corretora.lower() in c.lower().split()[0]:
            print(f"{bcolors.UNDERLINE}{bcolors.CBLUEBG}{c}{bcolors.FIM}")
            corretora_html = c.split(" ")[:2]
            corretora_html = " ".join(str(x) for x in corretora_html)
            linha = corretora_html.lower()
            html.append(linha)
        calendario_ordenado_2 = list(calendario)
        new_calendario_ordenado = []
        calendario_ordenado = []        
        for i in calendario_ordenado_2:
            nd = i.split("-")
            ndd = f'{nd[-1]}-{nd[-2]}'
            new_calendario_ordenado.append(ndd)
        new_calendario_ordenado.sort(key=lambda date: datetime.datetime.strptime(date, "%Y-%m"))
        for i in new_calendario_ordenado:
            nd = i.split("-")
            ndd = f'{nd[-1]}-{nd[-2]}'
            calendario_ordenado.append(ndd)                      
        # calendario_ordenado = sorted(calendario)        
        total_investido = 0
        compras_acumulado = {}
        for dias in calendario_ordenado:
            mes = dias[:2]
            mes_nome = CALENDARIO_MESES.get(mes)
            ano = dias[3:]
            if filtro_corretora.lower() in c.lower().split()[0]:
                print(f"{bcolors.CYELLOW2}{mes_nome}|{ano}{bcolors.FIM}")
                linha = f"{mes_nome} {ano}"
                html.append(linha)
            total_venda = 0
            total_compra = 0
            total_lp = 0

            for (
                _id,
                data,
                corretora,
                notafiscal,
                negociacoes_dia,
                usuario,
                cpf,
                acao,
                tipo,
                quantidade_negociada,
                valor_negociado,
                valor_total,
            ) in notas:
                data_iterator = data.strftime("%m-%Y")
                if dias == data_iterator:
                    if c == corretora:
                        if entrada_usuario and filtro_corretora:
                            if (
                                filtro_corretora.lower() in corretora.lower().split()[0]
                                and entrada_usuario.lower() in usuario.lower()
                            ):
                                if tipo == "C":
                                    total_compra = total_compra + valor_total
                                    tipo = f"{bcolors.VERDE}Compra{bcolors.FIM}"
                                    tipo_email = 'Compra'
                                else:
                                    tipo = f"{bcolors.VERMELHO}Venda{x_s}{bcolors.FIM}"
                                    tipo_email = 'Venda'
                                    quantidade_negociada = quantidade_negociada * -1
                                    valor_total = valor_total * -1
                                    total_venda = total_venda + valor_total

                                valor_negociado = f"{locale.currency(valor_negociado, grouping=True, symbol=None)}"
                                valor_total = f"{locale.currency(valor_total, grouping=True, symbol=None)}"
                                quantidade_negociada_formatada = "{:,}".format(
                                    quantidade_negociada
                                ).replace(",", ".")
                                data = data.strftime("%d %b %Y")
                                acao = acao + x if len(acao) < 8 else acao
                                unidades = (
                                    f"Unidades\t\t"
                                    if quantidade_negociada < 10
                                    else "Unidades\t"
                                )
                                unidades = (
                                    f"Unidades\t\t"
                                    if quantidade_negociada < 100
                                    else unidades
                                )
                                corretora = corretora.split(" ")[:2]
                                corretora = " ".join(str(x) for x in corretora)
                                sep_acao = acao.split()[0]
                                # print(sep_acao)
                                if len(sep_acao) < 8:
                                    print(
                                        f"{data} - {corretora} - {usuario} - {acao}\t\t | {tipo} - {quantidade_negociada_formatada} {unidades} - R$ {valor_negociado} - R$ {valor_total}"
                                    )
                                    linha = f"{data} - {corretora} - {usuario} - {acao} - {tipo_email} - {quantidade_negociada_formatada} {unidades} - R$ {valor_negociado} - R$ {valor_total}"
                                    html.append(linha)
                                else:
                                    print(
                                        f"{data} - {corretora} - {usuario} - {acao}\t | {tipo} - {quantidade_negociada_formatada} {unidades} - R$ {valor_negociado} - R$ {valor_total}"
                                    )
                                    linha = f"{data} - {corretora} - {usuario} - {acao} - {tipo_email} - {quantidade_negociada_formatada} {unidades} - R$ {valor_negociado} - R$ {valor_total}"
                                    html.append(linha)
                                # print(
                                #     f"{nota[0]} - {nota[1]} - {nota[2]} - {nota[3]} - {nota[4]} - {nota[5]} - {nota[6]}"
                                # )
                        elif filtro_corretora:
                            if filtro_corretora.lower() in corretora.lower().split()[0]:
                                if tipo == "C":
                                    total_compra = total_compra + valor_total
                                    tipo = f"{bcolors.VERDE}Compra{bcolors.FIM}"
                                    tipo_email = 'Compra'
                                else:
                                    tipo = f"{bcolors.VERMELHO}Venda{x_s}{bcolors.FIM}"
                                    tipo_email = 'Venda'
                                    quantidade_negociada = quantidade_negociada * -1
                                    valor_total = valor_total * -1
                                    total_venda = total_venda + valor_total

                                valor_negociado = f"{locale.currency(valor_negociado, grouping=True, symbol=None)}"
                                valor_total = f"{locale.currency(valor_total, grouping=True, symbol=None)}"
                                quantidade_negociada_formatada = "{:,}".format(
                                    quantidade_negociada
                                ).replace(",", ".")
                                data = data.strftime("%d %b %Y")
                                acao = acao + x if len(acao) < 8 else acao
                                unidades = (
                                    f"Unidades\t\t"
                                    if quantidade_negociada < 10
                                    else "Unidades\t"
                                )
                                unidades = (
                                    f"Unidades\t\t"
                                    if quantidade_negociada < 100
                                    else unidades
                                )
                                corretora = corretora.split(" ")[:2]
                                corretora = " ".join(str(x) for x in corretora)
                                sep_acao = acao.split()[0]
                                # print(sep_acao)
                                if len(sep_acao) < 8:
                                    print(
                                        f"{data} - {corretora} - {usuario} - {acao}\t\t | {tipo} - {quantidade_negociada_formatada} {unidades} - R$ {valor_negociado} - R$ {valor_total}"
                                    )
                                    linha = f"{data} - {corretora} - {usuario} - {acao} - {tipo_email} - {quantidade_negociada_formatada} {unidades} - R$ {valor_negociado} - R$ {valor_total}"
                                    html.append(linha)
                                else:
                                    print(
                                        f"{data} - {corretora} - {usuario} - {acao}\t | {tipo} - {quantidade_negociada_formatada} {unidades} - R$ {valor_negociado} - R$ {valor_total}"
                                    )
                                    linha = f"{data} - {corretora} - {usuario} - {acao} - {tipo_email} - {quantidade_negociada_formatada} {unidades} - R$ {valor_negociado} - R$ {valor_total}"
                                    html.append(linha)
                                # print(
                                #     f"{nota[0]} - {nota[1]} - {nota[2]} - {nota[3]} - {nota[4]} - {nota[5]} - {nota[6]}"
                                # )
                        elif entrada_usuario:
                            if entrada_usuario.lower() in usuario.lower():
                                lucro_prejuizo = 0
                                if tipo == "C":
                                    total_compra = total_compra + valor_total
                                    tipo = f"{bcolors.VERDE}Compra{bcolors.FIM}"
                                    tipo_email = 'Compra'


                                    if compras_acumulado.get(acao) == None:
                                        compras_acumulado[acao] = [quantidade_negociada, valor_negociado]
                                    else:
                                        quant_antiga = compras_acumulado.get(acao)[0]
                                        preco_antigo = compras_acumulado.get(acao)[1]
                                        quant_nova = quant_antiga + quantidade_negociada
                                        preco_novo = ((quant_antiga * preco_antigo) + (quantidade_negociada * valor_negociado)) / quant_nova
                                        compras_acumulado.update({acao: [quant_nova, preco_novo]})
                                else:
                                    tipo = f"{bcolors.VERMELHO}Venda{x_s}{bcolors.FIM}"
                                    tipo_email = 'Venda'
                                    quantidade_negociada = quantidade_negociada * -1
                                    valor_total = valor_total * -1
                                    total_venda = total_venda + valor_total


                                    quant_antiga = compras_acumulado.get(acao)[0]
                                    preco_antigo = compras_acumulado.get(acao)[1]
                                    quant_nova = quant_antiga - quantidade_negociada
                                    compras_acumulado.update({acao: [quant_nova, preco_antigo]})
                                    lucro_prejuizo = (valor_negociado - preco_antigo) * quantidade_negociada

                                total_lp += lucro_prejuizo
                                lucro_prejuizo = f"{locale.currency(lucro_prejuizo, grouping=True, symbol=None)}"
                                valor_negociado = f"{locale.currency(valor_negociado, grouping=True, symbol=None)}"
                                valor_total = f"{locale.currency(valor_total, grouping=True, symbol=None)}"
                                quantidade_negociada_formatada = "{:,}".format(
                                    quantidade_negociada
                                ).replace(",", ".")
                                data = data.strftime("%d %b %Y")


                                acumulado = 0 if compras_acumulado.get(acao)[0] == None else compras_acumulado.get(acao)[0]

                                acumulado_valor = 0 if compras_acumulado.get(acao)[1] == None else compras_acumulado.get(acao)[1]
                                acumulado_valor_form = 0 if acumulado_valor == 0 else f"{locale.currency(acumulado_valor, grouping=True, symbol=None)}"
                                
                                acao = acao + x if len(acao) < 8 else acao
                                unidades = (
                                    f"Unidades\t\t"
                                    if quantidade_negociada < 10
                                    else "Unidades\t"
                                )
                                unidades = (
                                    f"Unidades\t\t"
                                    if quantidade_negociada < 100
                                    else unidades
                                )
                                corretora = corretora.split(" ")[:2]
                                corretora = " ".join(str(x) for x in corretora)
                                sep_acao = acao.split()[0]
                                # print(sep_acao)
                                
                                if len(sep_acao) < 8:
                                    print(
                                        f"{data} - {corretora} - {usuario} - {acao}\t\t | {tipo} - {quantidade_negociada_formatada} {unidades} - Acumulado {acumulado} - \tPreço Médio R$ {acumulado_valor_form} \t\t - L/P R$ {lucro_prejuizo}\t\t - R$ {valor_negociado} - R$ {valor_total}"
                                    )
                                    linha = f"{data} - {corretora} - {usuario} - {acao} - {tipo_email} - {quantidade_negociada_formatada} {unidades} - R$ {valor_negociado} - R$ {valor_total}"
                                    html.append(linha)
                                else:
                                    print(
                                        f"{data} - {corretora} - {usuario} - {acao}\t | {tipo} - {quantidade_negociada_formatada} {unidades} - Acumulado {acumulado} - \tPreço Médio R$ {acumulado_valor_form} \t\t - L/P R$ {lucro_prejuizo}\t\t - R$ {valor_negociado} - R$ {valor_total}"
                                    )
                                    linha = f"{data} - {corretora} - {usuario} - {acao} - {tipo_email} - {quantidade_negociada_formatada} {unidades} - R$ {valor_negociado} - R$ {valor_total}"
                                    html.append(linha)
                                # print(
                                #     f"{nota[0]} - {nota[1]} - {nota[2]} - {nota[3]} - {nota[4]} - {nota[5]} - {nota[6]}"
                                # )
                        else:
                            if tipo == "C":
                                total_compra = total_compra + valor_total
                                tipo = f"{bcolors.VERDE}Compra{bcolors.FIM}"
                                tipo_email = "Compra"
                            else:
                                tipo = f"{bcolors.VERMELHO}Venda{x_s}{bcolors.FIM}"
                                tipo_email = "Venda"
                                quantidade_negociada = quantidade_negociada * -1
                                valor_total = valor_total * -1
                                total_venda = total_venda + valor_total

                            valor_negociado = f"{locale.currency(valor_negociado, grouping=True, symbol=None)}"
                            valor_total = f"{locale.currency(valor_total, grouping=True, symbol=None)}"
                            quantidade_negociada_formatada = "{:,}".format(
                                quantidade_negociada
                            ).replace(",", ".")
                            data = data.strftime("%d %b %Y")
                            acao = acao + x if len(acao) < 8 else acao
                            unidades = (
                                f"Unidades\t\t"
                                if quantidade_negociada < 10
                                else "Unidades\t"
                            )
                            unidades = (
                                f"Unidades\t\t"
                                if quantidade_negociada < 100
                                else unidades
                            )
                            corretora = corretora.split(" ")[:2]
                            corretora = " ".join(str(x) for x in corretora)
                            sep_acao = acao.split()[0]
                            # print(sep_acao)
                            if len(sep_acao) < 8:
                                print(
                                    f"{data} - {corretora} - {usuario} - {acao}\t\t | {tipo} - {quantidade_negociada_formatada} {unidades} - R$ {valor_negociado} - R$ {valor_total}"
                                )

                                linha = f"{data} - {corretora} - {usuario} - {acao} - {tipo_email} - {quantidade_negociada_formatada} {unidades} - R$ {valor_negociado} - R$ {valor_total}"
                                html.append(linha)

                            else:
                                print(
                                    f"{data} - {corretora} - {usuario} - {acao}\t | {tipo} - {quantidade_negociada_formatada} {unidades} - R$ {valor_negociado} - R$ {valor_total}"
                                )
                                # print(
                                #     f"{nota[0]} - {nota[1]} - {nota[2]} - {nota[3]} - {nota[4]} - {nota[5]} - {nota[6]}"
                                # )
                                linha = f"{data} - {corretora} - {usuario} - {acao} - {tipo_email} - {quantidade_negociada_formatada} {unidades} - R$ {valor_negociado} - R$ {valor_total}"
                                html.append(linha)
            if filtro_corretora.lower() in c.lower().split()[0]:
                total_investido = total_investido + total_compra - total_venda

                # print(compras_acumulado)
                
                
                if total_compra > 0:
                    total_compra_formatado = (
                        f"{locale.currency(total_compra, grouping=True, symbol=None)}"
                    )
                    print(
                        f"\t{bcolors.VERDE}Compra:{bcolors.FIM} R$ {total_compra_formatado}"
                    )
                    linha = f"Compra: R$ {total_compra_formatado}"
                    html.append(linha)
                    
                if total_venda > 0:
                    total_venda_formatado = (
                        f"{locale.currency(total_venda, grouping=True, symbol=None)}"
                    )
                    print(
                        f"\t{bcolors.VERMELHO}Venda:{bcolors.FIM} R$ {total_venda_formatado}"
                    )

                    print(f'\n{f"{locale.currency(total_lp, grouping=True, symbol=None)}"}')
                    lp_total_geral += total_lp
                    linha = f"Venda: R$ {total_venda_formatado}"
                    html.append(linha)
                print("\n")
        if filtro_corretora.lower() in c.lower().split()[0]:
            total_investido_formatado = (
                f"{locale.currency(total_investido, grouping=True, symbol=None)}"
            )
            print(
                f"\tTotal Investido: {bcolors.CGREEN2}R$ {total_investido_formatado}{bcolors.FIM}"
            )

            print(f'\nLucro geral com as acoes, sem considerar taxas e impostos: R$ {f"{locale.currency(lp_total_geral, grouping=True, symbol=None)}"}')
            linha = f"Total Investido: R$ {total_investido_formatado}"
            html.append(linha)
    


def print_html(html):
    dados_html = []
    quantiti = 0
    for i in html:   
        if 'Sem saldo na' in i:
            html_f = f'<tr><td></td></tr><tr><td style="color: red;font-weight: bold;">{i}</td> </tr>'
        elif 'xp' in i or 'Rico' in i or 'Xp' in i and len(i) < 30:
            html_f = f'<tr><td></td></tr><tr><td style="color: orange;font-weight: bold;">{i.title()}</td> </tr>'        
        elif 'Compra' in i and len(i) < 30:
            html_f = f'\t<tr style="color: green; text-align: center;"><td>&nbsp;&nbsp;&nbsp; {i}</td> </tr>'
        elif 'Venda' in i and len(i) < 30:
            html_f = f'\t<tr style="color: red; text-align: center;"><td>&nbsp;&nbsp;&nbsp; {i}</td> </tr>'
        elif 'Total Investido' in i and len(i) < 33:
            html_f = f'\t\t<tr style="color: blue; text-align: center;"><td>&nbsp;&nbsp;&nbsp; {i}</td> </tr>'
        elif 'Total Ações' in i:
            html_f = f'<tr><td></td></tr><tr><td style="color: green;font-weight: bold;">{i}</td> </tr>'        
        elif 'Saldo Carteira' in i:
            html_f = f'<tr><td></td></tr><tr><td style="color: green;font-weight: bold;">{i}</td> </tr>'
        elif 'Saldo Total Carteiras' in i:
            html_f = f'<tr><td></td></tr><tr><td style="font-weight: bold;">{i}</td> </tr>'
        elif 'Saldo Total: ' in i:
            html_f = f'<tr><td></td></tr><tr><td style="color: yellow;font-weight: bold;">{i}</td> </tr>'
        elif '202' in i and len(i) < 16:
            html_f = f'<tr><td></td></tr><tr><td style="color: yellow;font-weight: bold;">{i}</td> </tr>'
        elif 'Usuário: ' in i:
            i = i.split(":")[-1]
            html_f = f'<tr><td></td></tr><tr><td style="color: blue;font-weight: bold;">{i}</td> </tr>'        
        else:
            quantiti = quantiti + 1
            html_f = f'<tr><td><bold style="color: yellow;">{quantiti})</bold> &nbsp; {i}</td> </tr>'
        dados_html.append(html_f)
        # print(html)
    html_formatado = ''.join(dados_html)
    style = '<style>tr {}</style>'
    table = f'<table>{html_formatado}</table>'
    html_formatado = style + table
    # print(html_formatado)
    return html_formatado


def format_html(html):
    pass


def print_totais_compra_venda(notas):
    usuario = database.select_usuario()
    usuarios = [x[0] for x in usuario]
    for c in usuarios:
        calendario = set()
        for nota in notas:
            if c == nota[5]:
                for nota in notas:
                    data_cal = nota[1].strftime("%m-%Y")
                    calendario.add(data_cal)
        print("\n")
        print(f"{bcolors.UNDERLINE}{bcolors.CBLUEBG}{c}{bcolors.FIM}")
        print("\n")
        calendario_ordenado_2 = list(calendario)
        new_calendario_ordenado = []
        calendario_ordenado = []        
        for i in calendario_ordenado_2:
            nd = i.split("-")
            ndd = f'{nd[-1]}-{nd[-2]}'
            new_calendario_ordenado.append(ndd)
        new_calendario_ordenado.sort(key=lambda date: datetime.datetime.strptime(date, "%Y-%m"))
        for i in new_calendario_ordenado:
            nd = i.split("-")
            ndd = f'{nd[-1]}-{nd[-2]}'
            calendario_ordenado.append(ndd)    
        corretora = database.select_corretora()
        corretoras = [x[0] for x in corretora]
        for dias in calendario_ordenado:
            mes = dias[:2]
            mes_nome = CALENDARIO_MESES.get(mes)
            ano = dias[3:]
            print(f"\t{bcolors.CYELLOW2}{mes_nome}|{ano}{bcolors.FIM}")
            total_venda = 0
            total_compra = 0
            for (
                _id,
                data,
                corretora,
                notafiscal,
                negociacoes_dia,
                usuario,
                cpf,
                acao,
                tipo,
                quantidade_negociada,
                valor_negociado,
                valor_total,
            ) in notas:
                data_iterator = data.strftime("%m-%Y")
                if dias == data_iterator:
                    if c == usuario:
                        if tipo == "C":
                            total_compra = total_compra + valor_total
                            tipo = f"{bcolors.VERDE}Compra{bcolors.FIM}"
                        else:
                            tipo = f"{bcolors.VERMELHO}Venda{bcolors.FIM}"
                            quantidade_negociada = quantidade_negociada * -1
                            valor_total = valor_total * -1
                            total_venda = total_venda + valor_total

                        valor_negociado = f"{locale.currency(valor_negociado, grouping=True, symbol=None)}"
                        valor_total = f"{locale.currency(valor_total, grouping=True, symbol=None)}"
                        quantidade_negociada = "{:,}".format(
                            quantidade_negociada
                        ).replace(",", ".")
                        data = data.strftime("%d %b %Y")
                        acao = acao + x if len(acao) < 8 else acao
            if total_compra > 0:
                total_compra_formatado = (
                    f"{locale.currency(total_compra, grouping=True, symbol=None)}"
                )
                print(
                    f"\t\t{bcolors.VERDE}Compra:{bcolors.FIM} R$ {total_compra_formatado}"
                )
            if total_venda > 0:
                total_venda_formatado = (
                    f"{locale.currency(total_venda, grouping=True, symbol=None)}"
                )
                print(
                    f"\t\t{bcolors.VERMELHO}Venda:{bcolors.FIM} R$ {total_venda_formatado}"
                )
            print("\n")


def print_saldo_acoes(notas):
    corretora = database.select_corretora()
    corretoras = [x[0] for x in corretora]
    saldo_total_geral = 0
    notas_detal_empresa = database.select_all_notas()
    print("\n")
    pdf = PDF(orientation='P', unit='pt', format='A4')    
    # Insert Title    
    for c in corretoras:
        # if 'XP INVESTIMENTOS' in c:
        saldo_carteira = 0
        saldo_carteira_acoes = 0
        resultado_carteira = 0
        valor_investido_carteira = 0
        print(
            f"{bcolors.UNDERLINE}Corretora: {bcolors.UNDERLINE}{bcolors.CBLUEBG}{c}{bcolors.FIM}"
        )
        pdf.add_page()
        # pdf.set_font(family='Times', size=14, style='B')
        # pdf.cell(w=200, h=15, , border=0,ln=1)
        pdf.set_font(family='Times', size=24, style='B')
        pdf.cell(w=0, h=70, txt=c.title(), border=1, align="C", ln=1)    
        pdf.cell(w=0, h=60, txt=' ', border=0,ln=1) 
        pdf.set_font(family='Times', size=10, style='B')
        pdf.cell(w=140, h=20, txt='Empresa', border='B')
        pdf.cell(w=100, h=20, txt='Quantidade', border='B',align="C")
        pdf.cell(w=100, h=20, txt='Cotação', border='B',align="C")
        pdf.cell(w=100, h=20, txt='Var. %', border='B',align="C")
        pdf.cell(w=0, h=20, txt='Saldo', border='B',align="R",ln=1)
        # pdf.line(270, 300, 1100, 30)
        for acoes in notas:
            # print(f'{acoes[0]} - {acoes[1]} - {acoes[2]} - {acoes[3]}')            
            if acoes[2] == c:
                quantidade = "{:,}".format(acoes[1]).replace(",", ".")
                quantidade_matematica = acoes[1]
                empresa = acoes[0].strip()
                codigo = ACOES_CODIGO.get(f"{empresa}", "")
                try:
                    cotacao = get_last_price(codigo)[0]
                    v_percentual = get_last_price(codigo)[1]
                except:
                    print(
                        f"{bcolors.VERMELHO}Problema em pegar a cotacao{bcolors.FIM} | Empresa: {bcolors.AMARELO}  {empresa} {bcolors.FIM} possívelmente sem código cadastrado "
                    )
                    cotacao = 0
                    v_percentual = 0

                v_percentual_format = (
                    f"{bcolors.VERDE}{round(v_percentual,2)} %{bcolors.FIM}"
                    if v_percentual > 0
                    else f"{bcolors.VERMELHO}{round(v_percentual,2)} %{bcolors.FIM}"
                )

                v_percentual_pdf = round(v_percentual,2)
                cotacao_format = (
                    f"{locale.currency(cotacao, grouping=True, symbol=None)}"
                )
                saldo_total = quantidade_matematica * cotacao
                saldo_total_format = (
                    f"{locale.currency(saldo_total, grouping=True, symbol=None)}"
                )
                saldo_carteira = saldo_carteira + saldo_total
                saldo_carteira_format = (
                    f"{locale.currency(saldo_carteira, grouping=True, symbol=None)}"
                )
                saldo_carteira_acoes = saldo_carteira_acoes + quantidade_matematica
                saldo_carteira_acoes_formatada = "{:,}".format(
                    saldo_carteira_acoes
                ).replace(",", ".")
                if len(empresa) < 7:
                    print(
                        f"Empresa: {empresa}\t\t |{x} Quantidade: {x}{quantidade} Ações | Cotação: R$ {cotacao_format} | %: {v_percentual_format} | Total: R$ {saldo_total_format}"
                    )
                else:
                    print(
                        f"Empresa: {empresa}\t |{x} Quantidade: {x}{quantidade} Ações | Cotação: R$ {cotacao_format} | %: {v_percentual_format} | Total: R$ {saldo_total_format}"
                    )
                pdf.set_font(family='Times', size=10, style='B')
                pdf.cell(w=140, h=20, txt=empresa.title(), border=0)
                pdf.set_font(family='Times', size=10, style='I')
                pdf.cell(w=100, h=20, txt=f'{quantidade} Ações', border=0,align="C")
                pdf.cell(w=100, h=20, txt=f'R$ {cotacao_format}', border=0,align="C")
                
                pdf.set_text_color(0, 100, 0) if v_percentual_pdf > 0 else pdf.set_text_color(139, 0, 0)                 

                pdf.cell(w=100, h=20, txt=f' {str(v_percentual_pdf)} %', border=0,align="C")
                pdf.set_text_color(0, 0, 0)
                pdf.cell(w=0, h=20, txt=f'R$ {saldo_total_format}', border=0,align="R",ln=1)
                quantidade_comprada = 0
                total_comprado = 0
                for notas_detal in notas_detal_empresa:
                    if notas_detal[7] == acoes[0] and notas_detal[2] == c and notas_detal[8] == 'C':
                        # print(f'Empresa: {notas_detal[7]} - Tipo: {notas_detal[8]} -  Quantidade: {notas_detal[9]} - Valor unitário: {notas_detal[10]} - Valor Total: {notas_detal[11]}')
                        total_comprado += notas_detal[11]
                        quantidade_comprada += notas_detal[9]            
                preco_medio_compra = round((total_comprado / quantidade_comprada),2)
                preco_medio_compra_format =  f"{locale.currency(preco_medio_compra, grouping=True, symbol=None)}"
                quantidade_f = quantidade.replace(".","")                                
                valor_investido_incial = preco_medio_compra * int(quantidade_f)
                valor_investido_incial_formatado =  f"{locale.currency(valor_investido_incial, grouping=True, symbol=None)}"
                resultado_atual = saldo_total - float(valor_investido_incial)                    
                resultado_atual_format =  f"{locale.currency(resultado_atual, grouping=True, symbol=None)}"
                resultado_atual_format_color = (f"{bcolors.VERDE}R$ {resultado_atual_format} {bcolors.FIM}" if resultado_atual > 0 else f"{bcolors.VERMELHO}R$ {resultado_atual_format} {bcolors.FIM}"
                ) 
                percentual_resultado = round(((((resultado_atual + float(valor_investido_incial)) / float(valor_investido_incial)) * 100 ) - 100),2)                               
                print(f'Preco Médio: R$ {preco_medio_compra_format} | Valor Investido: R$ {valor_investido_incial_formatado} | Resultado: {resultado_atual_format_color}\n')
                
                pdf.set_font(family='Times', size=8, style='B')
                pdf.set_text_color(0, 0, 0)                
                pdf.cell(w=75, h=10, txt=f'Valor Inicial: ', border=0, align='R')                    
                pdf.set_text_color(0, 0, 255)                    
                pdf.cell(w=75, h=10, txt=f'R$ {str(valor_investido_incial_formatado)}', border=0, align='L')
                
                pdf.set_text_color(0, 0, 0)                
                pdf.cell(w=50, h=10, txt=f'Resultado :', border=0, align='R')                    
                pdf.set_text_color(0, 100, 0) if resultado_atual > 0 else pdf.set_text_color(139, 0, 0)                                                       
                pdf.cell(w=50, h=10, txt=f'R$ {str(resultado_atual_format)}', border=0, align='L')                                                            
                pdf.set_text_color(0, 100, 0) if percentual_resultado > 0 else pdf.set_text_color(139, 0, 0)
                pdf.cell(w=60, h=10, txt=f' {str(percentual_resultado)} %', border=0, align='L')                                                            
                
                pdf.set_font(family='Times', size=8, style='B')
                pdf.set_text_color(0, 0, 0)                
                pdf.cell(w=50, h=10, txt=f'Preço médio: ', border=0)                    
                pdf.set_text_color(0, 100, 0) if preco_medio_compra < cotacao else pdf.set_text_color(139, 0, 0)                                                       
                pdf.cell(w=50, h=10, txt=f'R$ {str(preco_medio_compra_format)}', border=0, align='L',ln=1)
                
                
                pdf.set_text_color(0, 0, 0)                                    
                pdf.cell(w=0, h=16, txt=' ', border=0,ln=1)    

                resultado_carteira += resultado_atual 
                resultado_atual_format =  f"{locale.currency(resultado_carteira, grouping=True, symbol=None)}"
                resultado_carteira_format_color = (f"{bcolors.VERDE}R$ {resultado_atual_format} {bcolors.FIM}" if resultado_atual > 0 else f"{bcolors.VERMELHO}R$ {resultado_atual_format} {bcolors.FIM}"
                )

                valor_investido_carteira += valor_investido_incial 
                valor_investido_carteira_format =  f"{locale.currency(valor_investido_carteira, grouping=True, symbol=None)}"

        saldo_total_geral = saldo_total_geral + saldo_carteira
        if saldo_carteira > 0:
            variacao_percentual_carteira = (resultado_carteira / float(valor_investido_carteira)) * 100
            variacao_percentual_carteira_pdf = round(variacao_percentual_carteira,2)
            variacao_percentual_carteira_format = f"{bcolors.VERDE}{round((variacao_percentual_carteira),2)} %{bcolors.FIM}" if variacao_percentual_carteira > 0 else f"{bcolors.VERMELHO} {round((variacao_percentual_carteira),2)} %{bcolors.FIM}"
        else:
            variacao_percentual_carteira = 0
            variacao_percentual_carteira_pdf = 0
            variacao_percentual_carteira_format = 0
        try:
            print(f'Valor Investido: {valor_investido_carteira_format}')
            print(
                f"{bcolors.CYELLOW}Saldo Carteira:{bcolors.FIM}{bcolors.CGREEN} R$ {saldo_carteira_format}{bcolors.FIM}"
            )
            print(f'Resultado Carteira: {resultado_carteira_format_color} | {variacao_percentual_carteira_format}')
            print(
                f"{bcolors.CYELLOW}Total Ações:{bcolors.FIM} {bcolors.CGREEN}{saldo_carteira_acoes_formatada}{bcolors.FIM}"
            )     
            pdf.cell(w=0, h=50, txt=' ', border=0,ln=1)
            pdf.set_font(family='Times', size=10, style='B')
            pdf.set_y(-200)
            pdf.cell(w=100, h=16, txt='Valor Investido Inicial:', border=0)
            pdf.set_font(family='Times', size=10, style='i')
            pdf.cell(w=85, h=16, txt=f'R$ {str(valor_investido_carteira_format)}', border=0,align="R",ln=1)
            pdf.set_font(family='Times', size=10, style='B')
            pdf.cell(w=100, h=16, txt='Resultado Carteira:', border=0)
            pdf.set_font(family='Times', size=10, style='i')
            pdf.set_text_color(0, 100, 0) if resultado_atual > 0 else pdf.set_text_color(139, 0, 0)                                                       
            pdf.cell(w=85, h=16, txt=f'R$ {str(resultado_atual_format)}', border=0,align="R",ln=1)
            pdf.set_text_color(0, 0, 0)                
            pdf.set_font(family='Times', size=10, style='B')
            pdf.cell(w=100, h=16, txt='Variacao Percentual:', border=0)
            pdf.set_font(family='Times', size=10, style='i')
            pdf.set_text_color(0, 100, 0) if variacao_percentual_carteira_pdf > 0 else pdf.set_text_color(139, 0, 0)                                                       
            pdf.cell(w=85, h=16, txt=f'{str(variacao_percentual_carteira_pdf)} %', border=0,align="R",ln=1)
            pdf.set_text_color(0, 0, 0)                
            pdf.set_font(family='Times', size=10, style='B')
            pdf.cell(w=100, h=16, txt='Saldo Carteira:', border=0)
            pdf.set_font(family='Times', size=10, style='i')
            pdf.cell(w=85, h=16, txt=f'R$ {str(saldo_carteira_format)}', border=0,align="R",ln=1)
            pdf.set_text_color(0, 0, 0)                          
            


        except:
            pass
        print("\n")
    saldo_total_geral_f = (
        f"{locale.currency(saldo_total_geral, grouping=True, symbol=None)}"
    )
    print(
        f"{bcolors.CBLINK}Saldo total: {bcolors.CGREEN2}R$ {saldo_total_geral_f}{bcolors.FIM}"
    )
    pdf.cell(w=0, h=50, txt=' ', border=0,ln=1)
    pdf.set_font(family='Times', size=10, style='B')
    pdf.cell(w=100, h=16, txt='Saldo Total:', border=0)
    pdf.set_font(family='Times', size=10, style='i')
    pdf.cell(w=85, h=16, txt=f'R$ {str(saldo_total_geral_f)}', border=0,align="R",ln=1)
    print("\n\n\n\n\n")
    nome_origem = f'/Users/marcelopata/Desktop/{nome_arquivo_origem}_report_saldo_acoes.pdf'
    pdf.output(nome_origem)
    nome_destino = f'/acoes/{nome_arquivo_origem}_report_saldo_acoes.pdf'
    send_to_server(nome_origem, nome_destino)


def print_saldo_acoes_usuario(notas, filtro_corretora):
    # print(notas)
    html.clear()
    assunto_list.clear()
    assunto = 'Saldo Ações por Carteira'
    assunto_list.append(assunto)
    usuario = database.select_usuario()
    usuarios = [x[0] for x in usuario]
    corretora = database.select_corretora()
    corretoras = [x[0] for x in corretora]
    saldo_carteiras = 0
    notas_detal_empresa = database.select_all_notas()
    for u in usuarios:
        print(
            f"{bcolors.UNDERLINE}Usuário: {bcolors.UNDERLINE}{bcolors.CGREENBG}{u}{bcolors.FIM}\n"
        )
        linha = f'Usuário: {u}'
        html.append(linha)
        saldo_total_geral = 0

        for c in corretoras:
            saldo_carteira = 0
            saldo_carteira_acoes = 0
            if filtro_corretora.lower() in c.lower().split()[0]:
                print(
                    f"{bcolors.UNDERLINE}Corretora: {bcolors.UNDERLINE}{bcolors.CBLUEBG}{c}{bcolors.FIM}"
                )
                corretora_html = c.split(" ")[:2]
                corretora_html = " ".join(str(x) for x in corretora_html)
                linha = corretora_html.title()
                html.append(linha)
            nome_corretora = ""
            for acoes in notas:
                if filtro_corretora:
                    if filtro_corretora.lower() in acoes[2].lower().split()[0]:
                        # print(f'{acoes[0]} - {acoes[1]} - {acoes[2]} - {acoes[3]}')
                        if acoes[2] == c and u == acoes[3]:
                            nome_corretora = acoes[2]
                            quantidade = "{:,}".format(acoes[1]).replace(",", ".")
                            quantidade_matematica = acoes[1]
                            empresa = acoes[0].strip()
                            codigo = ACOES_CODIGO.get(f"{empresa}", "")
                            try:
                                cotacao = get_last_price(codigo)[0]
                                v_percentual = get_last_price(codigo)[1]
                            except:
                                print(
                                    f"{bcolors.VERMELHO}Problema em pegar a cotacao{bcolors.FIM} | Empresa: {bcolors.AMARELO}  {empresa} {bcolors.FIM} possívelmente sem código cadastrado "
                                )
                                cotacao = 0
                                v_percentual = 0

                            v_percentual_format = (
                                f"{bcolors.VERDE}{x_s}{round(v_percentual,2)} %{bcolors.FIM}"
                                if v_percentual > 0
                                else f"{bcolors.VERMELHO}{round(v_percentual,2)} %{bcolors.FIM}"
                            )
                            cotacao_format = (
                                f"{x_s}{locale.currency(cotacao, grouping=True, symbol=None)}"
                                if cotacao < 10
                                else f"{locale.currency(cotacao, grouping=True, symbol=None)}"
                            )
                            saldo_total = quantidade_matematica * cotacao
                            saldo_total_format = f"{locale.currency(saldo_total, grouping=True, symbol=None)}"
                            saldo_carteira = saldo_carteira + saldo_total
                            saldo_carteira_format = f"{locale.currency(saldo_carteira, grouping=True, symbol=None)}"
                            saldo_carteira_acoes = (
                                saldo_carteira_acoes + quantidade_matematica
                            )
                            saldo_carteira_acoes_formatada = "{:,}".format(
                                saldo_carteira_acoes
                            ).replace(",", ".")
                            if len(empresa) < 7:
                                print(
                                    f"Empresa: {empresa}\t\t |{x} Quantidade: {x}{quantidade} Ações | Cotação: R$ {cotacao_format} |  {v_percentual_format} | Total: R$ {saldo_total_format}"
                                )
                                linha = f"Empresa: {empresa}\t\t |{x} Quantidade: {x}{quantidade} Ações | Cotação: R$ {cotacao_format} |  {v_percentual} % | Total: R$ {saldo_total_format}"
                                html.append(linha)
                            else:
                                print(
                                    f"Empresa: {empresa}\t |{x} Quantidade: {x}{quantidade} Ações | Cotação: R$ {cotacao_format} |  {v_percentual_format} | Total: R$ {saldo_total_format}"
                                )
                                linha = f"Empresa: {empresa}\t\t |{x} Quantidade: {x}{quantidade} Ações | Cotação: R$ {cotacao_format} |  {v_percentual} % | Total: R$ {saldo_total_format}"
                                html.append(linha)
                else:
                    if acoes[2] == c and u == acoes[3]:
                        nome_corretora = acoes[2]
                        quantidade = "{:,}".format(acoes[1]).replace(",", ".")
                        quantidade_matematica = acoes[1]
                        empresa = acoes[0].strip()
                        codigo = ACOES_CODIGO.get(f"{empresa}", "")
                        try:
                            cotacao = get_last_price(codigo)[0]
                            v_percentual = get_last_price(codigo)[1]
                        except:
                            print(
                                f"{bcolors.VERMELHO}Problema em pegar a cotacao{bcolors.FIM} | Empresa: {bcolors.AMARELO}  {empresa} {bcolors.FIM} possívelmente sem código cadastrado "
                            )
                            cotacao = 0
                            v_percentual = 0

                        v_percentual_format = (
                            f"{bcolors.VERDE}{x_s}{round(v_percentual,2)} %{bcolors.FIM}"
                            if v_percentual > 0
                            else f"{bcolors.VERMELHO}{round(v_percentual,2)} %{bcolors.FIM}"
                        )
                        cotacao_format = (
                            f"{x_s}{locale.currency(cotacao, grouping=True, symbol=None)}"
                            if cotacao < 10
                            else f"{locale.currency(cotacao, grouping=True, symbol=None)}"
                        )
                        saldo_total = quantidade_matematica * cotacao
                        saldo_total_format = f"{locale.currency(saldo_total, grouping=True, symbol=None)}"
                        saldo_carteira = saldo_carteira + saldo_total
                        saldo_carteira_format = f"{locale.currency(saldo_carteira, grouping=True, symbol=None)}"
                        saldo_carteira_acoes = (
                            saldo_carteira_acoes + quantidade_matematica
                        )
                        saldo_carteira_acoes_formatada = "{:,}".format(
                            saldo_carteira_acoes
                        ).replace(",", ".")
                        if len(empresa) < 7:
                            print(
                                f"Empresa: {empresa}\t\t |{x} Quantidade: {x}{quantidade} Ações | Cotação: R$ {cotacao_format} |  {v_percentual_format} | Total: R$ {saldo_total_format}"
                            )
                            linha = f"Empresa: {empresa}\t\t |{x} Quantidade: {x}{quantidade} Ações | Cotação: R$ {cotacao_format} |  {v_percentual} | Total: R$ {saldo_total_format}"
                            html.append(linha)
                        else:
                            print(
                                f"Empresa: {empresa}\t |{x} Quantidade: {x}{quantidade} Ações | Cotação: R$ {cotacao_format} |  {v_percentual_format} | Total: R$ {saldo_total_format}"
                            )
                            linha = f"Empresa: {empresa}\t\t |{x} Quantidade: {x}{quantidade} Ações | Cotação: R$ {cotacao_format} |  {v_percentual} | Total: R$ {saldo_total_format}"
                            html.append(linha)
            if filtro_corretora.lower() in c.lower().split()[0]:
                saldo_total_geral = saldo_total_geral + saldo_carteira
                if c == nome_corretora:
                    try:
                        print(
                            f"{bcolors.CYELLOW}Saldo Carteira:{bcolors.FIM}{bcolors.CGREEN} R$ {saldo_carteira_format}{bcolors.FIM}"
                        )
                        linha = f'Saldo Carteira: R$ {saldo_carteira_format}'
                        html.append(linha)
                        print(
                            f"{bcolors.CYELLOW}Total Ações:{bcolors.FIM} {bcolors.CGREEN}{saldo_carteira_acoes_formatada}{bcolors.FIM}"
                        )
                        linha = f'Total Ações: {saldo_carteira_acoes_formatada}'
                        html.append(linha)
                        print("\n")
                    except:
                        pass
                else:
                    corretora = c.split(" ")[:2]
                    nome_corretora = " ".join(str(x) for x in corretora)
                    print(
                        f'{bcolors.AMARELO}Usuário: {u.split(" ")[0]} {u.split(" ")[-1]}{bcolors.FIM} |  {bcolors.VERMELHO}Sem saldo na {nome_corretora}{bcolors.FIM}'
                    )
                    linha = f'Usuário: {u.split(" ")[0]} {u.split(" ")[-1]} |  Sem saldo na {nome_corretora}'
                    html.append(linha)
        if filtro_corretora.lower() in acoes[2].lower().split()[0]:
            saldo_total_geral_f = (
                f"{locale.currency(saldo_total_geral, grouping=True, symbol=None)}"
            )
            print("\n")
            print(
                f"Saldo total: {bcolors.CGREEN2}R$ {saldo_total_geral_f}{bcolors.FIM}"
            )
            linha = f'Saldo Total: R$ {saldo_total_geral_f}'
            html.append(linha)
            print("\n\n\n")
        saldo_carteiras = saldo_carteiras + saldo_total_geral
        saldo_carteiras_f = (
            f"{locale.currency(saldo_carteiras, grouping=True, symbol=None)}"
        )
    print(
        f"{bcolors.CBLINK}Saldo total Carteiras: {bcolors.CGREEN2}R$ {saldo_carteiras_f}{bcolors.FIM}"
    )
    linha = f'Saldo Total Carteiras: R$ {saldo_carteiras_f}'
    html.append(linha)
    


def print_empresas_negociadas(notas):
    print("\n\n\n")
    print(f"{bcolors.CVIOLET2}Empresas já negociadas!!{bcolors.FIM}")
    print("\n\n\n")
    for empresa in notas:
        empresa = empresa[0].strip()
        semcodigo = f"{bcolors.VERMELHO}Sem Código{bcolors.FIM}"
        codigo = ACOES_CODIGO.get(empresa, semcodigo)
        # print(f'Empresa: {empresa} - Tamanho: {len(empresa)}')
        if len(empresa) < 7:
            print(f"Empresa: {empresa}\t\t | Código: {codigo} ")
        else:
            print(f"Empresa: {empresa}\t | Código: {codigo} ")


def extrair_informacoes():
    for root, dirs, files in os.walk("."):
        for name in files:
            if name.endswith(".pdf"):
                arq = os.path.join(root, name)
                if notas_ja_importadas not in arq:
                    pdf = pdfplumber.open(arq, password=password)
                    for i in range(len(pdf.pages)):
                        page = pdf.pages[i]
                        text = page.extract_text()
                        # funcao com o numero da Nota fiscal
                        print("\n")
                        dadosnf(text)
                        print("\n")
                        try:
                            shutil.move(arq, pasta_notas_ja_importadas)
                        except Exception as e:
                            print(
                                f"{bcolors.AMARELO}Arquivo não movido: Erro: {bcolors.VERMELHO}{e}{bcolors.FIM}"
                            )

            # funcao que puxa os dados da NF, no arquivo info_nf


def app():
    create_tables()    
    while (user_input := input(menu)) != "8":
        if user_input == "1":
            notas = database.select_saldo_acoes()
            print_saldo_acoes(notas)
        elif user_input == "2":
            filtro_corretora = input(
                f"{bcolors.AMARELO}Digite o nome da {bcolors.AZUL}Corretora{bcolors.FIM}{bcolors.AMARELO} ou deixa em branco para todas:{bcolors.FIM}\n"
            ).title()
            notas = database.select_saldo_acoes_user()
            print_saldo_acoes_usuario(notas, filtro_corretora)
        elif user_input == "3":
            notas = database.select_empresas_negociadas()
            print_empresas_negociadas(notas)
        elif user_input == "4":
            entrada_usuario = input(
                f"{bcolors.AMARELO}Digite o nome do {bcolors.AZUL}Usuario{bcolors.FIM}{bcolors.AMARELO} ou deixa em branco para todos:{bcolors.FIM}\n"
            ).title()
            filtro_corretora = input(
                f"{bcolors.AMARELO}Digite o nome da {bcolors.AZUL}Corretora{bcolors.FIM}{bcolors.AMARELO} ou deixa em branco para todas:{bcolors.FIM}\n"
            ).title()
            notas = database.select_all_notas()
            print_notas(notas, entrada_usuario, filtro_corretora)
        elif user_input == "5":
            notas = database.select_all_notas()
            print_totais_compra_venda(notas)
        elif user_input == "6":
            extrair_informacoes()
        elif user_input == "7":         
            assunto = f'{assunto_list[0]} - {today_human}'
            send_email_yag(print_html(html),assunto)
            # print_html(html)
            
        else:
            print(
                f"{bcolors.BOLD}{bcolors.VERMELHO}Número fora das opções, tente novamente!!{bcolors.FIM}"
            )


if __name__ == "__main__":
    app()
    # notas = database.select_all_notas()
    # for i in notas:
    #     print(f'Corretora: {i[2]} - Empresa: {i[7]} - Tipo: {i[8]} -  Quantidade: {i[9]} - Valor unitário: {i[10]} - Valor Total: {i[11]}')
        
