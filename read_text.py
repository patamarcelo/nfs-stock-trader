#!/usr/local/bin/python3

import pdfplumber
import os
from decimal import Decimal
import locale
import pyperclip as pc

from info_nf import dadosnf, numeronotafiscal


numero_nota = "Nr. nota"
for root, dirs, files in os.walk("."):
    for name in files:
        if name.endswith(".pdf"):
            arq = os.path.join(root, name)
            pdf = pdfplumber.open(arq, password="019")
            page = pdf.pages[0]
            text = page.extract_text()
            # text = text.replace(" ", ";")
            titulo = text.split("\n")
            # for (i, item) in enumerate(titulo):
            #     print(f"index: {i} - Valor: {item}")
            corretora = titulo[3]
            numero_nota = titulo[2].split(" ")[0]
            data_nota = titulo[2].split(" ")[-1]
            cliente = titulo[10].split(" ")[1:4]
            cliente = " ".join(cliente).title()
            cpf = titulo[10].split(" ")[-1]
            # print(
            #     f"Corretora: {titulo[3]} | NF {numero_nota} | Data: {data_nota} | Cliente: {cliente}"
            # )
            print("\n")
            negociacoes_dia = 0
            for i in titulo:
                ibov = "1-BOVESPA"
                if ibov in i:
                    i = i.split(ibov)[-1]
                    negociacoes_dia = negociacoes_dia + 1
                    i = i.replace(" ", ";")
                    i = i.split(";")
                    # print(i)
                    valor_unitario = float(i[-3].replace(",", "."))
                    valor_unitario = round(valor_unitario, 2)
                    quantidade = int(i[-4].replace(".", ""))
                    valor_total = round(valor_unitario * quantidade, 2)
                    tipo_op = i[1]
                    papel_negociado = " ".join(i[3:5])
            if len(numero_nota) > 4:
                        print(
                            f"Corretora: {corretora} - Data: {data_nota} - Numero_Nota: {numero_nota} - Neg.Dia: {negociacoes_dia} - Cliente: {cliente} - Cpf: {cpf} Acão: {papel_negociado} - Tipo: {tipo_op} - Quantidade Comprada: {quantidade} - Valor: R$ {valor_unitario} - Total: R$ {valor_total} {type(valor_total)}"
                        )
                    #     # corretora,numero_nota,negociacoes_dia,cliente,papel_negociado,tipo_op,quantidade,valor_unitario,valor_total,)
                    # else:
                    #     i = i.replace(" ", ";")
                    #     i = i.split(";")
                    #     # print(i)
            else:
                numero_nota = 'Sem Nota'
                print(
                    f"Nota Fiscal ainda não gerada, aguarda o próximo dia para a mesma ser gerada!!"
                )
                print("Seguem as operações da mesma abaixo:")
                print(
                    f"Corretora: {corretora} - Data: {data_nota} - Numero_Nota: {numero_nota} - Neg.Dia: {negociacoes_dia} - Cliente: {cliente} - Cpf: {cpf} Acão: {papel_negociado} - Tipo: {tipo_op} - Quantidade Comprada: {quantidade} - Valor: R$ {valor_unitario} - Total: R$ {valor_total} {type(valor_total)}"
                )

            print("\n")
            
