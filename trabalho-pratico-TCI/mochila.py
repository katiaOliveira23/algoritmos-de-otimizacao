# -*- coding: utf-8 -*-
"""
Created on Sat Sep  4 22:36:31 2021

@author: Katia
"""

import pandas as pd
import pyomo.environ as pyo
from pyomo.environ import *
from pyomo.opt import SolverFactory
import time
import csv
import sys

# imprime o arquivo resumido de desempenho
def imprime_resumo(resultado):
    
    resumo = entradas
    #resumo = entradas.replace('.txt', '.out')
    

    with open('resumo.csv', mode = 'w', newline = '') as csv_file:
        colunas = ['instance', 'gerador', 'tempo', 'LB', 'UB', 'status']
        escrever = csv.DictWriter(csv_file, fieldnames = colunas)
        
        # Escreve o cabeçalho
        #escrever.writeheader()
        
        # Escreve os dados       
        escrever.writerow({'instance': resumo,
                           'gerador': gerador,
                           'tempo': resultado.Solver.Time,
                           'LB': resultado.Problem.lower_bound,
                           'UB': resultado.Problem.upper_bound})
        

# Imprime os resultados obtidos
def imprime_saida (itens, mochilas, model): 
       
    x = model.x
    M = model.M
    I = model.I
    
    saida = entradas.replace('.txt', '.sol')
    
    saida = open(saida, 'w')
    saida.write('{:.2f} \t {}'.format(model.obj(), len(M)))
    #print("{:.2f} \t {}".format(model.obj(), len(M)))
    for M in mochilas.index:
        itens_por_mochila = []
        for I in itens.index:
            if(pyo.value(x[M, I] > 0)):
                itens_por_mochila.append(itens.id[I])                
        saida.write('\nMochila {} \t {}\n'.format(mochilas.id[M], len(itens_por_mochila)))
        #print("{} \t {}".format(mochilas.id[M], len(itens_por_mochila)))
        
        for i in range(len(itens_por_mochila)):
            saida.write('{} \t'.format(itens_por_mochila[i]))
            #print(itens_por_mochila[i])   
    
def resolve(model, itens, mochilas):
    x = model.x
    M = model.M
    I = model.I
    
    model.obj = pyo.Objective(expr = sum(x[M, I] * itens.valor[I] for I in itens.index for M in mochilas.index ), sense = pyo.maximize)
    
    opt = SolverFactory('glpk')
    resultado = opt.solve(model)
    
    #print(resultado)
    #print(resultado.Solver.Time)
    
    # Imprime o resultado
    print("\n==================================================")
    print("Valor total em todas as mochilas {}".format(model.obj()))
    print("===================================================")
    
    imprime_saida(itens, mochilas, model)
    imprime_resumo(resultado)

########## INICIO DA LEITURA DOS DADOS ##########
# importação dos dados de entrada

entradas = sys.argv[1]
gerador = int(sys.argv[2])

arquivo = open (entradas, "r", encoding="utf-8")
i = 0
j = 1
capacidades = []
ids_mochilas = []
ids_itens = []
peso_itens = []
valor_itens = []


for linha in arquivo:
   inputs = linha.split()
   if i == 0:
        qnt_mochilas = int(inputs[1])
        qnt_itens = int(inputs[0])
        i += 1
        
   elif i <= qnt_mochilas:
       capacidades.append(inputs)
       ids_mochilas.append(i)
       i += 1      

   elif j <= qnt_itens:
       peso_itens.append(inputs[1])
       valor_itens.append(inputs[2])
       ids_itens.append(j)
       j += 1
       i += 1     

mochilas = pd.DataFrame(capacidades, columns = ['capacidade'])
mochilas['id'] = ids_mochilas
mochilas[['capacidade']] = mochilas[['capacidade']].apply(pd.to_numeric)

mochilas = mochilas[['id', 'capacidade']]

itens = pd.DataFrame(peso_itens, columns = ['peso'])
itens['valor'] = valor_itens
itens['id'] = ids_itens

# Altera toda as virgulas por ponto, para que seja possível a conversão para números
for l in itens.index:
    itens['peso'][l] = itens['peso'][l].replace(",", ".")
 
# Altera todas as colunas do DataFrame de string para númerica    
itens = itens.apply(pd.to_numeric)

########## FIM DA LEITURA DAS ENTRADAS ###########

########## CONSTRUÇÃO DO MODELO ############
# quantidade de itens e mochilas
j = len(mochilas)
i = len(itens)

# criação do modelo
model = pyo.ConcreteModel()

# guarda a quantidade de mochilas da base de dados
model.M = range(j)
M = model.M

# guarda a quantidade de itens da base de dados
model.I = range(i)
I = model.I

##### VARIÁVEL DE DECISÃO #########
if gerador == 1:
    model.x = pyo.Var(M, I, bounds = (0,1))
    x = model.x

else:    
    model.x = pyo.Var(M, I, within = Binary)
    x = model.x


###### RESTRIÇÕES ########
# limita o somatório do peso dos itens a capacidade total de cada mochila
model.C1 = pyo.ConstraintList()

for M in mochilas.index:
    model.C1.add(expr = sum(x[M, I] * itens.peso[I] for I in itens.index) <= mochilas.capacidade[M])

# determina que cada item só pode ser levado em apenas uma das mochilas    
model.C2 = pyo.ConstraintList()

for I in itens.index:
    model.C2.add(expr = sum(x[M, I] for M in mochilas.index) <= 1)

# 1 - resolve o algorítmo com relaxação linear
# 2 - resolve o algorítimo branch-and-bound (solução ótima)
if (gerador == 1) or (gerador == 2) : 
    resolve(model, itens, mochilas)

# Resove o algorítimo da Heuristica 1
elif gerador == 3:
    print("Hurística 1: \n AINDA NÃO IMPLEMENTADA")
    
# Resove o algorítimo da Heuristica 2
elif gerador == 4:
    print("Hurística 2: \n AINDA NÃO IMPLEMENTADA")
    
else:
    print("GERADOR INESISTENTE")
    

#model.pprint()

        



            

