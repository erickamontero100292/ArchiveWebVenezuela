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

# Script para procesar el directorio que contiene a los archivos warc
# Run with: $ python processWarcDir.py -d <directory> -i <collection_id> -e <event> -t <event_type>


from bs4 import BeautifulSoup
from hanzo.warctools import ArchiveRecord, WarcRecord
from hanzo.httptools import RequestMessage, ResponseMessage
from contextlib import closing

# crea la conexion en solr
conn = SolrConnection(server=["localhost:8990","localhost:7580"], detect_live_nodes=False, user=None, password=None, timeout=10)
coll = conn['tesis']
global log
global logAdvertencia
logAdvertencia = open("logAdvertencia.txt", "w+b")	
log = open("logIndexacion.txt", "w+b")
# Filters out html files from a log file produced by warc extraction
def parseLogFileForHtml(log_file):
    htmlList = []
    
    with open(log_file, 'r+b') as f:
        for line in f:
            splitext = line.split('\t')
            if len(splitext) >= 9:
            	content_type = splitext[6]
            	if content_type.find("text/html") == 0:
                	htmlList.append({"file":splitext[7], "wayback_url":splitext[8], "url":splitext[5]})
                
    return htmlList

# Extrae el texto de los html y lo añade a la coleccion
def extractTextAndIndexToSolr(html_file, file_url, wayback_url, collection_id, event, event_type,nameWarc,numHtml):
    log.write("Inicia el metodo extractTextAndIndexToSolr para el Warc: - "+nameWarc+" | " + time.strftime("%H:%M:%S") + " | " + time.strftime("%d/%m/%y")+" \n")
 
    name = html_file
    name = name.replace("/","")
    name= name.replace("-","")
    #lee el archivo para que  BeautifulSoup pueda usarlo
    html_file = open(html_file, "r")
    html_string = html_file.read()	
    #Obtener la version del warc
    nameWarcSplit = nameWarc
    nameWarcSplit = nameWarcSplit.split('-')
    version = nameWarcSplit[1]
    #obtener los valores para la busqueda facetadas
    fecha = nameWarcSplit[1]
    year = fecha[:4]
    month = fecha[4:6]
    day = fecha [6:8]
    if len(html_string) < 1:
      return
    try:
	  log.write("Se procede a extraer el html | " + time.strftime("%H:%M:%S") + " | " + time.strftime("%d/%m/%y")+" \n")
	  soup = BeautifulSoup(html_string,"lxml")
    except:
      log.write("Falla el metodo unpackWarcAndRetrieveHtml | " + time.strftime("%H:%M:%S") + " | " + time.strftime("%d/%m/%y")+" \n")
      print "Error: Cannot parse HTML from file: " + html_file
      return
    if len(html_string) < 1:
	  log.write("Error parseando el archivo | " + time.strftime("%H:%M:%S") + " | " + time.strftime("%d/%m/%y")+" \n")
	  print "error parsing html file " + str(html_file)
	  return
    #extraer el texto usando soup  
    html_id = hashlib.md5(file_url).hexdigest()
    #Quita el codigo javascript y css
    for script in soup(["script", "style"]):
		script.extract()    # rip it out
    
    html_body = soup.get_text() 
    
    # se construye el documento para indexarlo en solr
    log.write("Se genera el json para mandarlo a Solr Cloud| " + time.strftime("%H:%M:%S") + " | " + time.strftime("%d/%m/%y")+" \n")
    doc = [{"id":html_id, "nameWarc":nameWarc,"content":html_body, "URL":file_url,"version":version,"year":year,"month":month,"day":day, "waybackURL":wayback_url}]

    #se añade a la coleccion
    try:
        log.write("Se añade el json"+str(k)+" a la coleccion | " + time.strftime("%H:%M:%S") + " | " + time.strftime("%d/%m/%y")+" \n")
        coll.add(doc)
		
    except Exception as inst:
        log.write("Falla el metodo unpackWarcAndRetrieveHtml - No se puede añadir el json  "+str(numHtml)+" la coleccion - "+str(inst) +"| " + time.strftime("%H:%M:%S") + " | " + time.strftime("%d/%m/%y")+" \n")
        #ruta="/home/hilda/Escritorio/archivoWebVenezuela/archivosNoIndexados/"
        ruta="/home/erickamontero/archivoWebVenezuela2/archivosNoIndexados/"
        nameWarcFile =nameWarcSplit[0]+nameWarcSplit[1]
        print nameWarcFile
        nameJson=ruta+"documento"+nameWarcFile+"-"+str(numHtml)+".json"
        texto=str(doc)
        #print name
        with io.open(nameJson, 'w',encoding = 'utf-8') as outfile:
			outfile.write(unicode(json.dumps({"id":html_id, "nameWarc":nameWarc,"content":html_body, "URL":file_url,"version":version,"year":year,"month":month,"day":day, "waybackURL":wayback_url}, ensure_ascii=False)))
    



# descomprime un archivo .warc y produce un archivo de log
def unpackWarcAndRetrieveHtml(filename, textFile, collection_id, event, event_type):
	global k
	k=0
	print "unpackWarcAndRetrieveHtml"
	nameWarc = os.path.basename(filename)
	log.write("Inicia el metodo unpackWarcAndRetrieveHtml para el warc- "+nameWarc+" | "  + time.strftime("%H:%M:%S") + " | " + time.strftime("%d/%m/%y")+" \n")	
	output_dir = filename.split(".")[0] + "/"
	default_name = 'crawlerdefault'
	wayback="http://wayback.archive-it.org/"
	collisions = 0
	log_file = os.path.join(output_dir, filename.split("/")[1] + '.index.txt')
	log_file = open(log_file, 'w+b')
	warcunpack_ia.log_headers(log_file)
	
	try:
		with closing(ArchiveRecord.open_archive(filename=filename, gzip="auto")) as fh:
			collisions+=warcunpack_ia.unpack_records(filename, fh, output_dir, default_name, log_file, wayback)
	except StandardError, e:
		log.write("Falla el metodo unpackWarcAndRetrieveHtml para el warc- "+nameWarc+" | " + time.strftime("%H:%M:%S") + " | " + time.strftime("%d/%m/%y")+" \n")
		print >> sys.stderr, "exception in handling", filename, e
		
	html_files = parseLogFileForHtml(textFile)
	for i in html_files:
		log.write("Se llama el metodo extractTextAndIndexToSolr ""| " + time.strftime("%H:%M:%S") + " | " + time.strftime("%d/%m/%y")+" \n")
		k=k+1
		extractTextAndIndexToSolr(i["file"], i["url"], i["wayback_url"], collection_id, event, event_type,nameWarc,k)
        
	
# Inicia el proceso de abrir los arhchivos warc en el directorio
def processWarcFile(warc_file, collection_id, event, event_type):
	print "entre processWarcFile"
	log.write("Inicia el metodo processWarcFile | " + time.strftime("%H:%M:%S") + " | " + time.strftime("%d/%m/%y")+" \n")
	splitext = warc_file.split('.')
	output_dir = splitext[0] + "/"
	output_file = output_dir + warc_file.split("/")[1] + ".index.txt"

	if not os.path.exists(output_dir):
		os.makedirs(output_dir)
	log.write("Se llama el metodo unpackWarcAndRetrieveHtml para el WARC - "+os.path.basename(warc_file)+" | " + time.strftime("%H:%M:%S") + " | " + time.strftime("%d/%m/%y")+" \n")
	unpackWarcAndRetrieveHtml(warc_file, output_file, collection_id, event, event_type)
	
# Procesa el directorio donde se encuentran los archivos WARC
def main(argv):
	i=0
	log.write("Inicia el metodo main | " + time.strftime("%H:%M:%S") + " | " + time.strftime("%d/%m/%y")+" \n")
	print time.strftime("%H:%M:%S")
	if (len(argv) < 1):
		print >> sys.stderr, "usage: processWarcDir.py -d <directory> -i <collection_id> -e <event> -t <event_type>"
		log.write("Fallo el metodo main | " + time.strftime("%H:%M:%S") + " | " + time.strftime("%d/%m/%y")+" \n")
		log.close()
		sys.exit()
		
	if (argv[0] == "-h" or  len(argv) < 4):
		print >> sys.stderr, "usage: processWarcDir.py -d <directory> -i <collection_id> -e <event> -t <event_type>"
		logAdvertencia.write("No hay archivo WARC para indexar| " + time.strftime("%H:%M:%S") + " | " + time.strftime("%d/%m/%y")+" \n")		
		logAdvertencia.close()		
		sys.exit()
	
	rootdir = argv[1]
	collection_id = argv[3]
	event = argv[5]
	event_type = argv[7]

  	for root, subFolders, files in os.walk(rootdir):
		for filename in files:
			filePath = os.path.join(root, filename)
			if filename.endswith(".warc") or filename.endswith(".warc.gz"):
				log.write("Se llama el metodo processWarcFile para la ruta - "+ filePath+" | " + time.strftime("%H:%M:%S") + " | " + time.strftime("%d/%m/%y")+" \n")
				processWarcFile(filePath, collection_id, event, event_type)
			else:

				logAdvertencia.write("No hay archivo WARC para indexar| " + time.strftime("%H:%M:%S") + " | " + time.strftime("%d/%m/%y")+" \n")		
	
				
        		
	try:
		coll.commit()
		log.write("Se realiza el commit en Solr Cloud | " + time.strftime("%H:%M:%S") + " | " + time.strftime("%d/%m/%y")+" \n")
	except:
		log.write("No se pudo realizar el commit en Solr Cloud | " + time.strftime("%H:%M:%S") + " | " + time.strftime("%d/%m/%y")+" \n")
		print "Could not Commit Changes to Solr, check the log files."
	else:
		log.write("Se realizo el commit en Solr Cloud | " + time.strftime("%H:%M:%S") + " | " + time.strftime("%d/%m/%y")+" \n")
		print "Successfully committed changes"
	log.close()
	
if __name__ == "__main__":
	main(sys.argv[1:])

