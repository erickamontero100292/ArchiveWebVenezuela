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

# Script for processing a directory containing warc files
# Run with: $ python processWarcDir.py -d <directory> -i <collection_id> -e <event> -t <event_type>


from bs4 import BeautifulSoup
from hanzo.warctools import ArchiveRecord, WarcRecord
from hanzo.httptools import RequestMessage, ResponseMessage
from contextlib import closing

# create the connection to solr
conn = SolrConnection(server=["localhost:8990","localhost:7580"], detect_live_nodes=False, user=None, password=None, timeout=10)
coll = conn['tesis']
global log

log = open("log.txt", "w+b")
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

# Extracts text from a given HTML file and indexes it into the Solr Instance
def extractTextAndIndexToSolr(html_file, file_url, wayback_url, collection_id, event, event_type,nameWarc,numHtml):
    log.write("Inicia el metodo extractTextAndIndexToSolr para el Warc: - "+nameWarc+" | " + time.strftime("%H:%M:%S") + " | " + time.strftime("%d/%m/%y")+" \n")
 
    name = html_file
    name = name.replace("/","")
    name= name.replace("-","")
    #read the file into a string so beautifulsoup can use it
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
    #extract text using soup  
    html_id = hashlib.md5(file_url).hexdigest()
    #Quita el codigo javascript y css
    for script in soup(["script", "style"]):
		script.extract()    # rip it out
    
    html_body = soup.get_text() 
    #text_file = open(name + ".txt", "w+b")
    #text_file.write(html_body)
    #text_file.close()
    
    # build the doc to index into solr
    # the fields here are the same as if an xml file were being used
    # so id is similar to an <id> tag and <content> as well, etc...
    log.write("Se genera el json para mandarlo a Solr Cloud| " + time.strftime("%H:%M:%S") + " | " + time.strftime("%d/%m/%y")+" \n")
    doc = [{"id":html_id, "nameWarc":nameWarc,"content":html_body, "URL":file_url,"version":version,"year":year,"month":month,"day":day, "waybackURL":wayback_url}]

    #attempt to add it to the index, make sure to commit later
    try:
        
        #print numHtml
        #print "Se añade el json a la coleccion " +str(numHtml)
        log.write("Se añade el json"+str(k)+" a la coleccion | " + time.strftime("%H:%M:%S") + " | " + time.strftime("%d/%m/%y")+" \n")
        coll.add(doc)
		
    except Exception as inst:
        log.write("Falla el metodo unpackWarcAndRetrieveHtml - No se puede añadir el json  "+str(numHtml)+" la coleccion - "+str(inst) +"| " + time.strftime("%H:%M:%S") + " | " + time.strftime("%d/%m/%y")+" \n")
        ruta="/media/erickamontero/D/DatosDePrueba/archivoWebVenezuela/archivosNoIndexados/"
        nameWarcFile,warc,gz =nameWarc.split('.')
        nameJson=ruta+"documento"+nameWarcFile+str(numHtml)+".json"
        texto=str(doc)
        #print name
        json= open(nameJson, "w+b")
        json.write(texto)
        json.close()
        #print "Error indexting file, with message" + str(inst)
    



# Unpacks a given .warc file and produces a log file
def unpackWarcAndRetrieveHtml(filename, textFile, collection_id, event, event_type):
	global k
	k=0
	print "unpackWarcAndRetrieveHtml"
	#print "filename "+filename
	nameWarc = os.path.basename(filename)
	log.write("Inicia el metodo unpackWarcAndRetrieveHtml para el warc- "+nameWarc+" | "  + time.strftime("%H:%M:%S") + " | " + time.strftime("%d/%m/%y")+" \n")
	#print os.path.basename(filename)
	#print "textFile "+textFile
	#print "collection_id "+ collection_id
	#print "event "+event
	#print "event_type "+event_type
	
	output_dir = filename.split(".")[0] + "/"
	#print "output_dir " + output_dir
	
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
	#print html_files
	for i in html_files:
		log.write("Se llama el metodo extractTextAndIndexToSolr ""| " + time.strftime("%H:%M:%S") + " | " + time.strftime("%d/%m/%y")+" \n")
		k=k+1
		extractTextAndIndexToSolr(i["file"], i["url"], i["wayback_url"], collection_id, event, event_type,nameWarc,k)
        
	
# Begins the process of processing a single warc file in a directory
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
	
# Processes the given directory for .warc files
def main(argv):
	i=0
	log.write("Inicia el metodo main | " + time.strftime("%H:%M:%S") + " | " + time.strftime("%d/%m/%y")+" \n")
	#log.write("Inicia el metodo main | "+ time.strftime("%H:%M:%S")+"\n")
	print time.strftime("%H:%M:%S")
	if (len(argv) < 1):
		print >> sys.stderr, "usage: processWarcDir.py -d <directory> -i <collection_id> -e <event> -t <event_type>"
		log.write("Fallo el metodo main | " + time.strftime("%H:%M:%S") + " | " + time.strftime("%d/%m/%y")+" \n")
		log.close()
		sys.exit()
		
	if (argv[0] == "-h" or  len(argv) < 4):
		print >> sys.stderr, "usage: processWarcDir.py -d <directory> -i <collection_id> -e <event> -t <event_type>"
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
        		
	try:
		#solr_instance.commit()
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

