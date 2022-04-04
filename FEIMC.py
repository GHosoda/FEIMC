############################################################
#
#           TRABALHO DE CONCLUSÃO DE CURSO - TCC
#           GUILHERME HOSODA SOUZA REIS
#           UNIVERSIDADE FEDERAL DE SANTA CATARINA
#           2021-2
#
############################################################
#           IMPORTAÇÃO DAS BIBLIOTECAS
############################################################
# %%
#from PySide2 import QtCore
from os import path
import numpy as np
import pandas as pd
from copy import deepcopy
from Calculo.IEEE112 import *
from datetime import date
from MMC.mmc import *
from scipy import stats
import seaborn as sns
from functools import partial
from concurrent.futures import ProcessPoolExecutor as Executor


############################################################
# %%
class FEIMC:
    def __init__(self, dfs, classe, **kwargs):
        self._dfs = dfs
        self._classe = classe


    def mmc_incertezas(self, pontos, equipamentos, grandezas, escalas_auto,**kwargs):
        aux = {}
        for aba, df in self._dfs.items():
            df = df.astype(object)
            for linha in df.index:
                dicionario = df.loc[linha].to_dict()
                for coluna in df.columns:
                    a = deepcopy(df.loc[linha, coluna])
                    df.at[linha, coluna] = self.avaliar(a, coluna, pontos ,equipamentos, grandezas, dicionario, escalas_auto, **kwargs)
                    # if coluna == 'Torque':
                    #     print(df.loc[linha, coluna])
            aux[aba] = df
        return aux
                
    def avaliar(self, valor, coluna, pontos,equipamentos, grandezas ,d_linha, escalas_auto, **kwargs):
        for grandeza, l_coluna in grandezas.items():
            if coluna in l_coluna:
                d_linha.update(kwargs)
                funcao = eval(f'{grandeza}.{equipamentos[grandeza]}')
                classe = eval(grandeza)
                classe = classe()
                funcao = eval(f'classe.{equipamentos[grandeza]}')
                return funcao(valor, escalas_auto, pontos, **d_linha)
        return [valor for i in range(pontos+1)]
    
    def df2list(self, dict, pontos):
        lista = []
        for i in range(pontos+1):
            aux = {}
            for aba, df in dict.items():
                aux[aba] = df.applymap(lambda x: x[i])
            lista.append(aux)
        return lista
        
#OK
    def calcular(self, dfs_mc,**kwargs):
        metodo = self._classe
        dfs_mc = metodo.calculo(dfs_mc, **kwargs)
        return dfs_mc
        
    def list2df(self, lista):
        dfs = deepcopy(lista[0])
        pontos = len(lista) - 1
        for aba, df in dfs.items():
            for coluna in df.columns:
                dfs[aba][coluna] = dfs[aba][coluna].astype('object')
                for index in df.index:
                    aux = []
                    for i in range(pontos):
                        aux.append(lista[i][aba].loc[index, coluna])
                    dfs[aba].at[index, coluna] = deepcopy(aux)
        return dfs

    def saidas(self, lista, prints, motor, pontos):
        dfs = self.list2df(lista)
        df = dfs['Resultado']
        x = 'Potencia [pu]'
        y = 'Rendimento'
        
        #Calculo dos dataframes de saída
        dados = {'desvio_padrao': df.applymap(lambda x: np.std(x)),
                 'max_min': [df.applymap(lambda x: np.max(x)), df.applymap(lambda x: np.min(x))],
                 'media': df.applymap(lambda x: np.mean(x)),
                 'mediana': df.applymap(lambda x: np.median(x)),
                 'moda': df.applymap(lambda x: stats.mode(x)),
                 'quartis': [df.applymap(lambda x: stats.scoreatpercentile(x, 25)), df.applymap(lambda x: stats.scoreatpercentile(x, 75))],
                 'variancia': df.applymap(lambda x: np.var(x))}
        
        nomes = {'max_min': ['máximo', 'mínimo'],
                 'quartis': ['1_4', '3_4']}
        
        #Salvar os dataframes
        with pd.ExcelWriter('Resumo.xlsx') as writer:
            for chave, valor in dados.items():
                if prints[chave]:
                    if isinstance(valor, list):
                        for i, pedaco in enumerate(valor):
                            pedaco.to_excel(writer, nomes[chave][i])
                    else:
                        valor.to_excel(writer, chave)
                         
        #Configuração plots
        df_plots = df[[x, y]]
        df_plots[x] = df_plots[x].map(lambda k: np.mean(k))
        eixo_y = list(df_plots[y])
        yy = []
        tamanho = len(eixo_y[0]) 
        list_x = list(df_plots[x])
        eixo_x = [f'{x:.3f}' for x in list_x]
        eixo_x = [[x]*tamanho for x in eixo_x]
        xx = []
        
        for i in range(len(eixo_x)):
            for j in range(tamanho):
                xx.append(eixo_x[i][j])
                yy.append(eixo_y[i][j])
        
        dados = {x: xx, y: yy}
        dados = pd.DataFrame(dados)
        
        absolute_difference = lambda lista : abs(lista - 1)
        prox_nominal =  f'{min(list_x , key=absolute_difference):.3f}'
        dados_nom = dados[dados[x] == prox_nominal]
        sns.set_theme()
        
        plots = {'boxplot': partial(sns.boxplot, x = x, y = y, data = dados),
                 'histograma': partial(sns.histplot, x = x, y = y, data = dados, element = 'poly'),
                 'violino': partial(sns.violinplot, x = x, y = y, data = dados, inner="quartile"),
                 'histograma_nominal': partial(sns.histplot, x = y, y = x, data = dados_nom, kde = True)}
        
        ax = plots['violino']  
        
        #Salvar os plots
        for chave, valor in plots.items():
            if prints[chave]:
                ax = plots[chave]
                plot = ax()
                plot.set_title(f'Motor: {motor} para População do MMC: {pontos}')
                local = path.join('Plots', f'{chave}motor{motor}{pontos}.png')
                plot.figure.savefig(local)
                plot.clear()

        return dados


############################################################
# %%          INÍCIO DO PROGRAMA
############################################################
if __name__ == '__main__':
    motor = 'B'
    arquivo = {'A': r'Ensaios\A.xlsx',
               'B': r'Ensaios\B.xlsx',
               'C': r'Ensaios\C.xlsx'}
    
    motores = {'A': {'Polos': 4,
                     'Potencia Nominal': 3700},
               'B': {'Polos': 6,
                     'Potencia Nominal': 7500},
               'C': {'Polos': 4,
                     'Potencia Nominal': 11000}}
    
    arquivo = arquivo[motor]
    
    dfs = pd.read_excel(
        arquivo, sheet_name=None)
    abas = ['Resistências', 'de Carga', 'a Vazio']
    abas_excel = ['Ensaio_Vazio', 'Ensaio_Carga',
                  'Ensaio_Termico_Carga', 'Ensaio_Termico_Vazio']
    colunas_excel = {'Resistencias': ['RS', 'RT', 'ST', 'T_amb', 'T_res'],
                     'de Carga': ['Tensao', 'Corrente', 'Potencia', 'Frequencia', 'Temperatura', 'Torque', 'RPM'],
                     'a Vazio': ['Tensao', 'Corrente', 'Potencia', 'Frequencia']
                     }

    kwargs = {'Material Estator': 'Cobre',
              'Material Rotor': 'Alumínio',
              'Potencia Nominal': 11000,
              'Polos': 4,
              'Tensao Nominal': 380}
    
    kwargs.update(motores[motor])
    print(kwargs)
    
    prints = {'boxplot': True,
              'desvio_padrao': False,
              'histograma': False,
              'histograma_nominal': False,
              'max_min': True,
              'media': True,
              'mediana': False,
              'moda': False,
              'quartis': False,
              'variancia': True,
              'violino': True}
    
    grandezas = {'Tensao': ['Tensao'],
                 'Corrente': ['Corrente'],
                 'Potencia': ['Potencia'],
                 'Frequencia': ['Frequencia'],
                 'Resistencia': ['RS', 'RT', 'ST'],
                 'Temperatura': ['T_amb', 'T_res'],
                 'Torque': ['Torque'],
                 'Velocidade': ['Velocidade']}
    
    equipamentos = {'Tensao': 'wt500',
                    'Corrente': 'wt500',
                    'Potencia': 'wt500',
                    'Frequencia': 'wt500',
                    'Resistencia': 'agilent',
                    'Temperatura': 'gp10',
                    'Torque': 't40b',
                    'Velocidade': 't40b'}
    
    
    pontos = 1000
    f = FEIMC(dfs, IEEE112MetodoB())
    dfs_mmc = f.mmc_incertezas(pontos, equipamentos, grandezas, escalas_auto = True)
    list_mmc = f.df2list(dfs_mmc, pontos)
    dfs = f.calcular(list_mmc, **kwargs)
    print('Calculei')
    dfs2 = f.saidas(dfs, prints, motor, pontos)
    # print(dfs[0]['Resultado'])
    
    # classe = IEEE112MetodoB()
    # incertezas = classe.incertezas()
    # #print(incertezas)
    # dfs = classe.calculo(k, **kwargs)
    # dfs2 = FEIMC.saidas(FEIMC, dfs, prints)
