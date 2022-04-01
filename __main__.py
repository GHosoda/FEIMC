############################################################
#
#           TRABALHO DE CONCLUSÃO DE CURSO - TCC
#           GUILHERME HOSODA SOUZA REIS
#           UNIVERSIDADE FEDERAL DE SANTA CATARINA
#           2021-2
#
############################################################
# %%           IMPORTAÇÃO DAS BIBLIOTECAS
############################################################
#from PySide2 import QtCore
from sre_compile import isstring
import numpy as np
import pandas as pd
from copy import deepcopy
import dic_equip
import funcoes
import statsmodels.api as sm
from ui_interface import Ui_MainWindow
from interface_cadastrar import Ui_Cadastro
from interface_nova import Ui_MainWindow
from PyQt6 import QtCore, QtGui, QtWidgets
from datetime import date
from pathlib import Path
from inspect import getmembers, isclass
from FEIMC import FEIMC


############################################################
# %%                CRIAÇÃO DAS CLASSES
############################################################
class Plot:
    def __init__(self, dfs, tipo_plot):
        self.__dfs = dfs
        self.__tipo_plot = tipo_plot


############################################################
# %%                CLASSE INTERFACE
############################################################
class Interface(Ui_MainWindow):
    def __init__(self, MainWindow):
        super().setupUi(MainWindow)
        self.__arquivo_valido = False
        self.b_start.clicked.connect(self.rodar)
        self.b_arquivo.clicked.connect(self.aba_abrir)
        self.i_arquivo.textChanged.connect(self.validar_arquivo)
        self.b_maquina.clicked.connect(self.aba_cadastrar)
        self.b_ensaio.clicked.connect(self.indicar_col_abas)
        self.cb_todos_resultados.stateChanged.connect(self.selecionar_tudo)
        self.set_comboboxes()
        self.__wt_abas = {}
        self.__wt_colunas = {}

########################
# %% Novas Janelas
########################
    def aba_cadastrar(self):
        cadastro = NovoCadastro(None)
        cadastro.exec()

    def aba_abrir(self):
        fname = QtWidgets.QFileDialog.getOpenFileName(
            parent=None, filter='Excel Files(*xlsx)')
        self.i_arquivo.setText(fname[0])

########################
# %% Executar programa
########################
    def aviso(self, inputs):
        erro = False
        texto = ''
        if inputs['Arquivo'] == '':
            erro = True
            texto = f'{texto}- Preenchimento do arquivo.\n'

        if inputs['Operador'] == '':
            erro = True
            texto = f'{texto}- Preenchimento do operador.\n'
            pass

        if '' in self.__wt_abas.values():
            erro = True
            texto = f'{texto}- Relacionamento entre as abas.\n'
            
        if '' in self.__wt_colunas.values():
            #erro = True
            texto = f'{texto}- Relacionamento entre as colunas.\n'

        if erro:
            inicial = 'Impossível executar a função, necessário:'
            mensagem = f'{inicial}\n{texto}'
            self.erro(mensagem)
            return False
        return True

    def rodar(self):
        inputs, checkboxes_config, checkboxes_results, comboboxes, dia, pontos = self.dicionario_dados()
        checagem = self.aviso(inputs)
        if checagem:
            saida = FEIMC(self.__excel)
            saida.remapeamento(self.__wt_abas, self.__wt_colunas)

########################
# %% Config Dados
########################
    def set_comboboxes(self):
        maquinas = pd.read_csv('Maquinas\maquinas.csv',
                               sep=';', index_col=None)
        classes = [i[0] for i in (getmembers(funcoes, isclass))]
        self.c_ensaio.addItems(classes),
        self.c_maquina.addItems(list(maquinas['id'])),
        self.c_corrente.addItems(['WT500']),
        self.c_frequencia.addItems(['WT500']),
        self.c_potencia.addItems(['WT500']),
        self.c_resistencia.addItems(['Agilent34410A']),
        self.c_rpm.addItems(['HBMTB40']),
        self.c_temperatura.addItems(['YokogawaGP10']),
        self.c_tensao.addItems(['WT500']),
        self.c_torque.addItems(['HBMTB40'])

        dia = (int(x) for x in str(date.today()).split('-'))
        self.dateEdit.setDate(QtCore.QDate(*dia))

    def dicionario_dados(self):
        # Aquisição das entradas do usuário
        inputs = {'Arquivo': self.i_arquivo.text(),
                  'Operador': self.i_operador.text()}

        # Aquisição das checkboxes com as incertezas na Aba configurações
        incertezas = {'Corrente': self.cb_corrente.isChecked(),
                      'Tensao': self.cb_tensao.isChecked(),
                      'Frequencia': self.cb_frequencia.isChecked(),
                      'Potencia': self.cb_potencia.isChecked(),
                      'Resistencia': self.cb_resistencia.isChecked(),
                      'RPM': self.cb_rpm.isChecked(),
                      'Temperatura': self.cb_temperatura.isChecked(),
                      'Torque': self.cb_torque.isChecked()}

        # Aquisição dos valores das checkboxes na aba de resultados
        checkboxes_results = {'boxplot': self.cb_boxplot.isChecked(),
                              'desvio_padrao': self.cb_desvio_padrao.isChecked(),
                              'histograma': self.cb_histograma.isChecked(),
                              'histograma_nominal': self.cb_histograma_nominal.isChecked(),
                              'max_min': self.cb_max_min.isChecked(),
                              'media': self.cb_media.isChecked(),
                              'mediana': self.cb_mediana.isChecked(),
                              'moda': self.cb_moda.isChecked(),
                              'quartis': self.cb_quartis.isChecked(),
                              'variancia': self.cb_variancia.isChecked(),
                              'violino': self.cb_violino.isChecked()}

        # Aquisição dos valores das comboboxes - exceto equipamentos
        comboboxes = {'Ensaio': self.c_ensaio.currentText(),
                      'Maquina': self.c_maquina.currentText()}

        # Aquisição dos equipamentos em comboboxes
        equipamentos = {'Corrente': self.c_corrente.currentText(),
                        'Frequencia': self.c_frequencia.currentText(),
                        'Potencia': self.c_potencia.currentText(),
                        'Resistencia': self.c_resistencia.currentText(),
                        'RPM': self.c_rpm.currentText(),
                        'Temperatura': self.c_temperatura.currentText(),
                        'Tensao': self.c_tensao.currentText(),
                        'Torque': self.c_torque.currentText()}

        # Pegando os valores das abas da tabela de Widgets
        wt_abas = {}
        for i in range(self.__linhas_abas):
            dici = {self.tw_abas.item(i, 0).text(): self.tw_abas.cellWidget(i, 1).currentText()}
            wt_abas.update(dici)
        self.__wt_abas = wt_abas
        
        # Pegando os valores das abas da tabela de Widgets
        wt_colunas = {}
        for i in range(self.__linhas_colunas):
            try:
                dici = {self.tw_colunas.item(i, 0).text(): self.tw_colunas.cellWidget(i, 1).currentText()}
                wt_colunas.update(dici)
            except:
                pass
        self.__wt_colunas = wt_colunas
        
        dia = self.dateEdit.date()
        pontos = self.s_pontos.value()

        return(inputs, incertezas, checkboxes_results, comboboxes, dia, pontos)

    def indicar_col_abas(self):
        if not(self.__arquivo_valido):
            mensagem = (
                'Necessário Selecionar o arquivo antes de Configurar o Ensaio')
            self.erro(mensagem)
        self.__classe = eval(f'funcoes.{self.c_ensaio.currentText()}')
        self.__objeto = self.__classe()
        self.__linhas_abas = self.w_tabelas(
            self.tw_abas, self.__objeto.tabelas, list(self.__abas), nome='abas')
        colunas = []
        for aba in self.__abas:
            colunas.append(aba)
            for coluna in list(self.__colunas[aba]):
                colunas.append(coluna)
        filtro = [i for i, coluna in enumerate(
            colunas) if coluna in self.__abas]
        self.__linhas_colunas = self.w_tabelas(
            self.tw_colunas, colunas, self.__colunas_juntas, nome='colunas', fora=filtro)

    def w_tabelas(self, tabela, ensaio, excel, nome, fora=[]):
        excel.append('')
        excel.reverse()
        tamanho = len(ensaio)
        tabela.setRowCount(tamanho)
        for i in range(tamanho):
            tabela.setItem(i, 0, QtWidgets.QTableWidgetItem(ensaio[i]))
            if not(i in fora):
                tabela.setCellWidget(i, 1, ComboboxTabelas(excel, i, nome))
        return tamanho

    def selecionar_tudo(self):
        estado = self.cb_todos_resultados.isChecked()
        dicionario = {'boxplot': self.cb_boxplot,
                      'desvio_padrao': self.cb_desvio_padrao,
                      'histograma': self.cb_histograma,
                      'histograma_nominal': self.cb_histograma_nominal,
                      'max_min': self.cb_max_min,
                      'media': self.cb_media,
                      'mediana': self.cb_mediana,
                      'moda': self.cb_moda,
                      'quartis': self.cb_quartis,
                      'variancia': self.cb_variancia,
                      'violino': self.cb_violino}

        for valor in dicionario.values():
            valor.setChecked(estado)

########################
# %%  Config Arquivo
########################
    def validar_arquivo(self):
        try:
            self.__excel = pd.read_excel(
                self.i_arquivo.text(), sheet_name=None)
            self.__abas = self.__excel.keys()
            self.__colunas = {}
            self.__colunas_juntas = []

            for aba in self.__abas:
                self.__colunas[aba] = self.__excel[aba].columns.values
                for coluna in self.__colunas[aba]:
                    self.__colunas_juntas.append(f'{coluna}##{aba}')

            self.__arquivo_valido = True
        except:
            mensagem = f'Impossivel ler o arquivo: {self.i_arquivo.text()}'
            self.erro(mensagem)
            self.i_arquivo.setText('')
            self.__arquivo_valido = False
        pass

########################
# %%  Config MsgErro
########################
    def erro(self, mensagem):
        msg_arquivo = QtWidgets.QMessageBox()
        msg_arquivo.setWindowTitle('Aviso')
        msg_arquivo.setText(mensagem)
        msg_arquivo.exec()


############################################################
# %%                CLASSE TABELA COM COMBOBOX
############################################################
class ComboboxTabelas(QtWidgets.QComboBox):
    def __init__(self, lista, numero, local):
        super().__init__()
        self.addItems(lista)


############################################################
# %%                CLASSE NOVO CADASTRO
############################################################
class NovoCadastro(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Cadastro()
        self.ui.setupUi(self)
        # self.b_cm_cadastrar.clicked.connect(self.nova_maquina) #Identificar erro

    def nova_maquina(self):
        dicionario = self.pegar_dados()
        valido = self.validar(dicionario)
        if valido:
            antigo = pd.read_csv('Maquinas\maquinas.csv',
                                 sep=';', index_col=None)
            novo = pd.DataFrame(dicionario)
            final = pd.concat([antigo, novo])
            final.reset_index(drop=True, inplace=True)
            final.drop_duplicates(subset=['id'], inplace=True, keep='last')
            final.to_csv('Maquinas\maquinas.csv', sep=';', index=False)
            self.b_cm_cadastrar.clicked.connect(self.quit())

    def validar(self, dicionario):
        dicionario.pop('Outros')
        condicao = any(list(map(lambda x: x == '', dicionario.values())))
        return not(condicao)

    def pegar_dados(self):
        dicionario = {'id': ['MIT NOVA 5 cv 2'],
                      'Potência (kW)': ['3.7'],
                      'Tensão (V)': ['380'],
                      'Corrente (A)': ['8.2'],
                      'Frequência (Hz)': ['60'],
                      'Rotação (RPM)': ['1740'],
                      'cos fi': ['0.78'],
                      'Polos': ['4']}
        return dicionario


############################################################
# %% INÍCIO DO PROGRAMA
############################################################
if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    Principal = QtWidgets.QMainWindow()
    ui = Interface(Principal)
    Principal.show()
    sys.exit(app.exec())
