#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import os.path
import warcunpack_ia
import glob
import shutil
from solrcloudpy.connection import SolrConnection
from solrcloudpy import SearchOptions
import hashlib
import time
import io,json

# Script para procesar el directorio que contiene los documentos no indexados
# Run with: $ python processWarcDir.py -d <directory> -i <collection_id> -e <event> -t <event_type>


from bs4 import BeautifulSoup
from hanzo.warctools import ArchiveRecord, WarcRecord
from hanzo.httptools import RequestMessage, ResponseMessage
from contextlib import closing

# crea la conexion con solr
conn = SolrConnection(server=["localhost:8990","localhost:7580"], detect_live_nodes=False, user=None, password=None, timeout=10)
coll = conn['tesis']
global logArchivo	


logArchivo = open("logIndexacion.txt", "w+b")
# Extrae el texto de los html y lo añade a la coleccion
def extractTextAndIndexToSolr(fileJson):
    logArchivo.write("Inicia el metodo extractTextAndIndexToSolr para el json: - "+fileJson+" | " + time.strftime("%H:%M:%S") + " | " + time.strftime("%d/%m/%y")+" \n")
    data = []
    try:        
		data = ""
		with open(fileJson) as data_file:    
			data = json.load(data_file)
		logArchivo.write("Se añade el json"+fileJson+" a la coleccion | " + time.strftime("%H:%M:%S") + " | " + time.strftime("%d/%m/%y")+" \n")
		data = str(data)
		coll.add(data)
		os.unlink(fileJson)
		
    except Exception as inst:
        logArchivo.write("Falla el metodo extractTextAndIndexToSolr - No se puede añadir el json  " +fileJson+"|"+ time.strftime("%H:%M:%S") + " | " + time.strftime("%d/%m/%y")+" \n")
        #ruta="/home/hilda/Escritorio/archivoWebVenezuela/archivosNoIndexados/"
        ruta="/home/erickamontero/archivoWebVenezuela2/archivosNoIndexados/"
        nameJsonFile =fileJson
        print "falle - "+nameJsonFile

# Limpia la direccion del archivo json
def processJsonFile(json_file):
	logArchivo.write("Inicia el metodo processJsonFile| " + time.strftime("%H:%M:%S") + " | " + time.strftime("%d/%m/%y")+" \n")
	name_file = json_file.split('/')
	name_file = name_file[4]+"/"+name_file[5]
	print name_file
	extractTextAndIndexToSolr(name_file)

# Procesa el directorio para los archivos .json
def main(argv):
	i=0
	logArchivo.write("Inicia el metodo main | " + time.strftime("%H:%M:%S") + " | " + time.strftime("%d/%m/%y")+" \n")
	
	if (len(argv) < 1):
		print >> sys.stderr, "usage: processWarcDir.py -d <directory> -i <collection_id> -e <event> -t <event_type>"
		logArchivo.write("Fallo el metodo main | " + time.strftime("%H:%M:%S") + " | " + time.strftime("%d/%m/%y")+" \n")
		
		logArchivo.close()
		sys.exit()	
	rootdir = argv[1]
	hayArchivos =True
	intentos = 3 
	
	while hayArchivos and intentos > 0:	
		for root, subFolders, files in os.walk(rootdir):
			if(files):
				for filename in files:
					filePath = os.path.join(root, filename)
					if filename.endswith(".json"):
						logArchivo.write("Se encontro un archivo"+ filePath+" | " + time.strftime("%H:%M:%S") + " | " + time.strftime("%d/%m/%y")+" \n")
						processJsonFile(filePath)
						root, subFolders, files in os.walk(rootdir)

			else:
				hayArchivos =False
		print intentos
		intentos = intentos - 1

        		
	try:
		coll.commit()
		logArchivo.write("Se realiza el commit en Solr Cloud | " + time.strftime("%H:%M:%S") + " | " + time.strftime("%d/%m/%y")+" \n")
	except:
		logArchivo.write("No se pudo realizar el commit en Solr Cloud | " + time.strftime("%H:%M:%S") + " | " + time.strftime("%d/%m/%y")+" \n")
		print "Could not Commit Changes to Solr, check the log files."
	else:
		logArchivo.write("Se realizo el commit en Solr Cloud | " + time.strftime("%H:%M:%S") + " | " + time.strftime("%d/%m/%y")+" \n")
		print "Successfully committed changes"
	logArchivo.close()
	
if __name__ == "__main__":
	main(sys.argv[1:])

