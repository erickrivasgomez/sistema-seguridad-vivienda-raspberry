import serial
import time
import smtplib
from mysql.connector import MySQLConnection, Error
 
def insertar_en_mapa(latitud, longitud):
    query = "INSERT INTO ubicaciones(latitud, longitud) " \
            "VALUES(%s,%s)"
    args = (latitud, longitud)
 
    try:
        conn = MySQLConnection(host='localhost',
                                       database='db',
                                       user='username',
                                       password='password')
 
        cursor = conn.cursor()
        cursor.execute(query, args)
 
        if cursor.lastrowid:
            print "INSERTADO EN BD"
        else:
            print('last insert id not found')
 
        conn.commit()
    except Error as error:
        print(error)
 
    finally:
        cursor.close()
        conn.close()


def sendemail(from_addr, to_addr_list, cc_addr_list,
              subject, message,
              login, password,
              smtpserver='smtp.gmail.com:587'):
    header  = 'From: %s\n' % from_addr
    header += 'To: %s\n' % ','.join(to_addr_list)
    header += 'Cc: %s\n' % ','.join(cc_addr_list)
    header += 'Subject: %s\n\n' % subject
    message = header + message
    problems = ''
    #server = smtplib.SMTP(smtpserver)
    #server.starttls()
    #server.login(login,password)
    #problems = server.sendmail(from_addr, to_addr_list, message)
    #server.quit()
    return problems


arduino = serial.Serial('/dev/ttyACM0', baudrate=9600, timeout=3.0)
# arduino.open()
txt = '0' # Valor recibido del arduino (Char[])
valor = 0 # Valor para comparar (Int), es igual a txt
estado = True # True si la puerta esta Cerrada
anterior = estado
contador = 0


while True:
    time.sleep(1) # Esperar 1 decima de segundo
    
    # Ciclo para concatenar el valor recibido del arduino
    while arduino.inWaiting() > 0:
        txt += arduino.read(1) # Concatenar cada digito
    print txt
    valor = int(txt) # Convertir el valor, a entero
    
    # Si el estado es "Abierto, y el valor es menor a 5, la puerta se cerro"
    if valor <= 4 and valor > 0:
        estado = True # Cambiar el estado a "Cerrada"
        if estado != anterior:
            print "              Cerrada"
            anterior = estado
            
            sendemail(from_addr    = 'raspberrypichpiri@gmail.com', 
                to_addr_list = ['raspberrypichpiri@gmail.com'],
                cc_addr_list = [], 
                subject      = 'Casa Notificadora', 
                message      = 'Tu puerta ha sido abierta', 
                login        = 'raspberrypichpiri@gmail.com', 
                password     = 'pichpiri1.')
            print "###################################################"
            print "              EMAIL ENVIADO - CERRADO"
            print "###################################################"
            file = open("estado_puerta.txt","w")
            
            file.write("cerrada")
             
            file.close() 
            
         
    
    # Decidir si la puerta ha sido abierta
    if valor > 4:
        #insertar_en_mapa(19.721861,-101.185841)
        estado = False # Cambiar el estado a "Abierta"
        if estado != anterior:
            print "Abierta"
            anterior = estado
            
            sendemail(from_addr    = 'email@gmail.com', 
                to_addr_list = ['email@gmail.com'],
                cc_addr_list = [], 
                subject      = 'Casa Notificadora', 
                message      = 'Tu puerta ha sido abierta', 
                login        = 'email@gmail.com', 
                password     = 'password')
            print "###################################################"
            print "              EMAIL ENVIADO - ABIERTO"
            print "###################################################"
            file = open("estado_puerta.txt","w")
            
            file.write("abierta")
             
            file.close() 
            
    
    txt = '0'
arduino.close()
