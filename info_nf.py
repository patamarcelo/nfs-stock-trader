import locale
from database import create_tables, add_notas, search_notas
import database
import datetime
from colors import bcolors



locale.setlocale(locale.LC_MONETARY, "pt_BR.UTF-8")





def dadosnf(titulo):
    titulo = titulo.split("\n")
    corretora = titulo[3]
    numero_nota = titulo[2].split(" ")[0]
    data_nota = titulo[2].split(" ")[-1]
    # print(data_nota)
    timestamp = datetime.datetime.strptime(data_nota,"%d/%m/%Y")
    # print(timestamp)
    

    cliente = titulo[10].split(" ")[1:4]
    cliente = " ".join(cliente).title()
    cpf = titulo[10].split(" ")[-1]
    print(
        f"Corretora: {titulo[3]} | NF {numero_nota} | Data: {data_nota} | Cliente: {cliente}"
    )
    print("\n")
    negociacoes_dia = 0
    for i in titulo:
        ibov = "1-BOVESPA"
        if ibov in i:
            negociacoes_dia = negociacoes_dia + 1
            i = i.split(ibov)[-1]
            i = i.replace(" ", ";")
            i = i.split(";")
            tipo_op = i[1]
            valor_unitario = float(i[-3].replace(",", "."))
            valor_unitario = round(valor_unitario, 2)
            quantidade = int(i[-4].replace(".", ""))
            quantidade = (quantidade * -1) if tipo_op == 'V' else quantidade         
            valor_total = round(valor_unitario * quantidade,2)
            papel_negociado = " ".join(i[3:5])
            papel_negociado = papel_negociado.strip()
            if len(numero_nota) > 4:
                notas = database.search_notas(corretora,timestamp,numero_nota,negociacoes_dia,cliente,cpf,papel_negociado,tipo_op,quantidade,valor_unitario,valor_total,)


                if notas:                
                    print(f"{bcolors.BOLD}{bcolors.VERMELHO}Transação já incluída no sistema {bcolors.FIM}")
                else:
                    if tipo_op == 'V':
                        print(
                            f"{bcolors.BOLD}{bcolors.VERDE}Transação incluida com sucesso!! {bcolors.FIM}Acão: {papel_negociado} - {bcolors.BOLD}{bcolors.VERMELHO}Tipo: {tipo_op}{bcolors.FIM} - Quantidade Vendida: {quantidade} - Valor: R$ {locale.currency(valor_unitario, grouping=True, symbol=None)} - Total: R$ {locale.currency(valor_total, grouping=True, symbol=None)}"
                        )
                    else: 
                        print(
                            f"{bcolors.BOLD}{bcolors.VERDE}Transação incluida com sucesso!! {bcolors.FIM}Acão: {papel_negociado} - {bcolors.BOLD}{bcolors.VERDE} Tipo: {tipo_op}{bcolors.FIM} - Quantidade Comprada: {quantidade} - Valor: R$ {locale.currency(valor_unitario, grouping=True, symbol=None)} - Total: R$ {locale.currency(valor_total, grouping=True, symbol=None)}"
                        )            
                    add_notas(corretora,timestamp, numero_nota,negociacoes_dia,cliente,cpf,papel_negociado,tipo_op,quantidade,valor_unitario,valor_total,)
            else:
                numero_nf = f'{bcolors.VERMELHO} Sem Nota {bcolors.FIM}'
                print(
                    f"{bcolors.BOLD}{bcolors.VERMELHO}Nota Fiscal ainda não gerada, aguarda o próximo dia para a mesma ser gerada!!{bcolors.FIM}"
                )
                print(f"{bcolors.AMARELO}Seguem as operações da mesma abaixo:{bcolors.FIM}")
                print(
                    f"Corretora: {corretora} - Data: {data_nota} - Numero_Nota: {numero_nf} - Neg.Dia: {negociacoes_dia} - Cliente: {cliente} - Cpf: {cpf} Acão: {papel_negociado} - Tipo: {tipo_op} - Quantidade Comprada: {quantidade} - Valor: R$ {valor_unitario} - Total: R$ {valor_total}"
                )



def numeronotafiscal(titulo):
    nfnumero = titulo.split()
    numero_nota = nfnumero[8]
    data_nf = nfnumero[10]

    # for (i, item) in enumerate(nfnumero, start=1):
    #     print(f"index: {i} - Valor: {item}")
    print(f"NF: {numero_nota} - Data: {data_nf}")
