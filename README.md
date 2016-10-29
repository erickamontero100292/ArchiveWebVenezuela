### Módulo de indexación y búsqueda ###
Módulo de indexación y búsqueda, forma parte del modulo de almacenamiento y indexación del prototipo de Archivo Web Venezuela

### Descripción ###
Esta es la segunda version del modulo de indexación para este prototipo, apuntando a tener nuevas características como indices distribuido, manejo de grandes volumenes de datos y búsqueda por contenido . Este módulo fue desarrollado usando la herramienta de búsqueda Solr, específicamente haciendo uso de una de sus nuevas caracteristicas que es SolrCloud. Se uso python como lenguaje principal para extraer la información de los WARC y realizar la limpieza de los documentos html. Nos apoyamos en el framework de Django para hacer una pequeña interfaz, que permita realizar las búsquedas por palabra clave en el contenido y por url.


## ¿Qué se ha guardado en este repositorio? ##
En el siguiente repositorio se ha guardado:

* El módulo de indexación y búsqueda para el prototipo de Archivo Web Venezuela en la carpeta 
* Los documentos relacionados con la aplicación en la carpeta “Tesis”


## Tecnologías y versiones utilizadas ##
* Ubuntu 16.04
* Python 2.7
* Java 1.8
* BeatifulSoap
* WarcTools
* Django 1.9

## Instalación ##
### UBUNTU ###
* sudo apt-get update && apt-get upgrade -y

### PYTHON ###
* sudo apt-get install python-software-properties
* sudo apt-get update
* sudo apt-get install python-pip
* sudo apt-get install python-bs4
* pip install setuptools
* pip install unittest2
* pip install warctools
* pip install BeautifulSoup4
* pip install solrcloudpy
* Ubicar el archivo sitecustomize.py y agregar lo siguiente:
	import sys
	sys.setdefaulencondig('utf-8')


### JAVA ###
* sudo add-apt-repository ppa:webupd8team/java
* sudo apt-get update
* sudo apt-get install oracle-java8-installer

### SOLR ###
* cd /tmp wget http://www.us.apache.org/dist/lucene/solr/6.2.1/solr-6.2.1.tgz
* tar xzf solr-6.2.1.tgz solr-6.2.1/bin/install_solr_service.sh --strip-components=2
* sudo ./install_solr_service.sh solr-6.2.1.tgz

### DJANGO ###
* sudo apt-get update
* sudo apt-get install python-django==1.9
* sudo pip install virtualenv

## Paso a paso ##

Una vez instaladas todas las tecnologías, se procede a la creacion de la colección en SolrCloud.
>Una vez instaladas todas las tecnologías, se procede a la creacion de la colección en SolrCloud.
>>1. Ir al direcctorio cd /opt.
>>2. Ir al directorio cd solr-6.2.1.
>>3. Detener los servicios sudo bin/solr stop -all.
>>4. Crear la colección con la guía de SolrCloud sudo bin/solr -e cloud.
>>>4.1. En este punto tenemos que tener definidos:cantidad de nodos a crear (2),nombre de la colección (archiveWebVenezuela),núumeros de replicas y shard (2,2), puertos a usar ().

>Iniciar los nodos
>>1. Ir al direcctorio cd /opt
>>2. Ir al directorio cd solr-6.2.1
>>3. sudo bin/solr restart -c -p 8987 -s example/cloud/node1/solr
>>4. sudo bin/solr restart -c -p 7578 -z localhost:9987 -s example/cloud/node2/solr

>Detener los nodos
>>1. Ir al direcctorio cd /opt
>>2. Ir al directorio cd solr-6.2.1
>>3. sudo bin/solr stop -all ; detento los servicios

## ¿Con quién debo hablar? ##
* **Desarrolladora :** Ericka Montero - Correo: erickamontero100292@gmail.com
* **Desarrolladora :** Hilda Pérez - Correo: hcpl547@gmail.com 
* **Tutora:** Profa. Mercy Ospina - Correo: mercy05@gmail.com
