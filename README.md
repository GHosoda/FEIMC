# FEIMC
Software para análise da incerteza de medição de medidas indiretas pelo método de Monte Carlo - MMC.
Desenvolvido como trabalho de conclusão de curso em Engenharia Elétrica pela UFSC.

# Sobre
O programa tem como finalidade a criação de populações para cada entrada de um modelo matemático por meio das respectivas distribuições de probabilidade dos valores medidos de forma direta. Com as populações criadas o cálculo do modelo matemático é feito para individuo da população afim de obter um conjunto de possível resultados.

# Utilização
A utilização do sistema consiste na definição inicial de três parâmetros:
- Conjunto de _DataFrames_ com as entradas do sistema obtidos por meio de um arquivo XLSX;
- Determinação do modelo matemático a ser calculado;
- Escolha dos equipamentos de medição usados nos ensaios.

Finalizado os cálculos o operador poderá selecionar a forma de visualização dos dados, os parâmetros e gerar um relatório com as informações pertinentes.

# Estrutura do programa
O programa foi dividido da seguinte forma para possibilitar alterações futuras:
- \_\_main\_\_.py - Arquivo inicial do programa;
- MMC (Package) - Contém todos os arquivos com as incertezas relacionadas a cada equipamento já cadastrado;
- Calculo (Package) - Contém todos os modelos matemáticos já implementados no sistema;
- Interface (Package) - Unifica todas as interfaces utilizadas no programa;
- Teste.py - Utilizado no teste do correto funcionamento do programa.

# Modelos matemáticos já implementados
- Norma IEEE Standard 112 (Estudo do rendimento de motores de indução trifásicos)
  - Método A
  - Método B
- Modelo de validação do MMC

# Equipamentos cadastrados
- Yokogawa WT500 (Corrente, tensão, potência e frequência);
- HBM T40B (Torque e velocidade rotativa);
- Agilent 34410A (Resistência);
- Yokogawa GP10 (Temperatura).
