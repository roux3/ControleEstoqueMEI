from lib2to3.pgen2.token import AT
import threading
import holidays
import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem, QAbstractItemView, QHeaderView, QMessageBox,QTableWidgetItem
from PyQt5.uic import loadUi
from PyQt5.QtCore import QRegExp, QDate
from PyQt5 import QtGui,QtCore
from matplotlib.style import use
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import mysql.connector
import time
import gc
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

with open('host.txt','r') as arquivo:
    hostname = arquivo.read()


class Canvas(FigureCanvas):
        def __init__(parent,val,rotulos,colors):
            fig, ax = plt.subplots(figsize=(5, 4), dpi=200)
            super().__init__(fig)
            plt.pie(x=val, labels=rotulos,colors=colors,autopct='%1.1f%%')


hoje = time.ctime()

dia = time.strftime("%Y-%m-%d")
diasVazios = []
diasFeriados = []

ano = time.strftime("%Y")

if(time.strftime('%m')== '01'):
    ano = str(int(time.strftime("%Y"))-1)


range_feriados1 = time.strftime("%s-01-01" %ano)
range_feriados2 = time.strftime("%s-12-31" %ano)


feriados = holidays.Brazil()




for feriado in feriados[range_feriados1: range_feriados2]:
    feriado = str(feriado)
    date = QDate(int(feriado[0:4]),int(feriado[5:7]),int(feriado[8:10]))
    feriado = ("%s-%s-%s" %(date.year(), date.month(), date.day()))
    diasFeriados.append(feriado)




dia_verify = time.strftime("%Y-%m-%d")

ph = PasswordHasher()



dbestoque = mysql.connector.connect(
        host=hostname,
        user = 'Sistema',
        passwd = '',
        database='estoque'
)
cursor = dbestoque.cursor()



cursor.execute('''CREATE DATABASE IF NOT EXISTS estoque''')


cursor.execute('''CREATE TABLE IF NOT EXISTS produtos(
                    Nome MEDIUMTEXT NOT NULL,
                    Quantidade INTEGER NOT NULL,
                    Preco FLOAT NOT NULL,
                    Id TEXT NOT NULL,
                    Classe Text NOT NULL,
                    QuantidadeMin INTEGER NOT NULL)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS categorias(
                    Categoria TEXT NOT NULL)''')

cursor.execute(''' CREATE TABLE IF NOT EXISTS televisao(
                    Tvs LONGTEXT NOT NULL)''')

cursor.execute(''' CREATE TABLE IF NOT EXISTS Marcas_db(
                    Marca TEXT NOT NULL)''')

cursor.execute(''' CREATE TABLE IF NOT EXISTS produtos_vendidos(
                    Id TEXT NOT NULL,
                    Nome MEDIUMTEXT NOT NULL,
                    Quantidade INTEGER NOT NULL,
                    PrecoUnit FLOAT NOT NULL,
                    PrecoTotal FLOAT NOT NULL,
                    Data DATETIME DEFAULT CURRENT_TIMESTAMP,
                    Pagamento TEXT NOT NULL
)''')

cursor.execute(''' CREATE TABLE IF NOT EXISTS caixa_dia(
                    ValorDia FLOAT NOT NULL,
                    Data DATETIME DEFAULT CURRENT_TIMESTAMP,
                    Pagamento TEXT NOT NULL
)''')

cursor.execute(''' CREATE TABLE IF NOT EXISTS caixa_mes(
                    ValorMes FLOAT NOT NULL,
                    Data DATETIME DEFAULT CURRENT_TIMESTAMP,
                    Pagamento TEXT NOT NULL
)''')

cursor.execute(''' CREATE TABLE IF NOT EXISTS qtde_prod_vendidos(
                    Nome MEDIUMTEXT NOT NULL,
                    Quantidade INTEGER NOT NULL,
                    PrecoTotal FLOAT NOT NULL,
                    Data DATETIME DEFAULT CURRENT_TIMESTAMP
)''')

cursor.execute(''' CREATE TABLE IF NOT EXISTS saida(
                    Nome MEDIUMTEXT NOT NULL,
                    PrecoTotal FLOAT NOT NULL,
                    Data DATETIME DEFAULT CURRENT_TIMESTAMP
)''')

cursor.execute(''' CREATE TABLE IF NOT EXISTS config(
                        Empresa MEDIUMTEXT NOT NULL)''')


cursor.execute(''' CREATE TABLE IF NOT EXISTS users(
                        Nome MEDIUMTEXT NOT NULL,
                        Username MEDIUMTEXT NOT NULL,
                        Password varchar(98) NOT NULL,
                        Perm_Add BOOLEAN DEFAULT false,
                        Perm_Del BOOLEAN DEFAULT false,
                        Perm_Saida BOOLEAN DEFAULT false,
                        Perm_Manu BOOLEAN DEFAULT false,
                        Perm_FecharCaixa BOOLEAN DEFAULT false,
                        Perm_Exib BOOLEAN DEFAULT false,
                        Perm_Dia BOOLEAN DEFAULT false,
                        Perm_Cancelar BOOLEAN DEFAULT false,
                        Perm_Caixa BOOLEAN DEFAULT false,
                        admin BOOLEAN DEFAULT false)''')

def readAdmin():
    cursor.execute('SELECT * FROM users')
    data = cursor.fetchall()
    dbestoque.commit()
    if(data != []):
        return data[0]

def readAllUsers():
    cursor.execute('SELECT * FROM users')
    data = cursor.fetchall()
    dbestoque.commit()
    return data


def readUsers(user):
    cursor.execute('SELECT * FROM users WHERE Username=%s', [user])
    data = cursor.fetchall()
    dbestoque.commit()
    return data

def InserirAdmin():
    if(readAdmin() == None):
        cursor.execute('INSERT INTO users (Nome,Username,Password,Perm_Add,Perm_Del,Perm_Saida,Perm_Manu,Perm_FecharCaixa,Perm_Exib,Perm_Dia,Perm_Cancelar,Perm_Caixa,admin) VALUES("Administrador","loja",%s,true,true,true,true,true,true,true,true,true,true)', [ph.hash('adminLoja')])
        dbestoque.commit()
        
InserirAdmin()

listaUsuarioAtual = []
user_antigo = []


def readPermissoes(user):
    listaUsuarioAtual.clear()
    cursor.execute('SELECT * FROM users WHERE Username=%s', [user])
    data = cursor.fetchall()
    dbestoque.commit()
    x = 0
    for i in data[0]:
        if (x != 2):
            listaUsuarioAtual.append(i)
        x += 1



def InserirUsuario(Nome,username,password,Perm_Add,Perm_Del,Perm_Saida,Perm_Manu,Perm_FecharCaixa,Perm_Exib,Perm_Dia,Perm_Cancelar,Perm_Caixa):
    cursor.execute('INSERT INTO users (Nome,Username,Password,Perm_Add,Perm_Del,Perm_Saida,Perm_Manu,Perm_FecharCaixa,Perm_Exib,Perm_Dia,Perm_Cancelar,Perm_Caixa) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', [Nome,username,password,Perm_Add,Perm_Del,Perm_Saida,Perm_Manu,Perm_FecharCaixa,Perm_Exib,Perm_Dia,Perm_Cancelar,Perm_Caixa])
    dbestoque.commit()

def UpdateUsuario(old_user,Nome,username,password,Perm_Add,Perm_Del,Perm_Saida,Perm_Manu,Perm_FecharCaixa,Perm_Exib,Perm_Dia,Perm_Cancelar,Perm_Caixa):
    if(password != ''):
        cursor.execute('UPDATE users SET Nome=%s,Username=%s,Password=%s,Perm_Add=%s,Perm_Del=%s,Perm_Saida=%s,Perm_Manu=%s,Perm_FecharCaixa=%s,Perm_Exib=%s,Perm_Dia=%s,Perm_Cancelar=%s,Perm_Caixa=%s WHERE Username=%s', [Nome,username,ph.hash(password),Perm_Add,Perm_Del,Perm_Saida,Perm_Manu,Perm_FecharCaixa,Perm_Exib,Perm_Dia,Perm_Cancelar,Perm_Caixa,old_user])
    else:
        cursor.execute('UPDATE users SET Nome=%s,Username=%s,Perm_Add=%s,Perm_Del=%s,Perm_Saida=%s,Perm_Manu=%s,Perm_FecharCaixa=%s,Perm_Exib=%s,Perm_Dia=%s,Perm_Cancelar=%s,Perm_Caixa=%s WHERE Username=%s', [Nome,username,Perm_Add,Perm_Del,Perm_Saida,Perm_Manu,Perm_FecharCaixa,Perm_Exib,Perm_Dia,Perm_Cancelar,Perm_Caixa,old_user])
    dbestoque.commit()

def updateData(Nome,user,password,user_old):
    cursor.execute('UPDATE users SET Nome=%s,Username=%s,Password=%s WHERE Username=%s', [Nome,user,password,user_old])
    dbestoque.commit()


def readLogo():
    cursor = dbestoque.cursor()
    cursor.execute('SELECT Empresa FROM config')
    data = cursor.fetchone()
    dbestoque.commit()
    if(data != None):
        return data[0]
    else:
        return "Logo"


def read_task():
    cursor = dbestoque.cursor()
    cursor.execute('SELECT * FROM produtos')
    data = cursor.fetchall()
    dbestoque.commit()
    return data


def read_vendidos_mes(ano,mes):
    cursor = dbestoque.cursor()
    cursor.execute('SELECT * FROM qtde_prod_vendidos WHERE Data LIKE %s', ['%'+ano+"-"+mes+'%'])
    data = cursor.fetchall()
    dbestoque.commit()
    return data

def read_vendidos_pagamento(dia,Pagamento):
    cursor = dbestoque.cursor()
    cursor.execute('SELECT * FROM produtos_vendidos WHERE Data LIKE %s AND Pagamento=%s', ['%'+dia+'%',Pagamento])
    data = cursor.fetchall()
    dbestoque.commit()
    return data


def read_saida(dia):
    cursor = dbestoque.cursor()
    cursor.execute('SELECT * FROM saida WHERE Data LIKE %s', ['%'+dia+'%'])
    data = cursor.fetchall()
    dbestoque.commit()
    return data


def read_vendidos_ambos(dia):
    cursor = dbestoque.cursor()
    cursor.execute('SELECT * FROM produtos_vendidos WHERE Data LIKE %s', ['%'+dia+'%'])
    data = cursor.fetchall()
    dbestoque.commit()
    return data

def read_saida(dia):
    cursor = dbestoque.cursor()
    cursor.execute('SELECT * FROM saida WHERE Data LIKE %s', ['%'+dia+'%'])
    data = cursor.fetchall()
    dbestoque.commit()
    return data


def read_caixa_mes(mes):
    cursor = dbestoque.cursor()
    cursor.execute('SELECT * FROM caixa_dia WHERE Pagamento="Total" and Data LIKE %s', ['%-'+mes+'-%'])
    data = cursor.fetchall()
    dbestoque.commit()
    return data



def read_caixa(dia,Pagamento):
    cursor = dbestoque.cursor()
    cursor.execute('SELECT * FROM caixa_dia WHERE Data LIKE %s and Pagamento=%s', ['%'+dia+'%',Pagamento])
    data = cursor.fetchall()
    dbestoque.commit()
    return data

def get_value_mounth(ano,mes):
    cursor = dbestoque.cursor()
    cursor.execute('SELECT ValorMes FROM caixa_mes WHERE Data LIKE %s',['%'+ano+"-"+mes+'-%'])
    data = cursor.fetchall()
    dbestoque.commit()
    if data == []:
        return [] #preguiça de pensar muito
    else:
        return data

def read_quantidade(Nome):
    cursor = dbestoque.cursor()
    cursor.execute('SELECT Quantidade,QuantidadeMin FROM produtos WHERE Nome=%s', [Nome])
    data = cursor.fetchall()
    dbestoque.commit()
    return data[0]



def read_caixa_total(ano,mes,pagamento):
    cursor = dbestoque.cursor()
    cursor.execute('SELECT * FROM caixa_mes WHERE Data LIKE %s AND Pagamento=%s',['%'+ano+"-"+mes+'-%',pagamento])
    data = cursor.fetchall()
    dbestoque.commit()
    return data

def filtro(Nome):
    cursor = dbestoque.cursor()
    cursor.execute('SELECT * FROM produtos WHERE Nome LIKE %s', ['%'+Nome+'%'])
    data = cursor.fetchall()
    dbestoque.commit()
    return data

def readTopVendidos(ano,mes):
    cursor.execute('SELECT * FROM qtde_prod_vendidos WHERE Data LIKE %s ORDER BY Quantidade DESC LIMIT 10',['%'+ano+'-'+mes+'-%'])
    data = cursor.fetchall()
    dbestoque.commit()
    return data

def readTopVendidosAll(ano,mes):
    cursor.execute('SELECT * FROM qtde_prod_vendidos WHERE Data LIKE %s ORDER BY Quantidade DESC',['%'+ano+'-'+mes+'-%'])
    data = cursor.fetchall()
    dbestoque.commit()
    return data

def readManutencoes(dia):
    cursor.execute('SELECT * FROM produtos_vendidos WHERE Id=%s and Data LIKE %s', ['0','%'+dia+'%'])
    data = cursor.fetchall()
    dbestoque.commit()
    return data



def deleta(x):
    cursor.execute('DELETE FROM produtos WHERE Nome=%s', (x,))
    dbestoque.commit()

def updateCaixa(ValorDia, dia, Pagamento):
    cursor.execute('''update caixa_dia set ValorDia=%s where Data LIKE %s and Pagamento=%s''', [ValorDia,'%'+dia+'%',Pagamento])
    dbestoque.commit()

def updateCaixaMes(valor, dia,pagamento):
    cursor.execute('''update caixa_mes set ValorMes=%s where Data LIKE %s AND Pagamento=%s''', [valor,'%'+dia+'%',pagamento])
    dbestoque.commit()

def updateQtdVendidos(Nome,Quantidade,PrecoTotal):
    cursor.execute('''UPDATE qtde_prod_vendidos set Quantidade=Quantidade+%s,PrecoTotal=PrecoTotal+%s WHERE Nome=%s''', [Quantidade,PrecoTotal,Nome])
    dbestoque.commit()

def updateSaidaDia(Price,dia,Pagamento):
    cursor.execute('''update caixa_dia set ValorDia=%s where Data LIKE %s AND Pagamento=%s''', [Price,'%'+dia+'%',Pagamento])

def escreve(Nome, Quantidade,QuantidadeMin, Preco, Id, Classe):
    cursor.execute(''' INSERT INTO produtos (Nome, Quantidade, Preco, Id, Classe,QuantidadeMin) VALUES(%s, %s,%s, %s, %s, %s)''', [Nome, Quantidade, Preco, Id, Classe,QuantidadeMin])
    dbestoque.commit()

def escreveNomeEmpresa(Nome):
    cursor.execute('''INSERT INTO config (Empresa) VALUES(%s)''', [Nome])
    dbestoque.commit()

def escreveVenda(Id, Nome, Quantidade, PrecoUnit, PrecoTotal, Pagamento):
    cursor.execute(''' INSERT INTO produtos_vendidos (Id, Nome, Quantidade, PrecoUnit, PrecoTotal, Pagamento) VALUES(%s, %s, %s, %s, %s, %s)''', [Id, Nome, Quantidade, PrecoUnit, PrecoTotal, Pagamento])
    dbestoque.commit()

def escreveVendaData(Id, Nome, Quantidade, PrecoUnit, PrecoTotal, dia, Pagamento):
    cursor.execute(''' INSERT INTO produtos_vendidos (Id, Nome, Quantidade, PrecoUnit, PrecoTotal, Data, Pagamento) VALUES(%s, %s, %s, %s, %s, %s, %s)''', [Id, Nome, Quantidade, PrecoUnit, PrecoTotal, dia, Pagamento])
    dbestoque.commit()

def escreveCaixaDia(VendasDia, dia,Pagamento):
    cursor.execute(''' INSERT INTO caixa_dia (ValorDia, Data, Pagamento) VALUES(%s, %s, %s)''', [VendasDia,dia,Pagamento])
    dbestoque.commit()

def escreveCaixaMes(ValorMes, dia,Pagamento):
    cursor.execute(''' INSERT INTO caixa_mes (ValorMes, Data,Pagamento) VALUES(%s, %s,%s)''', [ValorMes,dia,Pagamento])
    dbestoque.commit()

def escreve_class(Categoria):
    cursor.execute(''' INSERT INTO categorias (Categoria) VALUES(%s)''',[Categoria])
    dbestoque.commit()

def escreveSaidaDia(Nome,PrecoTotal,dia):
    cursor.execute(''' INSERT INTO saida (Nome,PrecoTotal,Data) VALUES(%s,%s,%s)''', [Nome,PrecoTotal,dia])
    dbestoque.commit()

def escreveManutencao(Desc,price,Pagamento):
    cursor.execute(''' INSERT INTO produtos_vendidos (Id, Nome, Quantidade, PrecoUnit, PrecoTotal, Pagamento) VALUES(%s, %s, %s, %s, %s, %s)''', ["0", Desc, "1", price, price,Pagamento])
    dbestoque.commit()

def escreveQtdVendidos(Nome,Quantidade,PrecoTotal):
    cursor.execute('''INSERT INTO qtde_prod_vendidos (Nome,Quantidade,PrecoTotal) VALUES(%s,%s,%s)''', [Nome,Quantidade,PrecoTotal])
    dbestoque.commit()
def Editar(Id, Nome, Quantidade, Preco, Classe, p):
    cursor.execute('''update produtos set Nome=%s,Quantidade=%s,Preco=%s,Id=%s, Classe=%s where Nome=%s''', [Nome, Quantidade, Preco,Id, Classe,p])
    dbestoque.commit()

def ReductStock(Quantidade,Nome):
    cursor.execute('''update produtos set Quantidade=Quantidade-%s where Nome=%s''', [Quantidade,Nome])
    dbestoque.commit()

def AumentStock(Quantidade,Nome):
    cursor.execute('''update produtos set Quantidade=Quantidade+%s where Nome=%s''', [Quantidade,Nome])
    dbestoque.commit()

def updateNomeEmpresa(Nome):
    cursor.execute('''update config set Empresa=%s''', [Nome])
    dbestoque.commit()


def AumentVendidos(Quantidade,Preco,Nome ,Pagamento):
    cursor.execute('''update produtos_vendidos set Quantidade=Quantidade+%s,PrecoTotal=PrecoTotal+%s where Nome=%s and Pagamento=%s''', [Quantidade,Preco,Nome,Pagamento])
    dbestoque.commit()

def ReductVendidos(Quantidade,Preco, Nome,Pagamento):
    cursor.execute('''update produtos_vendidos set Quantidade=Quantidade-%s,PrecoTotal=PrecoTotal-%s where Nome=%s and Pagamento=%s''', [Quantidade,Preco,Nome,Pagamento])
    dbestoque.commit()

def ReductVendidosQtd(Nome,Quantidade,PrecoTotal):
    cursor.execute('''update qtde_prod_vendidos set Quantidade=Quantidade-%s,PrecoTotal=PrecoTotal-%s where Nome=%s''', [Quantidade,PrecoTotal,Nome])
    dbestoque.commit()

def DeletarVenda(Nome,Pagamento):
    cursor.execute('''DELETE FROM produtos_vendidos where Nome=%s and Pagamento=%s''', [Nome,Pagamento])
    dbestoque.commit()

def DeletarSaida(Nome,dia):
    cursor.execute('''DELETE FROM saida where Nome=%s and Data LIKE %s''', [Nome,'%'+dia+'%'])
    dbestoque.commit()




def Class():
    cursor = dbestoque.cursor()
    cursor.execute('SELECT Categoria FROM categorias')
    data = cursor.fetchall()
    dbestoque.commit
    return data

def login(user,senha):
    cursor.execute('SELECT Password from users WHERE Username=%(Username)s', {'Username':user})
    data = cursor.fetchone()
    dbestoque.commit()
    if(data == None):
        home.labelError.setText("Senha ou Login Invalido")
        home.lineEditPasswd.clear()
    else:
        senhaHash = data[0]
        try:
            if(ph.verify(senhaHash,senha)):
                return True
        except VerifyMismatchError:
            return False
    




########################################################################
########################################################################
########################################################################


def MesAnterior():
    if(int(time.strftime('%m')) == 1):
        mes = 12
    else:
        mes = int(time.strftime('%m'))-1
    
    if int(mes) <= 9:
        mes = '0'+str(mes)
    mes = str(mes)
    return mes

def CaixaMes():
    mes = MesAnterior()

    lista = []
    soma = 0
    ano = time.strftime("%Y")

    if(time.strftime('%m') == '01'):
        ano = str(int(time.strftime("%Y"))-1)

    metodos = ["Total","Dinheiro","Cartão/Pix","Saida"]

    dia = str(ano)+"-"+str(mes)
    
    for i in metodos:
        for f in read_caixa(dia,i):
            lista.append(f[1])
            soma += float(f[0])

        if soma != 0:
            if read_caixa_total(ano,mes,i) == []:
                escreveCaixaMes(soma, str('%s-%s-%s' %(ano,mes,'01')),i)
            else:
                updateCaixaMes(soma, str('%s-%s-%s' %(ano,mes,'01')),i)
        soma = 0


    dias = QDate(int(ano),int(mes),1)

    diasMes = dias.daysInMonth()
    d = 1


    
    
    for i in range(diasMes):
        diaSemana = QDate(int(ano),int(mes),d)
        diaSemana = diaSemana.dayOfWeek()

        if str("datetime.datetime(%s, %s, %s, 0, 0)"%(ano,int(mes),str(d))) not in str(lista):
            if int(diaSemana) != 7 and str("%s-%s-%s"%(ano,int(mes),str(d))) not in diasFeriados:
                diasVazios.append(str('%s-%s-%s' %(ano,mes,str(d))))
                
        d += 1

   


t = threading.Thread(target=CaixaMes, name='caixa')
t.start()
    



def TelaAdd():

    add.show()
    home.close()
    
    add.showMaximized()


    add.tableWidgetAdd.setColumnCount(5)

    AtualizarTableAdd()
    print(listaUsuarioAtual[2])

    if(listaUsuarioAtual[2] != 1):
        add.btnAdd.blockSignals(True)
        add.btnAdd.setStyleSheet("background-color: rgb(232, 213, 0);")
    if(listaUsuarioAtual[3] != 1):
        add.btnDeletar.blockSignals(True)
        add.btnDeletar.setStyleSheet("background-color: rgb(232, 213, 0);")

    #Remover Produtos
def AtualizarTableAdd():

    linhas = 0

    while(add.tableWidgetAdd.rowCount() > 0):
        add.tableWidgetAdd.removeRow(0)
    

    for i in read_task():

        add.tableWidgetAdd.insertRow(linhas)
        add.tableWidgetAdd.setItem(linhas,0,QTableWidgetItem(str(i[3])))
        add.tableWidgetAdd.setItem(linhas,1,QTableWidgetItem(str(i[0])))
        add.tableWidgetAdd.setItem(linhas,2,QTableWidgetItem(str(i[1])))
        add.tableWidgetAdd.setItem(linhas,3,QTableWidgetItem(str(i[2])))
        add.tableWidgetAdd.setItem(linhas,4,QTableWidgetItem(str(i[4])))
        add.tableWidgetAdd.setRowHeight(linhas,20)
        linhas+=1
    
    

    add.tableWidgetAdd.setColumnWidth(0,150)
    add.tableWidgetAdd.setColumnWidth(1,450)
    add.tableWidgetAdd.setColumnWidth(2,150)
    add.tableWidgetAdd.setColumnWidth(3,150)
    add.tableWidgetAdd.setColumnWidth(4,150)

    add.tableWidgetAdd.setHorizontalHeaderLabels(('Id', 'Nome', 'Quantidade', 'Preço', 'Classe'))

    add.tableWidgetAdd.setStyleSheet('QTableView {selection-background-color:blue}')

    add.tableWidgetAdd.verticalHeader().setVisible(False)
    add.tableWidgetAdd.setEditTriggers(QAbstractItemView.NoEditTriggers)
    add.tableWidgetAdd.setSelectionBehavior(QAbstractItemView.SelectRows)
    add.tableWidgetAdd.setSelectionMode(QAbstractItemView.SingleSelection)
    add.tableWidgetAdd.setFont(QtGui.QFont('Arial Rounded MT Bold',12))


    add.tableWidgetAdd.selectionModel().selectionChanged.connect(selection)



def AtualizarTableDesconto(lista):

    popup.tableWidgetDesconto.setColumnCount(4)

    linhas = 0

    while(popup.tableWidgetDesconto.rowCount() > 0):
        popup.tableWidgetDesconto.removeRow(0)

    for i in lista:
        

        popup.tableWidgetDesconto.insertRow(linhas)
        popup.tableWidgetDesconto.setItem(linhas,0,QTableWidgetItem(str(i[1])))
        popup.tableWidgetDesconto.setItem(linhas,1,QTableWidgetItem(str(i[2])))
        popup.tableWidgetDesconto.setItem(linhas,2,QTableWidgetItem(str(i[3])))
        popup.tableWidgetDesconto.setItem(linhas,3,QTableWidgetItem(str(i[4])))
        popup.tableWidgetDesconto.setRowHeight(linhas,20)
        linhas+=1
    
    

    popup.tableWidgetDesconto.setColumnWidth(0,450)
    popup.tableWidgetDesconto.setColumnWidth(1,100)
    popup.tableWidgetDesconto.setColumnWidth(2,100)
    popup.tableWidgetDesconto.setColumnWidth(3,100)

    popup.tableWidgetDesconto.setHorizontalHeaderLabels(('Nome', 'Quantidade', 'Preço Unidade', 'Preço Total'))

    popup.tableWidgetDesconto.setStyleSheet('QTableView {selection-background-color:blue}')

    popup.tableWidgetDesconto.verticalHeader().setVisible(False)
    popup.tableWidgetDesconto.setEditTriggers(QAbstractItemView.NoEditTriggers)
    popup.tableWidgetDesconto.setSelectionBehavior(QAbstractItemView.SelectRows)
    popup.tableWidgetDesconto.setSelectionMode(QAbstractItemView.SingleSelection)
    popup.tableWidgetDesconto.setFont(QtGui.QFont('Arial Rounded MT Bold',12))


    popup.tableWidgetDesconto.selectionModel().selectionChanged.connect(selectionDesconto)


def AtualizarTableCaixa(dia, Pagamento):

    caixa.tableWidgetProd.setColumnCount(5)

    linhas = 0

    while(caixa.tableWidgetProd.rowCount() > 0):
        caixa.tableWidgetProd.removeRow(0)
    
    if(Pagamento == 'Ambos'):
        read = read_vendidos_ambos(dia)
    else:
        read = read_vendidos_pagamento(dia,Pagamento)
    
    for i in read:

        caixa.tableWidgetProd.insertRow(linhas)
        caixa.tableWidgetProd.setItem(linhas,0,QTableWidgetItem(str(i[0])))
        caixa.tableWidgetProd.setItem(linhas,1,QTableWidgetItem(str(i[1])))
        caixa.tableWidgetProd.setItem(linhas,2,QTableWidgetItem(str(i[2])))
        caixa.tableWidgetProd.setItem(linhas,3,QTableWidgetItem(str(i[3])))
        caixa.tableWidgetProd.setItem(linhas,4,QTableWidgetItem(str(i[4])))
        caixa.tableWidgetProd.setRowHeight(linhas,20)
        linhas+=1
    
    

    caixa.tableWidgetProd.setColumnWidth(0,40)
    caixa.tableWidgetProd.setColumnWidth(1,340)
    caixa.tableWidgetProd.setColumnWidth(2,80)
    caixa.tableWidgetProd.setColumnWidth(3,80)
    caixa.tableWidgetProd.setColumnWidth(4,80)

    caixa.tableWidgetProd.setHorizontalHeaderLabels(('Id', 'Nome', 'Quantidade', 'Preço Unidade', 'Preço Total'))

    caixa.tableWidgetProd.setStyleSheet('QTableView {selection-background-color:blue}')

    caixa.tableWidgetProd.verticalHeader().setVisible(False)
    caixa.tableWidgetProd.setEditTriggers(QAbstractItemView.NoEditTriggers)
    caixa.tableWidgetProd.setSelectionBehavior(QAbstractItemView.SelectRows)
    caixa.tableWidgetProd.setSelectionMode(QAbstractItemView.SingleSelection)
    caixa.tableWidgetProd.setFont(QtGui.QFont('Arial Rounded MT Bold',12))


    




def AtualizarTableProdDay(Pagamento):

    venda.tableWidgetProd.setColumnCount(6)

    linhas = 0

    while(venda.tableWidgetProd.rowCount() > 0):
        venda.tableWidgetProd.removeRow(0)


    if(Pagamento =='Ambos'):
        read = read_vendidos_ambos(dia)
    else:
        read = read_vendidos_pagamento(dia,Pagamento)
    
    for i in read:

        venda.tableWidgetProd.insertRow(linhas)
        venda.tableWidgetProd.setItem(linhas,0,QTableWidgetItem(str(i[0])))
        venda.tableWidgetProd.setItem(linhas,1,QTableWidgetItem(str(i[1])))
        venda.tableWidgetProd.setItem(linhas,2,QTableWidgetItem(str(i[2])))
        venda.tableWidgetProd.setItem(linhas,3,QTableWidgetItem(str(i[3])))
        venda.tableWidgetProd.setItem(linhas,4,QTableWidgetItem(str(i[4])))
        venda.tableWidgetProd.setItem(linhas,5,QTableWidgetItem(str(i[6])))
        venda.tableWidgetProd.setRowHeight(linhas,20)
        linhas+=1
    
    

    venda.tableWidgetProd.setColumnWidth(0,40)
    venda.tableWidgetProd.setColumnWidth(1,340)
    venda.tableWidgetProd.setColumnWidth(2,80)
    venda.tableWidgetProd.setColumnWidth(3,80)
    venda.tableWidgetProd.setColumnWidth(4,80)
    venda.tableWidgetProd.setColumnWidth(5,50)

    venda.tableWidgetProd.setHorizontalHeaderLabels(('Id', 'Nome', 'Quantidade', 'Preço Unidade', 'Preço Total', 'Pagamento'))

    venda.tableWidgetProd.setStyleSheet('QTableView {selection-background-color:blue}')

    venda.tableWidgetProd.verticalHeader().setVisible(False)
    venda.tableWidgetProd.setEditTriggers(QAbstractItemView.NoEditTriggers)
    venda.tableWidgetProd.setSelectionBehavior(QAbstractItemView.SelectRows)
    venda.tableWidgetProd.setSelectionMode(QAbstractItemView.SingleSelection)
    venda.tableWidgetProd.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
    venda.tableWidgetProd.setFont(QtGui.QFont('Arial Rounded MT Bold',12))


    venda.tableWidgetProd.selectionModel().selectionChanged.connect(selectionDevolucao)




def AtualizarTableSaidaDia():

    venda.tableWidgetSaida.setColumnCount(2)

    linhas = 0

    while(venda.tableWidgetSaida.rowCount() > 0):
        venda.tableWidgetSaida.removeRow(0)


    read = read_saida(dia)


    for i in read:

        venda.tableWidgetSaida.insertRow(linhas)
        venda.tableWidgetSaida.setItem(linhas,0,QTableWidgetItem(str(i[0])))
        venda.tableWidgetSaida.setItem(linhas,1,QTableWidgetItem(str(i[1])))

        venda.tableWidgetSaida.setRowHeight(linhas,20)
        linhas+=1
    
    

    venda.tableWidgetSaida.setColumnWidth(1,70)
    venda.tableWidgetSaida.setColumnWidth(0,340)



    venda.tableWidgetSaida.setHorizontalHeaderLabels(('Nome', 'Preço Total'))

    venda.tableWidgetSaida.setStyleSheet('QTableView {selection-background-color:blue}')

    venda.tableWidgetSaida.verticalHeader().setVisible(False)
    venda.tableWidgetSaida.setEditTriggers(QAbstractItemView.NoEditTriggers)
    venda.tableWidgetSaida.setSelectionBehavior(QAbstractItemView.SelectRows)
    venda.tableWidgetSaida.setSelectionMode(QAbstractItemView.SingleSelection)
    venda.tableWidgetSaida.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
    venda.tableWidgetSaida.setFont(QtGui.QFont('Arial Rounded MT Bold',12))

    venda.tableWidgetSaida.selectionModel().selectionChanged.connect(selectionSaida)



def MostrarTudo():
    AtualizarTableTop10('Tudo')




def AtualizarTableTop10(flag):

    caixa.tableWidgetTop10.setColumnCount(3)

    linhas = 0

    while(caixa.tableWidgetTop10.rowCount() > 0):
        caixa.tableWidgetTop10.removeRow(0)

    ano = caixa.comboBoxAno2.currentText()

    mes = caixa.comboBoxMeses2.currentIndex()+1

    if int(mes) <= 9:
        mes = '0'+str(mes)
    mes = str(mes)

    if(flag == 'Tudo'):
        read = readTopVendidosAll(ano,mes)
    else:
        read = readTopVendidos(ano,mes)
    estoque_baixo = []

    if(read != []):
        for i in read:
            caixa.tableWidgetTop10.insertRow(linhas)
            caixa.tableWidgetTop10.setItem(linhas,0,QTableWidgetItem(str(i[0])))
            caixa.tableWidgetTop10.setItem(linhas,1,QTableWidgetItem(str(i[1])))
            caixa.tableWidgetTop10.setItem(linhas,2,QTableWidgetItem(str(i[2])))
            qtd = read_quantidade(i[0])
            if(qtd[0] <= qtd[1]):
                estoque_baixo.append(linhas)
            linhas+=1
    
    

    caixa.tableWidgetTop10.setColumnWidth(0,440)
    caixa.tableWidgetTop10.setColumnWidth(1,80)
    caixa.tableWidgetTop10.setColumnWidth(2,90)

    caixa.tableWidgetTop10.setHorizontalHeaderLabels(('Nome', 'Quantidade','Preço Total'))

    caixa.tableWidgetTop10.setStyleSheet('QTableView {selection-background-color:blue}')
    

 
    for row in estoque_baixo:
        caixa.tableWidgetTop10.item(row,0).setBackground(QtGui.QColor(255, 0, 0))
        caixa.tableWidgetTop10.item(row,1).setBackground(QtGui.QColor(255, 0, 0))
        caixa.tableWidgetTop10.item(row,2).setBackground(QtGui.QColor(255, 0, 0))


    caixa.tableWidgetTop10.verticalHeader().setVisible(False)
    caixa.tableWidgetTop10.setEditTriggers(QAbstractItemView.NoEditTriggers)
    caixa.tableWidgetTop10.setSelectionBehavior(QAbstractItemView.SelectRows)
    caixa.tableWidgetTop10.setSelectionMode(QAbstractItemView.SingleSelection)
    caixa.tableWidgetTop10.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
    caixa.tableWidgetTop10.setFont(QtGui.QFont('Arial Rounded MT Bold',12))


def AtualizarTableSaidas():

    caixa.tableWidgetSaidas.setColumnCount(2)

    linhas = 0

    while(caixa.tableWidgetSaidas.rowCount() > 0):
        caixa.tableWidgetSaidas.removeRow(0)

    ano = caixa.comboBoxAno2saida.currentText()

    mes = caixa.comboBoxMeses2saida.currentIndex()+1

    if int(mes) <= 9:
        mes = '0'+str(mes)
    mes = str(mes)

    dia = ano+"-"+mes+"-"

    read = read_saida(dia)


    if(read != []):
        for i in read:
            
            caixa.tableWidgetSaidas.insertRow(linhas)
            caixa.tableWidgetSaidas.setItem(linhas,0,QTableWidgetItem(str(i[0])))
            caixa.tableWidgetSaidas.setItem(linhas,1,QTableWidgetItem(str(i[1])))

    
    

    caixa.tableWidgetSaidas.setColumnWidth(0,440)
    caixa.tableWidgetSaidas.setColumnWidth(1,80)


    caixa.tableWidgetSaidas.setHorizontalHeaderLabels(('Nome', 'Valor'))

    caixa.tableWidgetSaidas.setStyleSheet('QTableView {selection-background-color:blue}')
    


    caixa.tableWidgetSaidas.verticalHeader().setVisible(False)
    caixa.tableWidgetSaidas.setEditTriggers(QAbstractItemView.NoEditTriggers)
    caixa.tableWidgetSaidas.setSelectionBehavior(QAbstractItemView.SelectRows)
    caixa.tableWidgetSaidas.setSelectionMode(QAbstractItemView.SingleSelection)
    caixa.tableWidgetSaidas.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
    caixa.tableWidgetSaidas.setFont(QtGui.QFont('Arial Rounded MT Bold',12))



def AtualizarTableManu():

    caixa.tableWidgetManu.setColumnCount(2)

    linhas = 0

    while(caixa.tableWidgetManu.rowCount() > 0):
        caixa.tableWidgetManu.removeRow(0)

    ano = caixa.comboBoxAnoManu.currentText()

    mes = caixa.comboBoxMesesManu.currentIndex()+1

    if int(mes) <= 9:
        mes = '0'+str(mes)
    mes = str(mes)

    dia = ano+"-"+mes+"-"

    read = readManutencoes(dia)


    if(read != []):
        for i in read:
            
            caixa.tableWidgetManu.insertRow(linhas)
            caixa.tableWidgetManu.setItem(linhas,0,QTableWidgetItem(str(i[1])))
            caixa.tableWidgetManu.setItem(linhas,1,QTableWidgetItem(str(i[4])))

    
    

    caixa.tableWidgetManu.setColumnWidth(0,440)
    caixa.tableWidgetManu.setColumnWidth(1,80)


    caixa.tableWidgetManu.setHorizontalHeaderLabels(('Nome', 'Valor'))

    caixa.tableWidgetManu.setStyleSheet('QTableView {selection-background-color:blue}')
    


    caixa.tableWidgetManu.verticalHeader().setVisible(False)
    caixa.tableWidgetManu.setEditTriggers(QAbstractItemView.NoEditTriggers)
    caixa.tableWidgetManu.setSelectionBehavior(QAbstractItemView.SelectRows)
    caixa.tableWidgetManu.setSelectionMode(QAbstractItemView.SingleSelection)
    caixa.tableWidgetManu.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
    caixa.tableWidgetManu.setFont(QtGui.QFont('Arial Rounded MT Bold',12))






def AtualizarTable2(nome):
    #estou usando a mesma função para o filtrar


    subAdd.tableWidgetGestao.setFont(QtGui.QFont('Arial Rounded MT Bold',10))

    linhas = 0

    while(subAdd.tableWidgetGestao.rowCount() > 0):
        subAdd.tableWidgetGestao.removeRow(0)
    
    

    if (nome == ''):
        read = read_task()

    elif(nome != ''):
        read = filtro(nome)


    for i in read:

        subAdd.tableWidgetGestao.insertRow(linhas)

        subAdd.tableWidgetGestao.setItem(linhas,0,QTableWidgetItem(str(i[3])))
        subAdd.tableWidgetGestao.setItem(linhas,1,QTableWidgetItem(str(i[0])))
        subAdd.tableWidgetGestao.setItem(linhas,2,QTableWidgetItem(str(i[2])))
        subAdd.tableWidgetGestao.setItem(linhas,3,QTableWidgetItem(str(i[1])))
        subAdd.tableWidgetGestao.setItem(linhas,4,QTableWidgetItem(str(i[4])))

        subAdd.tableWidgetGestao.setRowHeight(linhas,20)
        linhas+=1

    
    read = []
    

    subAdd.tableWidgetGestao.setColumnWidth(0,50)
    subAdd.tableWidgetGestao.setColumnWidth(1,200)
    subAdd.tableWidgetGestao.setColumnWidth(2,50)
    subAdd.tableWidgetGestao.setColumnWidth(3,85)
    subAdd.tableWidgetGestao.setColumnWidth(4,80)

    subAdd.tableWidgetGestao.setHorizontalHeaderLabels(('Id', 'Nome', 'Preço', 'Quantidade', 'Classe'))

    subAdd.tableWidgetGestao.setStyleSheet('QTableView {selection-background-color:blue}')

    subAdd.tableWidgetGestao.verticalHeader().setVisible(False)
    subAdd.tableWidgetGestao.setEditTriggers(QAbstractItemView.NoEditTriggers)
    subAdd.tableWidgetGestao.setSelectionBehavior(QAbstractItemView.SelectRows)
    subAdd.tableWidgetGestao.setSelectionMode(QAbstractItemView.SingleSelection)
    subAdd.tableWidgetGestao.verticalHeader().resizeSections(QHeaderView.ResizeToContents)


    


    subAdd.tableWidgetGestao.selectionModel().selectionChanged.connect(selection2)


def AtualizarTableVenda(nome):


    linhas = 0

    while(venda.tableWidgetBuscar.rowCount() > 0):
        venda.tableWidgetBuscar.removeRow(0)

    
    if (nome == ''):
        read = read_task()

    elif(nome != ''):
        read = filtro(nome)

    estoque_baixo = []

    for i in read:

        venda.tableWidgetBuscar.insertRow(linhas)
        venda.tableWidgetBuscar.setItem(linhas,0,QTableWidgetItem(str(i[3])))
        venda.tableWidgetBuscar.setItem(linhas,1,QTableWidgetItem(str(i[0])))
        venda.tableWidgetBuscar.setItem(linhas,2,QTableWidgetItem(str(i[1])))
        venda.tableWidgetBuscar.setItem(linhas,3,QTableWidgetItem(str(i[2])))
        venda.tableWidgetBuscar.setRowHeight(linhas,20)
        if(i[1] <= i[5]):
            estoque_baixo.append(linhas)
        linhas+=1
    
    

    venda.tableWidgetBuscar.setColumnWidth(0,50)
    venda.tableWidgetBuscar.setColumnWidth(1,435)
    venda.tableWidgetBuscar.setColumnWidth(2,70)
    venda.tableWidgetBuscar.setColumnWidth(3,50)


    venda.tableWidgetBuscar.setHorizontalHeaderLabels(('Id', 'Nome', 'Quantidade', 'Preço'))

    venda.tableWidgetBuscar.setStyleSheet('QTableView {selection-background-color:blue}')

     
    for row in estoque_baixo:
        venda.tableWidgetBuscar.item(row,0).setBackground(QtGui.QColor(255, 0, 0,170))
        venda.tableWidgetBuscar.item(row,1).setBackground(QtGui.QColor(255, 0, 0,170))
        venda.tableWidgetBuscar.item(row,2).setBackground(QtGui.QColor(255, 0, 0,170))
        venda.tableWidgetBuscar.item(row,3).setBackground(QtGui.QColor(255, 0, 0,170))


    venda.tableWidgetBuscar.verticalHeader().setVisible(False)
    venda.tableWidgetBuscar.setEditTriggers(QAbstractItemView.NoEditTriggers)
    venda.tableWidgetBuscar.setSelectionBehavior(QAbstractItemView.SelectRows)
    venda.tableWidgetBuscar.setSelectionMode(QAbstractItemView.SingleSelection)
    venda.tableWidgetBuscar.setFont(QtGui.QFont('Arial Rounded MT Bold',10))


    venda.tableWidgetBuscar.selectionModel().selectionChanged.connect(selectionVenda)



def AtualizarTableUser():

    telaUsers.tableWidgetUsers.setColumnCount(2)
    linhas = 0

    while(telaUsers.tableWidgetUsers.rowCount() > 0):
        telaUsers.tableWidgetUsers.removeRow(0)

    read = readAllUsers()

    for i in read:

        telaUsers.tableWidgetUsers.insertRow(linhas)
        telaUsers.tableWidgetUsers.setItem(linhas,0,QTableWidgetItem(str(i[0])))
        telaUsers.tableWidgetUsers.setItem(linhas,1,QTableWidgetItem(str(i[1])))
        telaUsers.tableWidgetUsers.setRowHeight(linhas,20)

    
    

    telaUsers.tableWidgetUsers.setColumnWidth(0,370)
    telaUsers.tableWidgetUsers.setColumnWidth(1,100)



    telaUsers.tableWidgetUsers.setHorizontalHeaderLabels(('Nome', 'Username'))

    telaUsers.tableWidgetUsers.setStyleSheet('QTableView {selection-background-color:blue}')



    telaUsers.tableWidgetUsers.verticalHeader().setVisible(False)
    telaUsers.tableWidgetUsers.setEditTriggers(QAbstractItemView.NoEditTriggers)
    telaUsers.tableWidgetUsers.setSelectionBehavior(QAbstractItemView.SelectRows)
    telaUsers.tableWidgetUsers.setSelectionMode(QAbstractItemView.SingleSelection)
    telaUsers.tableWidgetUsers.setFont(QtGui.QFont('Arial Rounded MT Bold',10))
    telaUsers.tableWidgetUsers.verticalHeader().resizeSections(QHeaderView.ResizeToContents)


    telaUsers.tableWidgetUsers.selectionModel().selectionChanged.connect(selectionUser)



def selection(selected):
    selecionados.clear()
    for i in selected.indexes():
        selecionado = add.tableWidgetAdd.item(i.row(),i.column()).text()
        selecionados.append(selecionado)
    


def selectionUser(selected):
    
    selecionadoUser.clear()
    for i in selected.indexes():
        selecionado = telaUsers.tableWidgetUsers.item(i.row(),i.column()).text()
        selecionadoUser.append(selecionado)
    

selecionadoUser = []
selecionados = []
selecionados2 = []
selecionados3 = []
selecionados4 = []
selecionados5 = []
selecionados6 = []

def selectionDesconto(selected):


    selecionados5.clear()
    for i in selected.indexes():
        selecionado = popup.tableWidgetDesconto.item(i.row(),i.column()).text()
        selecionados5.append(selecionado)
    

def selectionVenda(selected):


    selecionados3.clear()
    for i in selected.indexes():
        selecionado = venda.tableWidgetBuscar.item(i.row(),i.column()).text()
        selecionados3.append(selecionado)
    

def selectionDevolucao(selected):


    selecionados4.clear()
    for i in selected.indexes():
        selecionado = venda.tableWidgetProd.item(i.row(),i.column()).text()
        selecionados4.append(selecionado)

def selectionSaida(selected):


    selecionados6.clear()
    for i in selected.indexes():
        selecionado = venda.tableWidgetSaida.item(i.row(),i.column()).text()
        selecionados6.append(selecionado)


def selection2(selected):

    subAdd.comboBox.clear()
    
    categoria = Class()
    newCategoria = []
    contagem = 0
    for i in categoria:
    
        i = i[contagem]
        newCategoria.append(i)
        count =+ 1

    subAdd.comboBox.addItems(newCategoria)

    selecionados2.clear()


    for i in selected.indexes():
        selecionado = subAdd.tableWidgetGestao.item(i.row(),i.column()).text()
        selecionados2.append(selecionado)
    

    if (selecionados2 != []):

        subAdd.lineEdit_Id_2.setText(selecionados2[0])
        subAdd.lineEdit_Nome_2.setText(selecionados2[1])
        subAdd.lineEdit_Qtn_2.setText(selecionados2[3])
        subAdd.lineEdit_Preco_2.setText(selecionados2[2])
        subAdd.comboBox.setCurrentText(selecionados2[4])
        
        subAdd.lineEdit_Id_2.setReadOnly(False)
        subAdd.lineEdit_Nome_2.setReadOnly(False)
        subAdd.lineEdit_Preco_2.setReadOnly(False)
        subAdd.lineEdit_Qtn_2.setReadOnly(False)

        

    
    else:
        BlockClean()





def BlockClean():
    subAdd.lineEdit_Id_2.setReadOnly(True)
    subAdd.lineEdit_Nome_2.setReadOnly(True)
    subAdd.lineEdit_Preco_2.setReadOnly(True)
    subAdd.lineEdit_Qtn_2.setReadOnly(True)


    subAdd.lineEdit_Id_2.clear()
    subAdd.lineEdit_Nome_2.clear()
    subAdd.lineEdit_Qtn_2.clear()
    subAdd.lineEdit_Preco_2.clear()
    subAdd.comboBox.clear()

def Update():


    if(subAdd.lineEdit_Id_2.text() != ''):

        Id = subAdd.lineEdit_Id_2.text()
        Nome = subAdd.lineEdit_Nome_2.text()
        Quantidade = subAdd.lineEdit_Qtn_2.text()
        Preco = subAdd.lineEdit_Preco_2.text()
        Classe = subAdd.comboBox.currentText()


        p = selecionados2[1]


        Editar(Id, Nome, Quantidade, Preco, Classe, p)

        AtualizarTableAdd()
        AtualizarTable2('')
        BlockClean()


    
    



def Deletar(i):
    if(i.text() == 'OK'):
        x = selecionados[1]
        deleta(x)

        AtualizarTableAdd()


def showMessageBox():
    try:
        if(selecionados[1] != []):
            msg = QMessageBox()
            msg.setWindowTitle("Delete")
            msg.setText("Deseja mesmo Deletar esta item?")
            msg.setIcon(QMessageBox.Warning)
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

            msg.setDefaultButton(QMessageBox.Cancel)
            msg.buttonClicked.connect(Deletar)
            x = msg.exec_()
    except IndexError:
            msg = QMessageBox()
            msg.setWindowTitle("Error")
            msg.setText("Selecione um item primeiro")
            msg.setIcon(QMessageBox.Critical)
            msg.setStandardButtons(QMessageBox.Cancel)
            msg.setDefaultButton(QMessageBox.Cancel)
            x = msg.exec_()
def showMessageBox2():
    try:
        if(selecionado3Security[1] != []):
            msg = QMessageBox()
            msg.setWindowTitle("Delete")
            msg.setText("Deseja mesmo Deletar esta item?")
            msg.setIcon(QMessageBox.Warning)
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

            msg.setDefaultButton(QMessageBox.Cancel)
            msg.buttonClicked.connect(Deletar2)
            x = msg.exec_()
    except IndexError:
            msg = QMessageBox()
            msg.setWindowTitle("Error")
            msg.setText("Selecione um item primeiro")
            msg.setIcon(QMessageBox.Critical)
            msg.setStandardButtons(QMessageBox.Cancel)
            msg.setDefaultButton(QMessageBox.Cancel)
            x = msg.exec_()
    
def showMessageBox3():
    msg = QMessageBox()
    msg.setWindowTitle("Error")
    msg.setText("Selecione um metodo de pagamento!")
    msg.setIcon(QMessageBox.Critical)
    msg.setStandardButtons(QMessageBox.Ok)

    msg.setDefaultButton(QMessageBox.Ok)
    x = msg.exec_()
    

def Deletar2(i):
    if(i.text() == 'OK'):
        x = selecionado3Security[1]
        deleta(x)
        AtualizarTableVenda('')


def Home():
  
    
    home.show()
    add.close()
    venda.close()
    caixa.close()
    config.close()
    home.labelLogo.setText(readLogo())
    if(listaUsuarioAtual != []):
        PrimeiroNome = listaUsuarioAtual[0].split()
        home.btnConfig.setText("Ola, "+PrimeiroNome[0])

    


def Login():
    user = home.lineEditUser.text()
    passwd = home.lineEditPasswd.text()
    if(login(user,passwd) == True):
        home.frameLogin.close()
        readPermissoes(user)
        if(listaUsuarioAtual != []):
            PrimeiroNome = listaUsuarioAtual[0].split()
            home.btnConfig.setText("Ola, "+PrimeiroNome[0])
            if(listaUsuarioAtual[10] != 1):
                home.btnCaixa.blockSignals(True)
                home.btnCaixa.setStyleSheet('''color:#C03221;
                                                background-color: rgb(232, 213, 0);
                                                border-radius: 20px;
                                                border:none;
                                                font: 27px "Arial Rounded MT Bold";''')
        
    else:
        home.labelError.setText("Senha ou Login Invalido")
        home.lineEditPasswd.clear()
    

def radioChanged():
    
    if(venda.radioAmbos.isChecked()):
        AtualizarTableProdDay('Ambos')
        ValorCaixa()
    elif(venda.radioDinheiro.isChecked()):
        AtualizarTableProdDay('Dinheiro')
        ValorCaixa()
    elif(venda.radioPix.isChecked()):
        AtualizarTableProdDay('Cartão/Pix')
        ValorCaixa()
    
    LucroDia()

def radioChanged2():
    #fazer o teste com a seleçao do dia verificado no proprio radio
    dia = caixa.calendarWidget.selectedDate()
    day = dia.day()
    month = dia.month()
    if(day <= 9):
        day = ('0%d'%(dia.day()))
    if(month <= 9):
        month = ('0%d'%(dia.month()))
    global dia_caixa
    dia_caixa = "%s-%s-%s" %(dia.year(),month,day)
    
    if(caixa.radioAmbos.isChecked()):
        AtualizarTableCaixa(dia_caixa, 'Ambos')
        ValorCaixa2(dia_caixa)
    elif(caixa.radioDinheiro.isChecked()):
        AtualizarTableCaixa(dia_caixa,'Dinheiro')
        ValorCaixa2(dia_caixa)
    elif(caixa.radioPix.isChecked()):
        AtualizarTableCaixa(dia_caixa, 'Cartão/Pix')
        ValorCaixa2(dia_caixa)

def TelaCaixa():
    caixa.show()
    home.close()
    caixa.showMaximized()

    if(caixa.labelTotalMes.text() == "Valor Total do mês: "):
        caixa.btnGraph.hide()

    read_vendidos_ambos(dia)
    ano = time.strftime("%Y")

    if(time.strftime('%m')== '01'):
        ano = str(int(time.strftime("%Y"))-1)

    get = get_value_mounth(ano,MesAnterior())

    mounth_previous = caixa.calendarWidget.showPreviousMonth()
    if(mounth_previous == None):
        mounth_previous = "Dezembro"
    if get != []:
        caixa.labelCaixaMes.setText("A soma de %s: R$ %.2f" %(mounth_previous,get[0][0]))

   

    date_format = "yyyy-MM-d"
    cell_format = QtGui.QTextCharFormat()
    cell_format.setBackground(QtGui.QColor(255, 0, 0,100))
    for i in diasVazios:
        dt = QtCore.QDate.fromString(i, date_format)
        caixa.calendarWidget.setDateTextFormat(dt, cell_format)

    



def TelaConfig():
    config.show()
    home.close()
    config.labelError.clear()
    config.labelFeedback.clear()
    reg_ex = QRegExp("[A-Z,a-z,0-9,á,ã,õ,ô,ê]{1,10}[ ]{1,1}[A-Z,a-z,0-9,á,ã,õ,ô,ê]{1,10}")
    input_validator = QtGui.QRegExpValidator(reg_ex, config.lineEmpresa)
    config.lineEmpresa.setValidator(input_validator)

    if(listaUsuarioAtual[11] != 1):
        config.btnSalvar2.hide()
        config.lineEmpresa.setReadOnly(True)
        config.lineNome.setReadOnly(True)
        config.btnNext.hide()
        config.btnPrevious.hide()
        config.labelPageAtual.hide()

    config.lineNome.setText(listaUsuarioAtual[0])
    config.lineUsername.setText(listaUsuarioAtual[1])

def Usuario():
    Nome = config.lineNomeFuncionario.text()
    username = config.lineUsernameFuncionario.text()
    password = config.linePasswordFuncionario.text()
    confirm = config.lineConfirmFuncionario.text()
    print(user_antigo)
    if(user_antigo == []):
        if(readUsers(username) == []):
            if(password == confirm and password != ''):
                InserirUsuario(Nome,username,ph.hash(password),config.checkBox.isChecked(),config.checkBox2.isChecked(),config.checkBox3.isChecked(),config.checkBox4.isChecked(),config.checkBox5.isChecked(),config.checkBox6.isChecked(),config.checkBox7.isChecked(),config.checkBox8.isChecked(),config.checkBox9.isChecked())
                config.labelFeedback.setStyleSheet('color:#00ff00')
                config.labelFeedback.setText("Dados Atualizados!")
                config.linePasswordFuncionario.clear()
                config.lineConfirmFuncionario.clear()
                config.lineNomeFuncionario.clear()
                config.lineUsernameFuncionario.clear()
            else:
                config.labelFeedback.setStyleSheet('color:red')
                config.labelFeedback.setText("Senhas não coincidem!")
                config.linePasswordFuncionario.clear()
                config.lineConfirmFuncionario.clear()
        else:
            config.labelFeedback.setStyleSheet('color:red')
            config.labelFeedback.setText("Nome de usuário ja existe!")
    
    else:
        if(password == confirm):
            UpdateUsuario(user_antigo[0],Nome,username,password,config.checkBox.isChecked(),config.checkBox2.isChecked(),config.checkBox3.isChecked(),config.checkBox4.isChecked(),config.checkBox5.isChecked(),config.checkBox6.isChecked(),config.checkBox7.isChecked(),config.checkBox8.isChecked(),config.checkBox9.isChecked())
            config.labelFeedback.setStyleSheet('color:#00ff00')
            config.labelFeedback.setText("Dados Atualizados!")
            config.linePasswordFuncionario.clear()
            config.lineConfirmFuncionario.clear()
            config.lineNomeFuncionario.clear()
            config.lineUsernameFuncionario.clear()

        else:
            config.labelFeedback.setStyleSheet('color:red')
            config.labelFeedback.setText("Senhas não coincidem!")
            config.linePasswordFunrionario.clear()
            config.lineConfirmFunrionario.clear()

    user_antigo.clear()


def TelaUsers():
    telaUsers.show()
    AtualizarTableUser()
    

def NomeEmpresa():
    Nome = config.lineEmpresa.text()
    if(Nome != ''):
        if(home.labelLogo.text() == "Logo"):
            escreveNomeEmpresa(Nome)
        else:
            updateNomeEmpresa(Nome)
    config.lineEmpresa.clear()

def AtualizarDados():
    Nome = config.lineNome.text()
    User = config.lineUsername.text()
    Password = config.linePassword.text()
    Confirm = config.lineConfirm.text()
    if(Password == Confirm and Password != ''):
        updateData(Nome,User,ph.hash(Password),listaUsuarioAtual[1])
        config.labelError.setStyleSheet('color:#00ff00')
        config.labelError.setText("Dados Atualizados!")
    else:
        config.labelError.setText('As senhas não coincidem!')

    Password = config.linePassword.clear()
    Confirm = config.lineConfirm.clear()


def SelecionarUsuario():
    if(selecionadoUser != []):
        user_antigo.clear()
        config.lineNomeFuncionario.setText(selecionadoUser[0])
        config.lineUsernameFuncionario.setText(selecionadoUser[1])
        user_antigo.append(selecionadoUser[1])
        listaUser = readUsers(selecionadoUser[1])[0]
        config.checkBox.setChecked(listaUser[3])
        config.checkBox2.setChecked(listaUser[4])
        config.checkBox3.setChecked(listaUser[5])
        config.checkBox4.setChecked(listaUser[6])
        config.checkBox5.setChecked(listaUser[7])
        config.checkBox6.setChecked(listaUser[8])
        config.checkBox7.setChecked(listaUser[9])
        config.checkBox8.setChecked(listaUser[10])
        config.checkBox9.setChecked(listaUser[11])
        telaUsers.close()




def TelaVenda():
    venda.show()
    home.close()
    venda.showMaximized()

    ValorCaixa()
    d  = QDate(int(dia[0:4]),int(dia[5:7]),int(dia[8:10]))
    venda.dateEdit.setDate(d)
    venda.tableWidgetBuscar.setColumnCount(4)
    AtualizarTableVenda('')
    radioChanged()

    if(listaUsuarioAtual[3] != 1):
        venda.btnDeletar.blockSignals(True)
        venda.btnDeletar.setStyleSheet("background-color: rgb(232, 213, 0);")
    if(listaUsuarioAtual[4] != 1):
        venda.btnSaida.blockSignals(True)
        venda.btnSaida.setStyleSheet("background-color: rgb(232, 213, 0);")
    if(listaUsuarioAtual[5] != 1):
        venda.btnManutention.blockSignals(True)
        venda.btnManutention.setStyleSheet("background-color: rgb(232, 213, 0);")
    if(listaUsuarioAtual[6] != 1):
        venda.btnFecharCaixa.blockSignals(True)
        venda.btnFecharCaixa.setStyleSheet('''background-color: rgb(232, 213, 0);
                                            border:1px solid black;
                                            color: #C03221;
                                            font: 23px "Arial Rounded MT Bold";''')
    if(listaUsuarioAtual[7] != 1):
        venda.btnExib.blockSignals(True)
        venda.btnExib.setStyleSheet("background-color: rgb(232, 213, 0);")
    if(listaUsuarioAtual[8] != 1):
        venda.btnRefresh.blockSignals(True)
    if(listaUsuarioAtual[9] != 1):
        venda.btnCancelar.blockSignals(True)
        venda.btnCancelar.setStyleSheet('''background-color: rgb(232, 213, 0);''')

def Refresh():
    d = venda.dateEdit.date()
    global dia
    day = d.day()
    month = d.month()
    if(day <= 9):
        day = ('0%d'%(d.day()))
    if(month <= 9):
        month = ('0%d'%(d.month()))

    dia = f"{d.year()}-{month}-{day}"
    AtualizarTableProdDay('Ambos')
    ValorCaixa()
    radioChanged()
    


def ValorCaixa():
    if read_caixa(dia,'Total') != []:
        if(venda.radioAmbos.isChecked()):
            read = read_caixa(dia,'Total')
            valor_final = float(read[0][0])
            metodoPag = 'total'
        elif(venda.radioDinheiro.isChecked()):
            read = read_caixa(dia,'Dinheiro')
            valor_final = float(read[0][0])
            metodoPag = 'em dinheiro'
        elif(venda.radioPix.isChecked()):
            read = read_caixa(dia,'Cartão/Pix')
            valor_final = float(read[0][0])
            metodoPag = 'no cartão'

        if read != []:
            venda.labelCaixa.setText("O valor de vendas "+metodoPag+" R$ "+str("%.2f" %(valor_final)))
    else:
        venda.labelCaixa.setText("R$ 0,00")

def ValorSaida():
    read = read_caixa(dia,'Saida')

    if read != []:
            valor_final = float(read[0][0])
            venda.labelCaixaSaida.setText("O valor de da saida R$"+str("%.2f" %(valor_final)))
    else:
        venda.labelCaixaSaida.setText("R$ 0,00")






def ValorCaixa2(dia):
    if read_caixa(dia,'Total') != []:
        try:
            saida = float(read_caixa(dia,'Saida')[0][0])
            if(caixa.radioAmbos.isChecked()):
                read = read_caixa(dia,'Total')
                valor_final = float(read[0][0])
                metodoPag = 'total'
            elif(caixa.radioDinheiro.isChecked()):
                read = read_caixa(dia,'Dinheiro')
                valor_final = float(read[0][0])
                metodoPag = 'em dinheiro'
            elif(caixa.radioPix.isChecked()):
                read = read_caixa(dia,'Cartão/Pix')
                valor_final = float(read[0][0])
                metodoPag = 'no cartão'

            if read != []:
                caixa.labelCaixa.setText("O valor de vendas "+metodoPag+" R$ "+str("%.2f" %(valor_final)))
        except IndexError:
            pass
    else:
        caixa.labelCaixa.setText("R$ 0,00")


def AutoFechamentoCaixa(read,Pagamento):
    check = read_caixa(dia,Pagamento)
    pos = 4 
    if Pagamento == 'Saida':
        pos = 1
    if check == []:
        VendasDia = 0.0
        
        for i in read:
            VendasDia += float(i[pos])
        escreveCaixaDia(VendasDia, dia, Pagamento)

    else:
        VendasDia = 0.0
        for i in read:
            
            VendasDia += float(i[pos])
        
        updateCaixa(VendasDia, dia, Pagamento)


def FecharCaixa():
    lista = [1,2,3,4]
    for i in lista:
        if(i == 1):
            read = read_vendidos_ambos(dia)
            Pagamento = 'Total'
            AutoFechamentoCaixa(read,Pagamento)
        elif(i == 2):
            read = read_vendidos_pagamento(dia, 'Dinheiro')
            Pagamento = 'Dinheiro'
            AutoFechamentoCaixa(read,Pagamento)
            
        elif(i == 3):
            read = read_vendidos_pagamento(dia, 'Cartão/Pix')
            Pagamento = 'Cartão/Pix'
            AutoFechamentoCaixa(read,Pagamento)
        
        elif(i == 4):
            read = read_saida(dia)
            Pagamento = 'Saida'
            AutoFechamentoCaixa(read,Pagamento)

            
    ValorCaixa()
    ValorSaida()


def TrocarExibicao():
    venda.tableWidgetProd.selectionModel().clearSelection()
    venda.tableWidgetSaida.selectionModel().clearSelection()
    total = venda.stackedWidget.count()-1
    atual = venda.stackedWidget.currentIndex()
    if(atual == total):
        venda.stackedWidget.setCurrentIndex(0)
    else:
        venda.stackedWidget.setCurrentIndex(atual+1)

    if(venda.stackedWidget.currentIndex() == 1):
        ValorSaida()
        AtualizarTableSaidaDia()

    elif(venda.stackedWidget.currentIndex() == 2):
        LucroDia()

def LucroDia():
    if read_caixa(dia,'Total') != []:
        try:
            saida = float(read_caixa(dia,'Saida')[0][0])
            if(venda.radioAmbos.isChecked()):
                read = read_caixa(dia,'Total')
                valor_final = float(read[0][0])
                metodoPag = 'total'
            elif(venda.radioDinheiro.isChecked()):
                read = read_caixa(dia,'Dinheiro')
                valor_final = float(read[0][0])
                metodoPag = 'em dinheiro'
            elif(venda.radioPix.isChecked()):
                read = read_caixa(dia,'Cartão/Pix')
                valor_final = float(read[0][0])
                saida = 0.0
                metodoPag = 'no cartão'

            if read != []:
                venda.labelBruto.setText("Valor Total vendido "+metodoPag+": R$ "+str("%.2f" %(valor_final)))
                venda.labelSaida.setText("-   Saídas do dia "+metodoPag+": R$ "+str("%.2f"%(saida)))
                venda.labelLucro.setText("Lucro "+metodoPag+": R$ "+str("%.2f" %(valor_final-saida)))
        except IndexError:
            pass
    else:
        venda.labelCaixa.setText("R$ 0,00")




def NextPage2():
    total = config.stackedWidget.count()-1
    atual = config.stackedWidget.currentIndex()
    if(atual == total):
        config.stackedWidget.setCurrentIndex(0)
        config.labelPageAtual.setText(str(config.stackedWidget.currentIndex()+1))
    else:
        config.stackedWidget.setCurrentIndex(atual+1)
        config.labelPageAtual.setText(str(config.stackedWidget.currentIndex()+1))

    if(config.stackedWidget.currentIndex()+1 == 1):
        config.btnEdit.hide()
        config.labelEdit.hide()
    
    if(config.stackedWidget.currentIndex()+1 == 2):
        config.btnEdit.show()
        config.labelEdit.show()


def PreviousPage2():
    total = config.stackedWidget.count()-1
    atual = config.stackedWidget.currentIndex()
    if(atual == 0):
        config.stackedWidget.setCurrentIndex(total)
        config.labelPageAtual.setText(str(config.stackedWidget.currentIndex()+1))
    else:
        config.stackedWidget.setCurrentIndex(atual-1)
        config.labelPageAtual.setText(str(config.stackedWidget.currentIndex()+1))
    
    if(config.stackedWidget.currentIndex()+1 == 1):
        config.btnEdit.hide()
        config.labelEdit.hide()

    if(config.stackedWidget.currentIndex()+1 == 2):
        config.btnEdit.show()
        config.labelEdit.show()




def NextPage():
    total = caixa.stackedWidget.count()-1
    atual = caixa.stackedWidget.currentIndex()
    if(atual == total):
        caixa.stackedWidget.setCurrentIndex(0)
        caixa.labelPageAtual.setText(str(caixa.stackedWidget.currentIndex()+1))
    else:
        caixa.stackedWidget.setCurrentIndex(atual+1)
        caixa.labelPageAtual.setText(str(caixa.stackedWidget.currentIndex()+1))

    if(caixa.stackedWidget.currentIndex()+1 == 2):
        CarregarComboMeses()

    if(caixa.stackedWidget.currentIndex()+1 == 3):
        CarregarComboMeses()

    if(caixa.stackedWidget.currentIndex()+1 == 4):
        CarregarComboMeses()
    
    if(caixa.stackedWidget.currentIndex()+1 == 5):
        CarregarComboMeses()
    


def PreviousPage():
    total = caixa.stackedWidget.count()-1
    atual = caixa.stackedWidget.currentIndex()
    if(atual == 0):
        caixa.stackedWidget.setCurrentIndex(total)
        caixa.labelPageAtual.setText(str(caixa.stackedWidget.currentIndex()+1))
    else:
        caixa.stackedWidget.setCurrentIndex(atual-1)
        caixa.labelPageAtual.setText(str(caixa.stackedWidget.currentIndex()+1))
    
    if(caixa.stackedWidget.currentIndex()+1 == 2):
        CarregarComboMeses()

    if(caixa.stackedWidget.currentIndex()+1 == 3):
        CarregarComboMeses()
    
    if(caixa.stackedWidget.currentIndex()+1 == 4):
        CarregarComboMeses()
    
    if(caixa.stackedWidget.currentIndex()+1 == 5):
        CarregarComboMeses()




def CarregarComboMeses():
    caixa.comboBoxMeses.clear()
    caixa.comboBoxAno.clear()
    caixa.comboBoxMeses2.clear()
    caixa.comboBoxAno2.clear()
    caixa.comboBoxMeses2saida.clear()
    caixa.comboBoxAno2saida.clear()
    caixa.comboBoxMesesManu.clear()
    caixa.comboBoxAnoManu.clear()
    ano = int(time.strftime("%Y"))
    meses = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]
    anos = [str(ano-1),str(ano),str(ano+1),]
    caixa.comboBoxMeses.addItems(meses)
    caixa.comboBoxAno.addItems(anos)
    caixa.comboBoxMeses2.addItems(meses)
    caixa.comboBoxAno2.addItems(anos)
    caixa.comboBoxMeses2saida.addItems(meses)
    caixa.comboBoxAno2saida.addItems(anos)
    caixa.comboBoxMesesManu.addItems(meses)
    caixa.comboBoxAnoManu.addItems(anos)



def RelatorioCaixa():
    gc.collect()
    ano = caixa.comboBoxAno.currentText()
    mes = caixa.comboBoxMeses.currentIndex()+1
    if int(mes) <= 9:
        mes = '0'+str(mes)
    mes = str(mes)

    get = get_value_mounth(ano,mes)


    if get != []:
        try:
            rotulos = ["Dinheiro","Cartão/Pix","Gastos"]
            colors = ['g','#ff7f0e','r']
            val = [float(get[1][0])-float(get[3][0]),float(get[2][0]),float(get[3][0])]

            canvas = Canvas(val,rotulos,colors)
            caixa.gridLayout_3.addWidget(canvas,0,0)
            caixa.btnGraph.show()

            caixa.labelTotalMes.setText("Valor Total do mês %s: R$ %.2f" %(caixa.comboBoxMeses.currentText(),get[0][0]))
            caixa.labelSaidaMes.setText("Valor Saída do mês %s: R$ %.2f" %(caixa.comboBoxMeses.currentText(),float(get[3][0])))
            caixa.labelSaidaMes.setStyleSheet('color:red;')
            caixa.labelLucroMes.setText("Valor Lucro do mês %s: R$ %.2f" %(caixa.comboBoxMeses.currentText(),float(get[0][0])-float(get[3][0])))
            caixa.labelLucroMes.setStyleSheet('color:green;')
            caixa.labelDinheiroMes.setText("Em dinheiro de %s:\n R$ %.2f" %(caixa.comboBoxMeses.currentText(),float(get[1][0])-float(get[3][0])))
            caixa.labelDinheiroMes.setStyleSheet('color:green;')
            caixa.labelCartaoMes.setText("No Cartão/Pix de %s:\n R$ %.2f" %(caixa.comboBoxMeses.currentText(),get[2][0]))
        except IndexError:
            caixa.labelTotalMes.setText("Erro Caixa não foi fechado corretamente!")
            caixa.labelTotalMes.setStyleSheet('color:red;')

def AbrirGraph():
    gc.collect()
    ano = caixa.comboBoxAno.currentText()
    mes = caixa.comboBoxMeses.currentIndex()+1
    if int(mes) <= 9:
        mes = '0'+str(mes)
    mes = str(mes)

    get = get_value_mounth(ano,mes)
    if get != []:
        rotulos = ["Lucro","Gastos"]
        colors = ['g','r']
        val = [(float(get[0][0])-float(get[3][0])),float(get[3][0])]

        
        canvas = Canvas(val,rotulos,colors)
        caixa.gridLayout_3.addWidget(canvas,0,0)
        caixa.btnGraph.show()







def PrecoProduto():
    PrecoTotal = float(selecionados3[3])*int(popup.spinBox.text())
    Desconto = popup.lineEditDesconto.text()
    try:
        PrecoTotal = DescontoFunction(Desconto, PrecoTotal)

        popup.labelPreco.setText(str(PrecoTotal))

        return PrecoTotal
    except ValueError:
        print("Opa deu erro")

def DescontoTotal():
    soma = 0
    soma2 = 0 #soma dos produtos que ja tem desconto
    for i in listaProdDesconto:
        Quantidade = float(i[2])
        Preco = float(i[3])
        PrecoTotal = Preco*Quantidade
        PrecoTotalCheck = float(i[4])
        if(PrecoTotal == PrecoTotalCheck):
            soma = soma+float(i[4])
        else:
            soma2 = soma2+float(i[4])


    Desconto = popup.lineEditDescontoTotal.text()
    PrecoTotal = float(soma)
    
    try:
        

        PrecoTotal = float(DescontoFunction(Desconto,PrecoTotal))+soma2
        popup.labelValorVenda.setText("R$ "+str(PrecoTotal))

    except ValueError:
        print("Opa deu erro")
    


def subTelaAdd():

        
    reg_ex = QRegExp("[0-9]{1,}[.]{1,1}[0-9]{,}")
    reg_ex_Qtn = QRegExp("[0-9]{1,}")
    input_validator = QtGui.QRegExpValidator(reg_ex, subAdd.lineEdit_Preco)
    input_validator_Qtn = QtGui.QRegExpValidator(reg_ex_Qtn, subAdd.lineEdit_Preco)
    subAdd.lineEdit_Preco.setValidator(input_validator)
    subAdd.lineEdit_Preco_2.setValidator(input_validator)
    subAdd.lineEdit_Qtn.setValidator(input_validator_Qtn)
    subAdd.lineEdit_Qtn_2.setValidator(input_validator_Qtn)

    subAdd.tabWidget.setCurrentIndex(0)

    newCategoria = AtualizarComboBox()

    subAdd.show()
    
    subAdd.comboBoxClass.addItems(newCategoria)
    
    

    subAdd.lineEdit_Id_2.setReadOnly(True)
    subAdd.lineEdit_Nome_2.setReadOnly(True)
    subAdd.lineEdit_Preco_2.setReadOnly(True)
    subAdd.lineEdit_Qtn_2.setReadOnly(True)

    



    



def Filtrar():

    nome = subAdd.lineEdit_filtro.text()
    subAdd.lineEdit_filtro.clear()




    if(nome != ''):
        AtualizarTable2(nome)
    
    else:
        AtualizarTable2('')


def Filtrar2():

    nome = subAdd.lineEdit_filtro.text()

    AtualizarTable2(nome)
    


def FiltrarVenda():
    
    nome = venda.lineEditBuscar.text()

    if(nome != ''):
        AtualizarTableVenda(nome)
    
    else:
        AtualizarTableVenda('')

    
    venda.lineEditBuscar.clear()
def FiltrarVenda2():
    
    nome = venda.lineEditBuscar.text()
    
    AtualizarTableVenda(nome)
 

    
    



selecionado3Security = selecionados3
selecionado4Security = selecionados4
selecionado5Security = selecionados5
selecionado6Security = selecionados6


def popupVenda():


    if (venda.tableWidgetBuscar.selectedItems() != []):

        reg_ex = QRegExp("[0-9]{1,}[.,%]{1,1}[0-9,%]{,}")
        input_validator = QtGui.QRegExpValidator(reg_ex, popup.lineEditDesconto)
        input_validator2 = QtGui.QRegExpValidator(reg_ex, popup.lineEditDescontoTotal)
        popup.lineEditDesconto.setValidator(input_validator)
        popup.lineEditDescontoTotal.setValidator(input_validator2)

        venda.lineEditBuscar.clear()
        popup.lineEditDesconto.clear()
        popup.show()
        AtualizarTableDesconto(listaProdDesconto)

        popup.spinBox.clear()
        popup.spinBox.setValue(1)
        popup.spinBox.setMaximum(int(selecionados3[2]))

        popup.labelNome.setText(selecionados3[1])
        popup.labelPreco.setText(selecionados3[3])
        

        selecionado3Security = selecionados3 #caso algum paçoca troca a seleção no meio da inserção da quantidade


def show_popupVenda():
    popup.show()
    AtualizarTableDesconto(listaProdDesconto)

def VerificarProdutoVendeu(Nome):

    for e,i in enumerate(listaProdDesconto):
        if Nome == i[1]:
            return e

def VerificarProdutoVendeu2(Nome, Pagamento):

    for e,i in enumerate(read_vendidos_ambos(dia)):
        if (Nome == i[1] and Pagamento == i[6]):
            return e

def VerificarProdutoVendeuMes(Nome):
    ano = time.strftime("%Y")
    retorno2 = False
    if(read_vendidos_mes(ano,time.strftime(time.strftime("%m"))) == []):
        return False
    else:
        for i in (read_vendidos_mes(ano,time.strftime(time.strftime("%m")))):
            if (Nome == i[0]):
                retorno2 = True
    
    return retorno2
            

listaProdDesconto = []


def vendaRapida():
    if popup.radioDinheiro.isChecked():
        Pagamento = 'Dinheiro'
    elif popup.radioPix.isChecked():
        Pagamento = 'Cartão/Pix'


    if dia == dia_verify:
        try:
            Quantidade = int(popup.spinBox.text())
            Id = selecionado3Security[0]
            Nome = selecionado3Security[1]
            PrecoUnit = float(selecionado3Security[3])
            PrecoTotal = PrecoProduto()
            retorno = VerificarProdutoVendeu2(Nome, Pagamento)
            if (retorno == None):
                escreveVenda(Id, Nome, Quantidade, PrecoUnit, PrecoTotal,Pagamento)
                ReductStock(Quantidade, Nome)
                if(VerificarProdutoVendeuMes(Nome) == False):
                    escreveQtdVendidos(Nome,Quantidade,PrecoTotal)
                else:
                    updateQtdVendidos(Nome,Quantidade,PrecoTotal)
            else:
                AumentVendidos(Quantidade, PrecoTotal, Nome, Pagamento)
                ReductStock(Quantidade, Nome)
                if(VerificarProdutoVendeuMes(Nome) == False):
                    escreveQtdVendidos(Nome,Quantidade,PrecoTotal)
                else:
                    updateQtdVendidos(Nome,Quantidade,PrecoTotal)
        except IndexError:
            pass
    else: 
        Quantidade = int(popup.spinBox.text())
        Id = selecionado3Security[0]
        Nome = selecionado3Security[1]
        PrecoUnit = float(selecionado3Security[3])
        PrecoTotal = PrecoProduto()
        retorno = VerificarProdutoVendeu2(Nome, Pagamento)
        if (retorno == None):
            escreveVendaData(Id, Nome, Quantidade, PrecoUnit, PrecoTotal,dia,Pagamento)
            ReductStock(Quantidade, Nome)
            if(VerificarProdutoVendeuMes(Nome) == False):
                escreveQtdVendidos(Nome,Quantidade,PrecoTotal)
            else:
                updateQtdVendidos(Nome,Quantidade,PrecoTotal)
        else:
            AumentVendidos(Quantidade, PrecoTotal, Nome, Pagamento)
            ReductStock(Quantidade, Nome)
            if(VerificarProdutoVendeuMes(Nome) == False):
                escreveQtdVendidos(Nome,Quantidade,PrecoTotal)
            else:
                
                updateQtdVendidos(Nome,Quantidade,PrecoTotal)

    radioChanged()
    AtualizarTableVenda('')

    popup.close()
    
def CountDescontados():
    count = 0
    for b in listaProdDesconto:
        Quantidade = b[2]
        PrecoTotal = b[4]
        PrecoTotalCheck = b[3]*Quantidade
        if(PrecoTotal != PrecoTotalCheck):
            count += 1
        
    return count    


def addProdVenda():
    if(listaProdDesconto != []):
        
        if popup.radioDinheiro.isChecked():
            Pagamento = 'Dinheiro'
        elif popup.radioPix.isChecked():
            Pagamento = 'Cartão/Pix'

        
        
        if dia == dia_verify:

            CountDescontados()
            
            for e,i in enumerate(listaProdDesconto):
                
                Desconto = popup.lineEditDescontoTotal.text()
                Id = i[0]
                Quantidade = i[2]
                PrecoUnit = i[3]
                PrecoTotal = i[4]
                PrecoTotalCheck = PrecoUnit*Quantidade
                Nome = i[1]
  
                retorno = VerificarProdutoVendeu2(Nome,Pagamento)
                if (retorno == None):
                    
                    if(PrecoTotalCheck == PrecoTotal):
                        PrecoTotal  = DescontoFunction2(Desconto,PrecoTotal)


                    escreveVenda(Id,Nome,Quantidade,PrecoUnit,PrecoTotal,Pagamento)
                    ReductStock(Quantidade,Nome)
                    radioChanged()
                    AtualizarTableVenda('')
                    if(VerificarProdutoVendeuMes(Nome) == False):
                        escreveQtdVendidos(Nome,Quantidade,PrecoTotal)
                    else:
                        updateQtdVendidos(Nome,Quantidade,PrecoTotal)

                else:
                    
                    if(PrecoTotalCheck == PrecoTotal):
                        PrecoTotal = DescontoFunction2(Desconto,PrecoTotal)

                    AumentVendidos(Quantidade, PrecoTotal, Nome, Pagamento)
                    ReductStock(Quantidade, Nome)
                    radioChanged()
                    AtualizarTableVenda('')
                    if(VerificarProdutoVendeuMes(Nome) == False):
                        escreveQtdVendidos(Nome,Quantidade,PrecoTotal)
                    else:
                        updateQtdVendidos(Nome,Quantidade,PrecoTotal)

        else:
            for e,i in enumerate(listaProdDesconto):
                Desconto = popup.lineEditDescontoTotal.text()
                Id = i[0]
                Nome = i[1]
                Quantidade = i[2]
                PrecoUnit = i[3]
                PrecoTotal = i[4]
                PrecoTotalCheck = PrecoUnit*Quantidade

                retorno = VerificarProdutoVendeu2(Nome, Pagamento)
                if (retorno == None):

                    if(PrecoTotal == PrecoTotalCheck):
                        PrecoTotal = DescontoFunction2(Desconto, PrecoTotal)

                    escreveVendaData(Id,Nome,Quantidade,PrecoUnit,PrecoTotal,dia,Pagamento)
                    ReductStock(Quantidade,Nome)
                    radioChanged()
                    AtualizarTableVenda('')
                    if(VerificarProdutoVendeuMes(Nome) == False):
                        escreveQtdVendidos(Nome,Quantidade,PrecoTotal)
                    else:
                        updateQtdVendidos(Nome,Quantidade,PrecoTotal)
                else:
                    if(PrecoTotal == PrecoTotalCheck):
                        PrecoTotal = DescontoFunction2(Desconto, PrecoTotal)

                    AumentVendidos(Quantidade, PrecoTotal, Nome, Pagamento)
                    ReductStock(Quantidade, Nome)
                    radioChanged()
                    AtualizarTableVenda('')
                    if(VerificarProdutoVendeuMes(Nome) == False):
                        escreveQtdVendidos(Nome,Quantidade,PrecoTotal)
                    else:
                        updateQtdVendidos(Nome,Quantidade,PrecoTotal)
        
        listaProdDesconto.clear()
        popup.labelValorVenda.setText('R$ 0,00')
        popup.lineEditDescontoTotal.clear()
        popup.close()

def DescontoFunction(Desconto, PrecoTotal):
    if('%' in Desconto):
        Desconto = Desconto.replace('%','')
        Desconto = 100-int(Desconto)
        Desconto = Desconto/100

        PrecoTotal = PrecoTotal*Desconto
        PrecoTotal = ('%.2f'%(PrecoTotal))

    
    elif(Desconto != '' and '%' not in Desconto):
        PrecoTotal = PrecoTotal-float(Desconto)
        PrecoTotal = ('%.2f'%(PrecoTotal))
    
    return PrecoTotal


def DescontoFunction2(Desconto, PrecoTotal):
    if('%' in Desconto):
        Desconto = Desconto.replace('%','')
        Desconto = 100-float(Desconto)
        Desconto = Desconto/100
        PrecoTotal = PrecoTotal*Desconto
        PrecoTotal = ('%.2f'%(PrecoTotal))
 

    elif(Desconto != '' and '%' not in Desconto):
        divisor = len(listaProdDesconto)-CountDescontados()
        Desconto = float(Desconto)/divisor
        PrecoTotal = PrecoTotal-float(Desconto)
        PrecoTotal = ('%.2f'%(PrecoTotal))

    return PrecoTotal

        

def addProdDesconto():
    if(selecionado3Security != []):
        if(popup.spinBox.text() != '0'):
            retorno = VerificarProdutoVendeu(selecionado3Security[1])


            if(retorno == None):
                Quantidade = int(popup.spinBox.text())
                Id = selecionado3Security[0]
                Nome = selecionado3Security[1]
                PrecoUnit = float(selecionado3Security[3])
                PrecoTotal = float(Quantidade*PrecoUnit)
                
                Desconto = popup.lineEditDesconto.text()
                popup.lineEditDesconto.clear()
                
                PrecoTotal = DescontoFunction(Desconto, PrecoTotal)
                

                lista = (Id,Nome,Quantidade,PrecoUnit,PrecoTotal)

                listaProdDesconto.append(lista)
                AtualizarTableDesconto(listaProdDesconto)

                AtualizarTableVenda('')
                radioChanged()

            else:
                Id = selecionado3Security[0]
                Quantidade = int(popup.spinBox.text())+listaProdDesconto[retorno][2]
                QuantidadeReduct = int(popup.spinBox.text())
                Nome = selecionado3Security[1]
                PrecoUnit = float(selecionado3Security[3])
                PrecoTotal = float(QuantidadeReduct*PrecoUnit)


                PrecoTotal = PrecoTotal+float(listaProdDesconto[retorno][4])

                Desconto = popup.lineEditDesconto.text()
                popup.lineEditDesconto.clear()
                
                PrecoTotal = DescontoFunction(Desconto ,PrecoTotal)

                listaProdDesconto[retorno] = (Id,Nome,Quantidade,PrecoUnit,PrecoTotal)
            
                AtualizarTableDesconto(listaProdDesconto)


                AtualizarTableVenda('')
                radioChanged()
            soma = 0
            for i in listaProdDesconto:
                soma = soma+float(i[4])
            
            popup.labelValorVenda.setText('R$ %.2f'%(soma))


        else:
            popup.close()


def retirarProdDesconto():
    popup3.close()
    if(selecionado5Security != []):
        retorno = VerificarProdutoVendeu(selecionado5Security[1])
        if(popup3.spinBox.text() != '0'):
            retorno = VerificarProdutoVendeu(selecionado5Security[0])
            if(popup3.spinBox.text() != selecionado5Security[1]):
                Id = selecionado5Security[0]
                Quantidade = listaProdDesconto[retorno][2]-int(popup3.spinBox.text())

                QuantidadeStock = int(popup3.spinBox.text())

                Nome = selecionado5Security[0]
                PrecoUnit = float(selecionado5Security[2])
                PrecoTotal = float(Quantidade*PrecoUnit)


                listaProdDesconto[retorno] = (Id,Nome,Quantidade,PrecoUnit,PrecoTotal)

                AumentStock(QuantidadeStock,Nome)
        
                AtualizarTableDesconto(listaProdDesconto)

                AtualizarTableVenda('')
                radioChanged()

            else:

                
                Nome = selecionado5Security[0]
                Quantidade = selecionado5Security[1]
                AumentStock(Quantidade,Nome)

                del listaProdDesconto[retorno]

                AtualizarTableDesconto(listaProdDesconto)
                AtualizarTableVenda('')
                radioChanged()
            
            soma = 0
            for i in listaProdDesconto:
                soma = soma+float(i[4])
            
            popup.labelValorVenda.setText('R$ %.2f'%(soma))

        else:
            popup.close()


def PopupManuntecao():
    popup5.show()

def PopupSaida():
    popup6.show()

def Manutencao():

    Desc = popup5.lineEditDesc.text()
    Price = popup5.lineEditPrice.text()

    try:
        if(popup5.radioDinheiro.isChecked()):
            pagamento = "Dinheiro"
        elif(popup5.radioPix.isChecked()):
            pagamento = "Cartão/Pix"
        
        escreveManutencao(Desc,Price,pagamento)
        popup5.close()
    except UnboundLocalError:
        showMessageBox3()

    radioChanged()

    popup5.lineEditDesc.clear()
    popup5.lineEditPrice.clear()
    popup5.radioDinheiro.setAutoExclusive(False)
    popup5.radioDinheiro.setChecked(False)
    popup5.radioDinheiro.setAutoExclusive(True)
    popup5.radioPix.setAutoExclusive(False)
    popup5.radioPix.setChecked(False)
    popup5.radioPix.setAutoExclusive(True)

def Saida():
    Desc = popup6.lineEditDesc.text()
    Price = popup6.lineEditPrice.text()
    if (Desc != '' and Price != ''):
        escreveSaidaDia(Desc,Price,dia)
        AtualizarTableSaidaDia()

    popup6.close()
    popup6.lineEditDesc.clear()
    popup6.lineEditPrice.clear()



 
def PopupCancelar():
    

    
    if (venda.tableWidgetProd.selectedItems() != []):

        popup2.show()


        popup2.spinBox.clear()
        popup2.spinBox.setValue(int(selecionados4[2]))

        popup2.spinBox.setMaximum(int(selecionados4[2]))

        popup2.labelNome.setText(selecionados4[1])
        

        selecionado4Security = selecionados4
    
    elif (venda.tableWidgetSaida.selectedItems() != []):
        DeletarSaida(selecionados6[0],dia)
        AtualizarTableSaidaDia()
    
def PopupCancelar2():
    if (popup.tableWidgetDesconto.selectedItems() != []):

        popup3.show()

        popup3.spinBox.clear()
        popup3.spinBox.setValue(int(selecionados5[1]))

        popup3.spinBox.setMaximum(int(selecionados5[1]))

        popup3.labelNome.setText(selecionados5[0])
        

        selecionado5Security = selecionados5



def OpFast():
    Nome = popup4.labelNome.text()
    Quantidade = popup4.spinBox.text()

    if(check == 'add'):
        AumentStock(Quantidade, Nome)
    elif(check == 'retira'):
        ReductStock(Quantidade, Nome)

    AtualizarTableVenda('')
    popup4.close()

def PopupAddFast():
    if (venda.tableWidgetBuscar.selectedItems() != []):
        
        global check
        popup4.show()

        popup4.spinBox.clear()
        popup4.labelNome.setText(selecionados3[1])
        check='add'

def PopupRemoveFast():
    if (venda.tableWidgetBuscar.selectedItems() != []):
        global check 
        popup4.show()

        popup4.spinBox.clear()

        popup4.spinBox.setMaximum(int(selecionados3[2]))

        popup4.labelNome.setText(selecionados3[1])
        check ='retira'

def Devolucao():
    if(selecionado4Security != []):
        if(popup2.spinBox.text() != '0'):
            if(popup2.spinBox.text() != selecionado4Security[2]):
                Quantidade = int(popup2.spinBox.text())
                PrecoUnit = float(selecionado4Security[3])
                PrecoTotal = Quantidade*PrecoUnit
                Nome = selecionado4Security[1]
                Pagamento = selecionado4Security[5]
                

                AumentStock(Quantidade,Nome)
                ReductVendidos(Quantidade,PrecoTotal,Nome,Pagamento)

                ReductVendidosQtd(Nome,Quantidade,PrecoTotal)

                AtualizarTableVenda('')
                radioChanged()

                popup2.close()
            else:
                Quantidade = int(popup2.spinBox.text())
                Nome = selecionado4Security[1]
                Pagamento = selecionado4Security[5]
                PrecoUnit = float(selecionado4Security[3])
                PrecoTotal = Quantidade*PrecoUnit
                ReductVendidosQtd(Nome,Quantidade,PrecoTotal)
                DeletarVenda(Nome,Pagamento)
                AumentStock(Quantidade,Nome)
                popup2.close()

                AtualizarTableVenda('')
                radioChanged()

        else:
            popup2.close()
    





def AtualizarComboBox():

    subAdd.comboBoxClass.clear()

    categoria = Class()
    newCategoria = []
    contagem = 0
    for i in categoria:
        
        i = i[contagem]
        newCategoria.append(i)
        count =+ 1
    
    return newCategoria

def abaAtual():


    if (subAdd.tabWidget.currentIndex() == 1):


        subAdd.tableWidgetGestao.setColumnCount(5)
        AtualizarTable2('')
    
    else:
        BlockClean()



def AddClass():
    addClass.show()
    addClass.btnGravar.clicked.connect(AddCategoria)
    


def AddProduto():

    
    
    if(subAdd.lineEdit_Id.text() != '' and subAdd.lineEdit_Nome.text() != ''):

        Id = subAdd.lineEdit_Id.text()
        Nome = subAdd.lineEdit_Nome.text()
        Quantidade = subAdd.lineEdit_Qtn.text()
        Preco = subAdd.lineEdit_Preco.text()
        Classe = subAdd.comboBoxClass.currentText()
        QuantidadeMin = subAdd.lineEditMin.text()
        if(QuantidadeMin == ''):
            QuantidadeMin = 5
        escreve(Nome, Quantidade,QuantidadeMin, Preco, Id, Classe)

        
        subAdd.lineEdit_Id.clear()
        subAdd.lineEdit_Nome.clear()
        subAdd.lineEdit_Qtn.clear()
        subAdd.lineEdit_Preco.clear()
        subAdd.lineEdit_Id.setFocus()


        AtualizarTableAdd()




def AddCategoria():
    if (addClass.lineEditClass.text() != ''):
        newCategoria = addClass.lineEditClass.text()
        escreve_class(newCategoria)
        addClass.lineEditClass.clear()
        addClass.close()

def Close():
    popup.close()




if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    home = loadUi('PrimeiraTela.ui')
    add = loadUi('TelaAdd.ui')
    subAdd = loadUi('subTelaAdd.ui')
    addClass = loadUi('AddClass.ui')    
    venda = loadUi('TelaVenda.ui')
    popup = loadUi('popupVenda.ui')

    popup2 = loadUi('popupCancelar.ui')
    popup3 = loadUi('popupCancelar2.ui')
    popup4 = loadUi('popup4.ui')
    popup5 = loadUi('popupManutencao.ui')
    popup6 = loadUi('popupSaida.ui')

    caixa = loadUi('TelaCaixa.ui')
    config = loadUi('TelaConfig.ui')
    telaUsers = loadUi('TabelaUsuario.ui')


    #chamada de click buttons tela add
    add.btnVoltar.clicked.connect(Home)
    
    
    add.btnAdd.clicked.connect(subTelaAdd)
    add.btnDeletar.clicked.connect(showMessageBox)
    
    #chamada de click buttons tela subAdd
    subAdd.btnFiltrar.clicked.connect(Filtrar)
    subAdd.tabWidget.currentChanged.connect(abaAtual)

    subAdd.btnAddClass.clicked.connect(AddClass)
    subAdd.btnAddClass_2.clicked.connect(AddClass)
    subAdd.btnGravar_2.clicked.connect(Update)
    subAdd.btnGravar.clicked.connect(AddProduto)
    subAdd.lineEdit_filtro.textEdited.connect(Filtrar2)
    
    
    #chamada de click buttons tela venda
    venda.btnVoltar.clicked.connect(Home)
    venda.btnBuscar.clicked.connect(FiltrarVenda)
    venda.btnVender.clicked.connect(show_popupVenda)
    venda.btnVender2.clicked.connect(popupVenda)
    venda.btnDeletar.clicked.connect(showMessageBox2)
    venda.btnCancelar.clicked.connect(PopupCancelar)
    venda.btnFecharCaixa.clicked.connect(FecharCaixa)

    venda.lineEditBuscar.textEdited.connect(FiltrarVenda2)
    
    venda.btnRefresh.clicked.connect(Refresh)
    
    venda.radioDinheiro.clicked.connect(radioChanged)
    venda.radioAmbos.clicked.connect(radioChanged)
    venda.radioPix.clicked.connect(radioChanged)


    

    venda.btnRetira.clicked.connect(PopupRemoveFast)
    venda.btnAdiciona.clicked.connect(PopupAddFast)
    venda.btnManutention.clicked.connect(PopupManuntecao)
    venda.btnSaida.clicked.connect(PopupSaida)
    venda.btnExib.clicked.connect(TrocarExibicao)


    

    #chamada de click buttons tela home
    home.btnAdd.clicked.connect(TelaAdd)
    home.btnVenda.clicked.connect(TelaVenda)
    home.btnEntrar.clicked.connect(Login)
    home.btnCaixa.clicked.connect(TelaCaixa)
    home.labelLogo.setText(readLogo())
    if(listaUsuarioAtual != []):
        PrimeiroNome = listaUsuarioAtual[0].split()
        home.btnConfig.setText("Ola, "+PrimeiroNome[0])
    home.btnConfig.clicked.connect(TelaConfig)

    #poupvenda 
    popup.btnEnviar.clicked.connect(addProdDesconto)
    popup.btnAdicionar.clicked.connect(Close)
    popup.btnVender.clicked.connect(addProdVenda)
    popup2.btnEnviar.clicked.connect(Devolucao)
    popup3.btnEnviar.clicked.connect(retirarProdDesconto)
    popup.btnRetirar.clicked.connect(PopupCancelar2)
    popup.lineEditDesconto.textEdited.connect(PrecoProduto)
    popup.spinBox.textChanged.connect(PrecoProduto)
    popup.btnVendaRapida.clicked.connect(vendaRapida)
    popup.lineEditDescontoTotal.textEdited.connect(DescontoTotal)

    #popup4
    popup4.btnEnviar.clicked.connect(OpFast)

    #popup5
    popup5.btnEnviar.clicked.connect(Manutencao)

    #popup6
    popup6.btnEnviar.clicked.connect(Saida)
    

    #chamadas do TelaCaixa
    caixa.calendarWidget.selectionChanged.connect(radioChanged2)
    caixa.btnVoltar.clicked.connect(Home)
    caixa.radioDinheiro.clicked.connect(radioChanged2)
    caixa.radioAmbos.clicked.connect(radioChanged2)
    caixa.radioPix.clicked.connect(radioChanged2)
    caixa.btnNext.clicked.connect(NextPage)
    caixa.btnPrevious.clicked.connect(PreviousPage)
    caixa.btnAtualizar.clicked.connect(RelatorioCaixa)
    caixa.btnGraph.clicked.connect(AbrirGraph)
    caixa.btnAtualizar2.clicked.connect(AtualizarTableTop10)
    caixa.btnAtualizar2saida.clicked.connect(AtualizarTableSaidas)
    caixa.btnMore.clicked.connect(MostrarTudo)
    caixa.btnAtualizarManu.clicked.connect(AtualizarTableManu)


    #config page
    config.btnEdit.hide()
    config.labelEdit.hide()
    config.btnNext.clicked.connect(NextPage2)
    config.btnPrevious.clicked.connect(PreviousPage2)
    config.btnVoltar.clicked.connect(Home)
    config.btnSalvar2.clicked.connect(NomeEmpresa)
    config.btnSalvar.clicked.connect(AtualizarDados)
    config.btnSalvarUser.clicked.connect(Usuario)
    config.btnEdit.clicked.connect(TelaUsers)
    telaUsers.btnEnviar.clicked.connect(SelecionarUsuario)

    

    Home()



    sys.exit(app.exec())

