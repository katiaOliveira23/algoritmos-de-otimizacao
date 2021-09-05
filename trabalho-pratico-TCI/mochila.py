# -*- coding: utf-8 -*-
"""
Created on Sat Sep  4 22:36:31 2021

@author: Katia
"""

import pandas as pd
import pyomo.environ as pyo
from pyomo.environ import *
from pyomo.opt import SolverFactory
import csv


# Imprime os resultados obtidos
def imprime (produtos, mochilas, model, x):
    saida = open('saida.txt', 'w')
    saida.write('{}\t {}'.format(model.obj(), j))
    print("{:.2f} \t {}".format(model.obj(), j))
    for m in mochilas.id:
        itens = []
        for p in produtos.id:
            if(pyo.value(x[m, p] > 0)):
                itens.append(p + 1)
          
        saida.write('\n{} \t {}'.format(m + 1, len(itens)))
        print("{} \t {}".format(m + 1, len(itens)))
        for i in range(len(itens)):
            saida.write('\n{}'.format(itens[i]))
            print(itens[i])
 

# resolve o modelo
def resolve(model, produtos, mochilas, x, m, p, i, j, gerador):
    
    # limita o somatório do peso dos itens a capacidade total de cada mochila
    model.C1 = pyo.ConstraintList()
    for m in mochilas.id:
        model.C1.add(expr = sum(x[m, p] * produtos.peso[p] for p in produtos.id) <= mochilas.carga_maxima[m])
        
    # determina que cada item só pode ser levado em apenas uma das mochilas
    model.C2 = pyo.ConstraintList()
    for p in produtos.id:
        model.C2.add(expr = sum(x[m, p] for m in mochilas.id) <= 1)    
        
    # define a função objetivo para maximizar o valor total levado    
    model.obj = pyo.Objective(expr = sum(x[m,p] * produtos.valor[p] for p in produtos.id for m in mochilas.id ), sense = pyo.maximize) 
        
    # imprime toda a construção do modelo
    # model.pprint()
        
    # define o solver a ser utilizado na otimização, neste caso, o GLPK
    opt = SolverFactory('glpk')
    result = opt.solve(model)
    
    # imprime os resultados 
    imprime(produtos, mochilas, model, x)
    
    #teste csv 


# importação dos dados de entrada
produtos = pd.read_excel('mochila_multipla.xlsx', sheet_name = 'elementos')
mochilas = pd.read_excel('mochila_multipla.xlsx', sheet_name = 'mochila')

# quantidade de itens e mochilas
j = len(mochilas)
i = len(produtos)

# criação do modelo
model_relaxacao = pyo.ConcreteModel()
model_branch_and_bound = pyo.ConcreteModel()

# guarda a quantidade de mochilas da base de dados
model_relaxacao.m = range(j)
m = model_relaxacao.m

# quarda a quantidade de itens da base de dados
model_relaxacao.p = range(i)
p = model_relaxacao.p

# determina a variável de decisão com seus respectivos limites 
# Agorítmo com relaxação linear   
gerador = 1
model_relaxacao.x = pyo.Var(m, p, bounds = (0, 1))
x = model_relaxacao.x
resolve(model_relaxacao, produtos, mochilas, x, m, p, i, j, gerador)

# determina a variável de decisão com seus respectivos limites  
# Algorítimo exato branch_and_bound  
gerador = 2
model_branch_and_bound.x = pyo.Var(m, p, within = Binary)
x = model_branch_and_bound.x
resolve(model_branch_and_bound, produtos, mochilas, x, m, p, i, j, gerador)




        



            

