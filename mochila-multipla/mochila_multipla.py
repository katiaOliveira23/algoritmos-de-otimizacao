# -*- coding: utf-8 -*-
"""
Created on Mon Aug 30 11:28:27 2021

@author: Katia
"""

# j = indice das mochilas
# i = indice do elemento
# C = capacidade da mochila
# e = elemento
# C_usada = capacidade usada 
# C_disponivel = capacidade disponível 


import pandas as pd
import pyomo.environ as pyo
from pyomo.environ import *
from pyomo.opt import SolverFactory
import numpy as np

produtos = pd.read_excel('mochila_multipla.xlsx', sheet_name = 'elementos')
mochilas = pd.read_excel('mochila_multipla.xlsx', sheet_name = 'mochila')

# quantidade de itens e mochilas
j = len(mochilas)
i = len(produtos)

# criação do modelo
model = pyo.ConcreteModel()

# guarda a quantidade de mochilas da base de dados
model.m = range(j)
m = model.m

# quarda a quantidade de itens da base de dados
model.p = range(i)
p = model.p

# determina a variável de decisão com seus respectivos limites
model.x = pyo.Var(m, p, within = pyo.Binary)
x = model.x

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
model.pprint()

# define o solver a ser utilizado na otimização, neste caso, o GLPK
opt = SolverFactory('glpk')
result = opt.solve(model)


# Imprime os resultados obtidos
print("\n==================================================")
print("Valor total em todas as mochilas {}".format(model.obj()))
print("===================================================")

for m in mochilas.id:
    print("\nCarga da Mochila {} com capacidade de {}kg".format(m + 1, mochilas.carga_maxima[m]))
    valor_total = 0
    carga_total = 0
    for p in produtos.id:
        if(pyo.value(x[m, p]) == 1):
            carga_total = carga_total + (pyo.value(x[m, p] * produtos.peso[p]))
            valor_total = carga_total + (pyo.value(x[m, p] * produtos.valor[p]))
            print("{} \tR$ {:.2f} \t {}Kg ".format(p, produtos.valor[p], produtos.peso[p]))
           
           
    print("\nValor Total: R$ {:.2f} \nCarga Total: {}Kg \nCapacidade Ociosa: {}Kg"
          .format(valor_total, carga_total, (mochilas.carga_maxima[m] - carga_total)))       
           

