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
from copy import deepcopy
import pandas as pd
import numpy as np
from math import pi


def definir_escala(valor: float, escalas: list, escalas_auto: bool, **kwargs):
      
        if escalas_auto:
            try:
                melhor_escala = escalas[0]
            except TypeError:
                return 0
            except IndexError:
                return 0
                
            for escala in escalas:
                if valor < escala:
                    return melhor_escala
                else:
                    melhor_escala = escala
            return melhor_escala

############################################################
#           CLASSES
############################################################
class Sensores:
   
    def placebo(self, valor: float, escalas_auto:bool, pontos: int, **kwargs):
        return [valor for i in range(pontos + 1)]
    
##############################
    def termico(self, temperatura, dist, centro):
        if temperatura < centro+dist and temperatura >centro-dist:
            return 0
        else:
            return abs(temperatura - centro) - dist
        
##############################  
    def distribuicoes(self, valor, retangulares:list, normais:list, incertezas:dict, bool_incertezas:dict, pontos:int):
        ret = 1
        parcial = np.ones(pontos+1)*valor
        
        for retangular in retangulares:
            # if bool_incertezas[retangular]:
            parcial += np.random.uniform(-incertezas[retangular]*ret, incertezas[retangular]*ret, pontos+1)
        
        for normal in normais:
            # if bool_incertezas[normal]:
            parcial += np.random.normal(0, incertezas[normal], pontos+1)
        
        parcial[pontos] = valor
        return parcial

##############################
    
        
############################################################
class Tensao(Sensores):
    def wt500(self, valor: float, escalas_auto: bool, pontos:int, **kwargs):
        #Inicialização valores
        temperatura = self.termico(kwargs.get('Temperatura', 25), 5, 25)
        escala = [.5, 1., 2., 5., 10., 20., 40.]
        escala = definir_escala(valor, escala, escalas_auto)
        retangulares = ['Incerteza Leitura', 'Incerteza Escala', 'Incerteza Temperatura', 'Incerteza Resolução']
        normais = []
        consts = {
            'Incerteza Leitura': 0.001,
            'Incerteza Escala': 0.001,
            'Incerteza Temperatura': 0.0003,
            'Incerteza Resolução': 0
            }
    
        incertezas = {
            'Incerteza Leitura': consts['Incerteza Leitura']*valor,
            'Incerteza Escala': consts['Incerteza Escala']*escala,
            'Incerteza Temperatura': consts['Incerteza Temperatura']*temperatura,
            'Incerteza Resolução': 0
            }
        
        return self.distribuicoes(valor, retangulares, normais, incertezas, bool_incertezas = {}, pontos = pontos) 

############################################################
class Corrente(Sensores):
    def wt500(self, valor: float, escalas_auto:bool, pontos: int, **kwargs):
        temperatura = self.termico(kwargs.get('Temperatura', 25), 5, 25)
        escala = [.5, 1, 2, 5, 10, 20, 40]
        escala = definir_escala(valor, escala, escalas_auto)
        retangulares = ['Incerteza Leitura', 'Incerteza Escala', 'Incerteza Temperatura', 'Incerteza Resolução', 'Incerteza Posição Sensor', 'Incerteza Precisão do Sensor', 'Incerteza TC']
        normais = []
        consts = {
            'Incerteza Leitura': 0.001,
            'Incerteza Escala': 0.001,
            'Incerteza Temperatura': 0.0003,
            'Incerteza Resolução': 0,
            'Incerteza Posição Sensor': 0.005,
            'Incerteza Precisão do Sensor': [0.005, .1/10],
            'Incerteza TC': 0.007
            }
        
        incertezas = {
            'Incerteza Leitura': consts['Incerteza Leitura']*valor,
            'Incerteza Escala': consts['Incerteza Escala']*escala,
            'Incerteza Temperatura': consts['Incerteza Temperatura']*temperatura,
            'Incerteza Resolução': consts['Incerteza Resolução'],
            'Incerteza Posição Sensor': consts['Incerteza Posição Sensor']*valor,
            'Incerteza Precisão do Sensor': consts['Incerteza Precisão do Sensor'][1] + consts['Incerteza Precisão do Sensor'][0]*valor,
            'Incerteza TC': consts['Incerteza TC']*valor}
        
        return self.distribuicoes(valor, retangulares, normais, incertezas, bool_incertezas = {}, pontos = pontos)

############################################################
class Potencia(Sensores):
    def wt500(self, valor: float, escalas_auto: bool, pontos: int, **kwargs):
        temperatura = self.termico(kwargs.get('Temperatura', 25), 5, 25)
        escala = []
        escala = definir_escala(valor, escala, escalas_auto, **kwargs)
        corrente = kwargs.get('Corrente', 0)
        tensao = kwargs.get('Tensao', 0)
        
        retangulares = ['Incerteza Leitura', 'Incerteza Escala', 'Incerteza Temperatura','Incerteza Resolução', 'Incerteza FP']
        normais = []
        consts = {
            'Incerteza Leitura': 0.001,
            'Incerteza Escala': 0.001,
            'Incerteza Temperatura': 0.0003,
            'Incerteza Resolução': 0,
            'Incerteza FP': 0.002
            }
        
        #Cálculo valor do ângulo phi
        try:
            phi = valor/(corrente*tensao*(3**0.5))
        except ZeroDivisionError:
            phi = 0
        
        incertezas = {
            'Incerteza Leitura': consts['Incerteza Leitura']*valor,
            'Incerteza Escala': consts['Incerteza Escala']*escala*np.cos(phi),
            'Incerteza Temperatura': consts['Incerteza Temperatura']*temperatura,
            'Incerteza Resolução': consts['Incerteza Resolução'],
            'Incerteza FP': consts['Incerteza FP']*valor*np.tan(phi)
            }
        
        return self.distribuicoes(valor, retangulares, normais, incertezas, bool_incertezas = {}, pontos = pontos)

############################################################
class Frequencia(Sensores):
    def wt500(self, valor: float, escalas_auto: bool, pontos: int, **kwargs):
        escala = []
        escala = definir_escala(valor, escala, escalas_auto, **kwargs)
        retangulares = ['Incerteza Leitura']
        normais = []
        consts = {
            'Incerteza Leitura': 0.006
            }
        incertezas = {'Incerteza Leitura': consts['Incerteza Leitura']*valor}
        
        return self.distribuicoes(valor, retangulares, normais, incertezas, bool_incertezas = {}, pontos = pontos)
        
############################################################
class Resistencia(Sensores):
    def agilent(self, valor: float, escalas_auto: bool, pontos:int, **kwargs):
        retangulares = ['Incerteza Leitura', 'Incerteza Escala', 'Incerteza Temperatura']
        normais = []
        E34410A = [10**(j+2) for j in range(8)]
        escala = definir_escala(valor, E34410A, escalas_auto, **kwargs)
        consts = {
            'Incerteza Leitura': dict(zip(E34410A, [0.01, 0.01, 0.01, 0.01, 0.012, 0.04, 0.8, 8.0])),
            'Incerteza Escala': dict(zip(E34410A, [0.004, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001])),
            'Incerteza Temperatura': dict(zip(E34410A, zip([0.0006, 0.0006, 0.0006, 0.0006, 0.001, 0.003, 0.1, 1.0], [0.0005, 0.0001, 0.0001, 0.0001, 0.0002, 0.0004, 0.0001, 0.0001])))
            }

        incertezas = {
            'Incerteza Leitura':valor*consts['Incerteza Leitura'][escala],
            'Incerteza Escala':escala*consts['Incerteza Escala'][escala],
            'Incerteza Temperatura':valor*consts['Incerteza Temperatura'][escala][0] + escala*consts['Incerteza Temperatura'][escala][1]
            }
        
        return self.distribuicoes(valor, retangulares, normais, incertezas, bool_incertezas = {}, pontos = pontos)

############################################################
class Temperatura(Sensores):
    def gp10(self, valor: float, escalas_auto: bool, pontos: int, **kwargs):
        escala = []
        escala = definir_escala(valor, escala, escalas_auto, **kwargs)
        
        
        retangulares = ['Incerteza Leitura']
        normais = []
        
        incertezas = {'Incerteza Leitura': 0.2}
        
        return self.distribuicoes(valor, retangulares, normais, incertezas, bool_incertezas = {}, pontos = pontos)
        
############################################################
class Torque(Sensores):
    def t40b(self, valor: float, escalas_auto: bool, pontos: int, **kwargs):
        temperatura = self.termico(kwargs.get('Temperatura', 25), 5, 25)
        tpp = kwargs.get('Tpp', 0)
        f_torque = kwargs.get('Frequencia_Torque', 120)
        periodo = kwargs.get('Periodo', 1)
        
        retangulares = ['Incerteza não Linearidade e Histerese',
                        'Incerteza Efeito da Temperatura',
                        'Incerteza Efeito da Temperatura sobre o zero',
                        'Incerteza Tolerância da Sensibilidade',
                        'Incerteza Resolução Limitada',
                        'Incerteza Long Term Drift Over 48h',
                        'Incerteza Tolerância da Frequência',
                        'Incerteza Desvio Integração Numérica']
        
        normais = ['Incerteza Repetibilidade']
        escala = []
        escala = definir_escala(valor, escala, escalas_auto, **kwargs)
        
        consts = {
            'Incerteza não Linearidade e Histerese': 0.0001,
            'Incerteza Repetibilidade': 0.0003,
            'Incerteza Efeito da Temperatura': 0.0005/10,
            'Incerteza Efeito da Temperatura sobre o zero': 0.0005,
            'Incerteza Tolerância da Sensibilidade': 0.001,
            'Incerteza Resolução Limitada': 0.016,
            'Incerteza Long Term Drift Over 48h': 0.0003,
            'Incerteza Tolerância da Frequência': 0.0001,
            'Incerteza Desvio Integração Numérica': 0.0
            }
        
        try:
            perc = valor/escala
        except ZeroDivisionError:
            perc = 1
        fator = 1
        if perc <.6:
            if perc >.2:
                fator = 2
        else:
            fator = 3
        
        incertezas = {
            'Incerteza não Linearidade e Histerese': valor*fator*consts['Incerteza não Linearidade e Histerese'],
            'Incerteza Repetibilidade': valor*consts['Incerteza Repetibilidade'],
            'Incerteza Efeito da Temperatura': temperatura*valor*consts['Incerteza Efeito da Temperatura'],
            'Incerteza Efeito da Temperatura sobre o zero': temperatura*valor*consts['Incerteza Efeito da Temperatura sobre o zero'],
            'Incerteza Tolerância da Sensibilidade': valor*consts['Incerteza Tolerância da Sensibilidade'],
            'Incerteza Resolução Limitada': consts['Incerteza Resolução Limitada'],
            'Incerteza Long Term Drift Over 48h': valor*consts['Incerteza Long Term Drift Over 48h'],
            'Incerteza Tolerância da Frequência': valor*consts['Incerteza Tolerância da Frequência'],
            'Incerteza Desvio Integração Numérica': tpp/(periodo*2*pi*f_torque)
            }
        
        return self.distribuicoes(valor, retangulares, normais, incertezas, bool_incertezas = {}, pontos = pontos)

############################################################
class Velocidade(Sensores):
    def t40b(self, valor: float, escalas_auto: bool, pontos: int, **kwargs):
        retangulares = ['Incerteza Máxima Variação de polos', 'Incerteza Tolerância de Pulso', 'Incerteza Resolução da Medição de Frequência', 'Incerteza Desvio por Integração Numérica']
        normais = [] 
        temperatura = self.termico(kwargs.get('Temperatura', 25), 5, 25)
        escala = []
        escala = definir_escala(valor, escala, escalas_auto, **kwargs)
        polos = kwargs.get('Polos', 4)
        npp = kwargs.get('Npp', 0)
        consts = {
            'Incerteza Máxima Variação de polos': 50*pi/(180*60*3600),
            'Incerteza Tolerância de Pulso':  0.05*pi*1024/(20000*180*60),
            'Incerteza Resolução da Medição de Frequência': 0.01*2*pi,
            'Incerteza Desvio por Integração Numérica': 0.0
            }
        incertezas = {
            'Incerteza Máxima Variação de polos': consts['Incerteza Máxima Variação de polos']*valor*polos,
            'Incerteza Tolerância de Pulso':  valor*consts['Incerteza Tolerância de Pulso'],
            'Incerteza Resolução da Medição de Frequência': consts['Incerteza Resolução da Medição de Frequência'],
            'Incerteza Desvio por Integração Numérica': consts['Incerteza Desvio por Integração Numérica']*npp/0.9/(2*pi*valor/60)*pi/30
            }
        return self.distribuicoes(valor, retangulares, normais, incertezas, bool_incertezas = {}, pontos = pontos)
    
############################################################
