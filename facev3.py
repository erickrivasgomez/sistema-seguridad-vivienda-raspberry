import cv2
import pickle
import numpy as np
import os
from PIL import Image
import pyttsx3
import json
import firebase_admin
import time
from firebase_admin import credentials, firestore,db
import sys

def registrar(nomb):
	DirectoryPath ='Database/'+str(nomb)
	os.mkdir(DirectoryPath)

	raw_input("Presione enter para generar su carpeta de datos")

	web_cam = cv2.VideoCapture(0)
	web_cam.set(3, 640)
	web_cam.set(4, 480)

	#web_cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
	#web_cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
	cascPath = "Cascades/haarcascade_frontalface_default.xml"
	faceCascade = cv2.CascadeClassifier(cascPath)

	contador = 0

	while(True):
		_, imagen_marco = web_cam.read()
		grises = cv2.cvtColor(imagen_marco, cv2.COLOR_BGR2GRAY)

		rostro = faceCascade.detectMultiScale(grises, 1.5, 5)

		for(x,y,w,h) in rostro:
			cv2.rectangle(imagen_marco,(x,y), (x+w,y+h), (255,0,0), 4)
			contador +=1

			cv2.imwrite("Database/"+nomb+"/"+nomb+"_"+str(contador)+".jpg",grises[y:y+h,x:x+w])
		cv2.imshow("Registrado tu perfil en la base de datos..",imagen_marco)

		if cv2.waitKey(1) & 0xFF == ord('e'):
			break
		elif contador >= 100:
			break


	web_cam.release()
	cv2.destroyAllWindows()
	actualizarYML()
	


#Aactualizar Base de Datos ------------------------------------------------------------------------------------------------------------- 
def actualizarYML():	
	cascPath = "Cascades/haarcascade_frontalface_alt2.xml"
	faceCascade = cv2.CascadeClassifier(cascPath)

	#reconocimiento con opencv
	# reconocimiento = cv2.createLBPHFaceRecognizer()
	reconocimiento = cv2.face.LBPHFaceRecognizer_create()


	BASE_DIR = os.path.dirname(os.path.abspath(__file__))
	image_dir = os.path.join(BASE_DIR,"Database")


	current_id = 0
	etiquetas_id = {}
	y_etiquetas = []
	x_entrenamiento = []

	for root, dirs, archivos in os.walk(image_dir):
	    for archivo in archivos:
	        if archivo.endswith("png") or archivo.endswith("jpg"):
	            pathImagen = os.path.join(root,archivo)
	            etiqueta = os.path.basename(root).replace(" ", "-")#.lower()

	            #Creando las etiquetas
	            if not etiqueta in etiquetas_id:
	                etiquetas_id[etiqueta] = current_id
	                current_id += 1
	            id_ = etiquetas_id[etiqueta]

	            pil_image = Image.open(pathImagen).convert("L")
	            tamanio = (550,550)
	            imagenFinal = pil_image.resize(tamanio, Image.ANTIALIAS)
	            image_array = np.array(pil_image,"uint8")

	            rostros = faceCascade.detectMultiScale(image_array, 1.5, 5)

	            for (x,y,w,h) in rostros:
	                roi = image_array[y:y+h, x:x+w]
	                x_entrenamiento.append(roi)
	                y_etiquetas.append(id_)

	with open("labels.pickle",'wb') as f:
	    pickle.dump(etiquetas_id, f)

	reconocimiento.train(x_entrenamiento, np.array(y_etiquetas))
	reconocimiento.save("nuevosdatos.yml")






def reconocer():
	global persona
	persona = "desconocido"

	print "Reconomiento facial" 

	cascPath = "Cascades/haarcascade_frontalface_alt2.xml"
	faceCascade = cv2.CascadeClassifier(cascPath)

	eyeCascade = cv2.CascadeClassifier("Cascades/haarcascade_eye.xml")
	smileCascade = cv2.CascadeClassifier("Cascades/haarcascade_smile.xml")

	# reconocimiento = cv2.createLBPHFaceRecognizer()
	reconocimiento = cv2.face.LBPHFaceRecognizer_create()
	# reconocimiento.load("nuevosdatos.yml")
	reconocimiento.read("nuevosdatos.yml")

	etiquetas = {"nombre_persona": 1}
	with open("labels.pickle",'rb') as f:
            pre_etiquetas = pickle.load(f)
            etiquetas = {v:k for k,v in pre_etiquetas.items()}

	web_cam = cv2.VideoCapture(0)
	#web_cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
	web_cam.set(3, 640)
	web_cam.set(4, 480)
	#web_cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
	count = 0

	while(True):
		intruso()
		estado = open("estado_puerta.txt",'r')
		if "abierta" in estado.read():
			estado.close
			break
		ret,marco = web_cam.read()
		grises = cv2.cvtColor(marco, cv2.COLOR_BGR2GRAY)
		rostros = faceCascade.detectMultiScale(grises, 1.5,5)

		for(x, y, w, h) in rostros:
			#print(x,y,w,h)
			roi_gray = grises[y:y+h, x:x+w]
			roi_color = marco[y:y+h, x:x+w]
			persona = "desconocido"


			#reconocimiento facial
			_id, conf = reconocimiento.predict(roi_gray)
			if conf >= 10 and conf < 48:
				font = cv2.FONT_HERSHEY_SIMPLEX
				count += 1



				nombre = etiquetas[_id]

				if conf > 50:
					print "Comparando..."

				color = (255,255,255)
				grosor = 2
				# cv2.putText(marco, nombre, (x,y), font, 1, color, grosor, cv2.CV_AA)
				cv2.putText(marco, nombre, (x,y), font, 1, color, grosor, cv2.LINE_AA)
				persona = nombre
				intruso()
				return persona


			cv2.rectangle(marco, (x,y), (x+w, y+h), (0,255,0), 2)

			rasgos = smileCascade.detectMultiScale(roi_gray)
			for(ex,ey,ew,eh) in rasgos:
				cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0,255,0),2)
		#Display resize del marco
		#marco_display = cv2.resize(marco, (800, 480), interpolation = cv2.INTER_CUBIC)
		cv2.imshow('Detectando rostros - Presione (e) para salir',marco)

		if count >= 8:
			#count = True
			engine = pyttsx3.init()
			engine.setProperty('rate', 130)
			engine.say('{}'.format('bienvenido '+nombre))
			engine.runAndWait()
			#entradaBD(nombre)
			print(nombre)
			break;


		elif cv2.waitKey(1) & 0xFF == ord('e'):
			break;

	#cuando todo esta hecho, liberamos la captura
	web_cam.release()
	cv2.destroyAllWindows()

def entradaBD(nombre):
	cred = credentials.Certificate("ServiceAccountKey.json")

	firebase_admin.initialize_app(cred, {
	    'databaseURL': 'https://test-eb0f8.firebaseio.com'
	})
	ref = db.reference('data/')

	fecha = str(time.strftime("%d-%m-%y"))
	print fecha
	hora = str(time.strftime("%H:%M:%S"))
	print hora
	datos = ref.child('Datos')
	datos.update({
	    fecha+" "+hora : {
	        'Nombre': nombre,
	    }
	})

def intruso():
	archivo = open ("desconocido.txt","w")
	archivo.write(persona)
	archivo.close

def estadoPuerta():
	while True:
		desconocido = open ("desconocido.txt","r")
		estado = open("estado_puerta.txt",'r')
		if "cerrada" in estado.read() and "desconocido" in desconocido.read() :
			reconocer()
		estado.close
		desconocido.close

persona="desconocido"

n=""
#while n!="4" :
	#print "1.- Registrar\n2.- Actualizar Base de Datos\n3.- Reconocer\n4.- Salir"
	
n = sys.argv[1]

if n=="1":
	nombre=raw_input("Introduzca su nombre: ")
	registrar(nombre)
elif n=="2":
	actualizarYML()
elif n=="3":
	reconocer()
	estadoPuerta()
