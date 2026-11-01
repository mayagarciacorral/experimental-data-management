#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Authors
    student1 number/name: Maya Garcia 
        student1 contribution (%): 50%
        contribution description: 
            
    student2 number/name: Rita Pina
        student2 contribution (%): 50%
        contribution description:

"""

# %%
# MODULES
#

import sqlite3
import math
import matplotlib.pyplot as plt 

#CREATE TABLES
def cmd_create_tables(con:sqlite3.Connection)->None:
   """Cria duas tabelas Samples e Tests vazias e importa-as para a base de dados.
       Apaga tabelas da base de dados, caso estas existam.
       Cria duas tabelas novas:
         A tabela Tests, define cada ensaio.
           Paramêtros- indicador do ensaio(id), 
                       referência do material (mat_id),
                       ano da realização(year), 
                       temperatura inicial do material (temp_ini),
                       certificação do laboratório (certification)
        A tabela Samples, define as amostras de cada ensaio
          Paramêtros- identificador da amostra(id), 
                      identificador do ensaio (test_id),
                      tempo desde do início da exepriência até à realização da amostra (time)
                      temperatura do material quando a amostra foi realizada (temperature)
    """
   cursor=con.cursor()
   cursor.execute("DROP TABLE IF EXISTS Tests") 
   cursor.execute("DROP TABLE IF EXISTS Samples") 
   cursor.execute("""CREATE TABLE Tests 
                   (id INTEGER, mat_id VARCHAR(6), year INTEGER,
                   temp_ini REAL, certification VARCHAR(20),
                   PRIMARY KEY (id));""")
   cursor.execute(""" CREATE TABLE Samples
                   (id INTEGER, test_id INTEGER, time INTEGER, 
                   temperature REAL, PRIMARY KEY(id));""") 
   con.commit() 
   pass

#LOAD TEST
def cmd_load_test(db: sqlite3.Connection, args:str)->None:
    """Carrega dados de arquivos para a base de dados.
       Variável- nome do ficheiro,
       Ficheiro é lido linha a linha 
       Associa os dados das linhas ao paramêtros das tabelas Samples e Tests
      Os dados de cada ficheiro são inseridos na base de dados, nas respetivas tabelas
    """
    files=args.split(";" )
    cursor=db.cursor()
    for file in files: 
       with open(file, "r") as f:
           lines=f.readlines()
           id=int(lines[0].strip())
           year=int(lines[1].strip())
           mat_id=lines[2].strip()
           temp_ini=float (lines[4].strip())
           certification=lines[3].strip()
           sql1="INSERT INTO Tests VALUES(?,?,?,?,?);"
           values1=(id, mat_id, year, temp_ini, certification)
           db.execute(sql1,values1)
           for line in lines [5:]: 
               sample_id, time, temperature = line.strip().split(";")
               test_id=id
               sql2="INSERT INTO Samples VALUES(?,?,?,?);"
               values2=(int(sample_id), test_id, int(time), float(temperature))
               cursor.execute(sql2,values2)
                              
    db.commit()
    f.close()       
    pass
    
# %%
# WRITE A SUMMARY
#
def cmd_summary(con: sqlite3.Connection, args: str) -> None:
    """Regista um resumo dos materiais testados em um intervalo de datas
    e com a certificção especificada 
       Variáveis- data de ínicio (start_arg)
                  data de fim (end_arg)
                  certificação (certification)
      Consulta a base de dados
      Seleciona as referências (mat_id) e o número de materias que respeitam as condições:
          -ensaios realizados entre as datas indicadas (start e end)
          -certetificação indicada
      Conta o número de amostras referentes aos materias selcionados    
      
    """
    lista= args.split(";")
    start_arg=lista[0]
    end_arg=lista[1]
    certification_arg=lista[2]
    
    cur=con.cursor()
    query1="SELECT MIN(year) from Tests"
    cur.execute(query1)
    start=cur.fetchone()[0]
    query2="SELECT MAX(year) from Tests"
    cur.execute(query2)
    end=cur.fetchone()[0]
    if start_arg=="*":
       startex=start
    else:
       startex=int(start_arg)
    if end_arg=="*":
       endex=end   
    else:
       endex=int(end_arg)
    if certification_arg=="*":
        cur=con.cursor()    
        queryfinal2="SELECT DISTINCT mat_id from Tests WHERE year >=? AND year<=?;"
        cur.execute(queryfinal2, (startex, endex,))
        materials=cur.fetchall()
        totsamples=0
        for material in materials:
            sample_cursor=cur.execute("""SELECT COUNT (*) 
                                      FROM Tests,Samples 
                                      WHERE Tests.id=Samples.test_id AND Tests.mat_id=? """, (material[0],))
            totsamples += sample_cursor.fetchone ()[0]
        print(str(len(materials))+" materials between "+str(start_arg)+" and "+str(end_arg)+
              " with certification "+certification_arg+" :")
        for material in materials:
            print("\t"+material[0])
        print("Total samples: "+str(totsamples))
    else:
        cur=con.cursor()    
        queryfinal2="SELECT DISTINCT mat_id from Tests WHERE year >=? AND year<=? AND certification=?;"
        cur.execute(queryfinal2, (startex, endex, certification_arg))
        materials=cur.fetchall()
        totsamples=0
        for material in materials:
            sample_cursor=cur.execute("""SELECT COUNT (*) 
                                      FROM Tests, Samples 
                                      WHERE Tests.id=Samples.test_id AND Tests.mat_id=? """, (material[0],))
            totsamples += sample_cursor.fetchone ()[0]
        print(str(len(materials))+" materials between "+str(start_arg)+" and "+str(end_arg)+
              " with certification "+certification_arg+" :")
        for material in materials:    
            print("\t"+material[0])
        print("Total samples: "+str(totsamples))
    pass
   
    

def cmd_summary_file(con: sqlite3.Connection, args: str) -> None:
    """Salva o resultado em um arquivo
       Cria um ficheiro
       Escreve os dados selcionados com configuração igual ao comando summary
    """
    lista= args.split(";")
    filename=lista[0]
    start_arg=lista[1]
    end_arg=lista[2]
    certification_arg=lista[3]
    
    cur=con.cursor()
    query1="SELECT MIN(year) from Tests"
    cur.execute(query1)
    start=cur.fetchone()[0]
    query2="SELECT MAX(year) from Tests"
    cur.execute(query2)
    end=cur.fetchone()[0]
    if start_arg=="*":
       startex=start
    else:
       startex=int(start_arg)
    if end_arg=="*":
       endex=end   
    else:
       endex=int(end_arg)
    if certification_arg=="*":
        cur=con.cursor()    
        queryfinal2="SELECT DISTINCT mat_id from Tests WHERE year >=? AND year<=?;"
        cur.execute(queryfinal2, (startex, endex,))
        materials=cur.fetchall()
        totsamples=0
        for material in materials:
            sample_cursor=cur.execute("""SELECT COUNT (*) 
                                      FROM Tests,Samples 
                                      WHERE Tests.id=Samples.test_id AND Tests.mat_id=? """, (material[0],))
            totsamples += sample_cursor.fetchone ()[0]
        file=open(filename,"w")
        file.write(str(len(materials))+" materials between "+start_arg+" and "+end_arg+" with certification "+certification_arg+" :"+"\n")
        for material in materials:
           file.write("\t"+material[0]+"\n")
        file.write("Total samples: "+str(totsamples)) 
        file.close()
    else:
        cur=con.cursor()    
        queryfinal2="SELECT DISTINCT mat_id from Tests WHERE year >=? AND year<=? AND certification=?;"
        cur.execute(queryfinal2, (startex, endex, certification_arg))
        materials=cur.fetchall()
        totsamples=0
        for material in materials:
            sample_cursor=cur.execute("""SELECT COUNT (*) 
                                      FROM Tests, Samples 
                                      WHERE Tests.id=Samples.test_id AND Tests.mat_id=? """, (material[0],))
            totsamples += sample_cursor.fetchone ()[0]
        file=open(filename,"w")
        file.write(str(len(materials))+" materials between "+start_arg+" and "+end_arg+
              " with certification "+certification_arg+" :"+"\n")
        for material in materials:
           file.write("\t"+material[0]+"\n")
        file.write("Total samples: "+str(totsamples)) 
        file.close()
    pass

# %%
# PLOT A GRAPH OF MATERIALS
#    
def cmd_plot(db: sqlite3.Connection, args: str) -> None:
    """Cria um gráfico que define o arrefecimento de um material ao longo do tempo
       Seleciona, para um material, os paramêtros das respetivas tabelas:
           tempo, temperatura e temperatura inicial 
       Calcula a temperatura relativa e o k 
       Cria um gráfico com mil 1000 pontos de temperatura relativa em função do tempo decorrido     
    """
    cur=db.cursor()
    mts=args.split(";")
    for mt in mts:
        cur.execute ("""SELECT Samples.time, Samples.temperature, Tests.temp_ini 
                           FROM Samples, Tests 
                           WHERE Samples.test_id=Tests.id AND Tests.mat_id=?;""",(mt,))
        data=cur.fetchall()
        time=[]
        temp_rel=[]
        for row in data:
            time.append(row[0])
            temp_relative=row[1]/row[2]
            temp_rel.append(temp_relative) 
        kinter=0
        for i in range(len(time)):
            if temp_rel[i]>0 and time[i]>0:
              kinter+=(-1)*math.log(temp_rel[i])/time[i]
        if len(time)>0:
            k=kinter/len(time)          
            T=[i/10 for i in range(1000)]
            K=[]
            for t in T:
              K.append(math.exp((-1)*t*k))
            plt.plot(time, temp_rel, "x")
            plt.plot(T, K, "-", label=mt)
    plt.xlabel("Elapsed time(hours)")
    plt.ylabel("Relative temperature")
    plt.title("Cooling over time")
    plt.legend()
    plt.show()       
    pass


# %%
# PLOT A GRAPH TO FILE
#


def cmd_plot_file(db: sqlite3.Cursor, args: str) -> None:
    """Salva o gráfico em um ficheiro
       Cria um ficheiro
       Cria o gráfico relativo ao areefecimento dos materias ao longo do tempo
       Salva a figura criada no ficheiro
    """
    cur=db.cursor()
    listmts=args.split(";")
    filename=listmts[0]
    mts=listmts[1:]
    plt.figure()
    for mt in mts:
        cur.execute ("""SELECT Samples.time, Samples.temperature, Tests.temp_ini 
                           FROM Samples, Tests 
                           WHERE Samples.test_id=Tests.id AND Tests.mat_id=?;""",(mt,))
        data=cur.fetchall()
        time=[]
        temp_rel=[]
        for row in data:
            time.append(row[0])
            temp_relative=row[1]/row[2]
            temp_rel.append(temp_relative) 
        kinter=0
        for i in range(len(time)):
            if temp_rel[i]>0 and time[i]>0:
              kinter+=(-1)*math.log(temp_rel[i])/time[i]
        if len(time)>0:
            k=kinter/len(time)          
            T=[i/10 for i in range(1000)]
            K=[]
            for t in T:
              K.append(math.exp((-1)*t*k))
            plt.plot(time, temp_rel, "x")
            plt.plot(T, K, "-", label=mt)
    plt.xlabel("Elapsed time(hours)")
    plt.ylabel("Relative temperature")
    plt.title("Cooling over time")
    plt.legend()
    plt.savefig(filename)
       
    pass


# %%
# EXECUTE ONE COMMAND
#
def cmd_execute(con: sqlite3.Connection, file_cmds: str) -> None:
    """Executa os comandos lidos do ficheiro ‘filename’, um por linha, 
    como se tivessem sido introduzidos a partir do teclado.
       Abre um ficheiro
       Lê o ficheiro linha a linha
       Executa os comandos presentes na linha a ler associando-os com uma função
    """
    fich=open(file_cmds, "r")
    comand=fich.readlines()
    for line in comand:
        line=upper_command(line) + " "
        cmd=strip_list(line.split(" ",1))
        if cmd[0]=="CREATE_TABLES":  
            cmd_create_tables(con)
        elif cmd[0]=="LOAD_TEST":
            cmd_load_test(con,cmd[1])
        elif cmd[0]=="SUMMARY":
             cmd_summary(con,cmd[1])
        elif cmd[0]=="SUMMARY_FILE":
             cmd_summary_file(con,cmd[1])
        elif cmd[0]=="PLOT":
             cmd_plot(con,cmd[1])
        elif cmd[0]=="PLOT_FILE":
             cmd_plot_file(con,cmd[1])
    return None
    pass
    


# %%
# AUXILIAR FUNCTIONS
#

def strip_list(x: list[str]) -> list[str]:
    """
    Strip all the strings in the list
    """
    return [i.strip() for i in x]


def upper_command(s: str) -> str:
    """
    Converts the first word in 's' to uppercase.
    """
    words = strip_list(s.split(' ', maxsplit=1))
    words[0] = words[0].upper()
    cmd = ' '.join(words)
    return cmd


def read_command(f) -> str:
    """
    Reads a command.
    retuns the command word in uppercase followed by the given arguments.
    """
    if f is None:
        # reads from keyboard
        cmd = ''
        while cmd == '':
            cmd = input("Command: ").strip()
    else:
        # reads from file 'f'
        cmd = f.readline()
        if cmd == '':
            cmd = 'QUIT'
    return upper_command(cmd.strip())


# %%
# PROCESS ONE COMMAND
#
def process_one_cmd(db: sqlite3.Connection, comando: str) -> None:
    """Executa o comando incidado.
       Lê o comando pretendido
       Associa-o a função
       Executa a função
    """
    comando = comando + ' '
    cmd = strip_list(comando.split(' ', 1))
    
    if cmd[0]=="CREATE_TABLES":  
        cmd_create_tables(db)
    elif cmd[0]=="LOAD_TEST":
        cmd_load_test(db,cmd[1])
    elif cmd[0]=="SUMMARY":
         cmd_summary(db,cmd[1])
    elif cmd[0]=="SUMMARY_FILE":
         cmd_summary_file(db,cmd[1])
    elif cmd[0]=="PLOT":
         cmd_plot(db,cmd[1])
    elif cmd[0]=="PLOT_FILE":
         cmd_plot_file(db,cmd[1])
    elif cmd[0]=="EXECUTE":
         cmd_execute(db,cmd[1])
    
    else:
        print('Unknown command!')
    return 


# %%
# MAIN FUNTION TO PROCESS ALL COMMANDS
#

def process_cmds(db_file: str, inf=None) -> None:
    """
     Processes a sequence of commands, producing corresponding outputs.
     db_file: name of the database where to place/read the information.
     inf: (please ignore, call this function with only the first argument)
    """
    assert (db_file != "")

    #   open the database file
    conn = sqlite3.connect(db_file)

    # The main loop
    cmd = '#'
    while cmd != 'QUIT':
        if cmd[0] != '#':
            process_one_cmd(conn, cmd)
        cmd = read_command(inf)

    conn.close()
    print("BYE!")


def main():
    process_cmds("database.db")
    


if __name__ == '__main__':
    main()  # run program