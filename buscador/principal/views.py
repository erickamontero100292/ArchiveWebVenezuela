from principal.models import Buscador
from principal.forms import BuscadorForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from solrcloudpy.connection import SolrConnection
from solrcloudpy import SearchOptions
import urllib2
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render

conn = SolrConnection(server=["localhost:8987","localhost:7578"], detect_live_nodes=False, user=None, password=None, timeout=10)
coll = conn['archiveWebVenezuela']


def inicioContenido(request):
	palabraClaves =  request.GET.get('q', '')
	page = request.GET.get('page')
	resul= 0
     	if palabraClaves:
		print palabraClaves
		palabra=palabraClaves
           	palabraClaves=  'content:*'+palabraClaves+'*'
	   	print palabraClaves
    	   	respuesta = coll.search({'q':palabraClaves})
	   	#print respuesta.result.response
	   	paginator = Paginator(respuesta.result.response['docs'], 10)
		print respuesta.result.response['docs']
	   	try:	
	         	p=paginator.page(page)
			resul=1
	   	except PageNotAnInteger:
		 	p=paginator.page(1)
	   	except EmptyPage:
		 	p=paginator.page(paginator.num_pages)
		print p
	   	return render (request,'home.html',{'palabraClaves':p,'res':'0'})
	else:	
		print page
		if page:
			resul=1
			palabraClaves = request.GET.get('res')
			palabraClaves=  str('content:*'+palabraClaves+'*')
	   		print palabraClaves
    	   		respuesta = coll.search({'q':palabraClaves})
			
			paginator = Paginator(respuesta.result.response['docs'], 10)
			print paginator
	   		try:	
	         		p=paginator.page(page)
	   		except PageNotAnInteger:
		 		p=paginator.page(1)
	   		except EmptyPage:
		 		p=paginator.page(paginator.num_pages)
	   		return render (request,'home.html',{'palabraClaves':p,'res':'0'})

	#WARC1.warc.gz
      	palabraClaves=""
      	return render (request,'home.html',{'palabraClaves':"",'res':{},'resul':" "})

def inicioURL(request):
	print 'entre url'
	palabraClaves =  request.GET.get('q', '')
	page = request.GET.get('page')
	resul= 0
     	if palabraClaves:
		print palabraClaves
		palabra=palabraClaves
           	palabraClaves=  'URL:*'+palabraClaves+'*'
	   	print palabraClaves
    	   	respuesta = coll.search({'q':palabraClaves})
	   	#print respuesta.result.response
	   	paginator = Paginator(respuesta.result.response['docs'], 10)
		#print respuesta.result.response['docs']
	   	try:	
	         	p=paginator.page(page)
			resul=1
	   	except PageNotAnInteger:
		 	p=paginator.page(1)
	   	except EmptyPage:
		 	p=paginator.page(paginator.num_pages)

		print p
	   	return render (request,'home.html',{'palabraClaves':p,'res':'0'})
	else:	
		print page
		if page:
			resul=1
			palabraClaves = request.GET.get('res')
			palabraClaves=  str('URL:*'+palabraClaves+'*')
	   		print palabraClaves
    	   		respuesta = coll.search({'q':palabraClaves})
			
			paginator = Paginator(respuesta.result.response['docs'], 10)
			print paginator
	   		try:	
	         		p=paginator.page(page)
	   		except PageNotAnInteger:
		 		p=paginator.page(1)
	   		except EmptyPage:
		 		p=paginator.page(paginator.num_pages)
	   		return render (request,'home.html',{'palabraClaves':p,'res':'0'})

	#WARC1.warc.gz
      	palabraClaves=""
      	return render (request,'home.html',{'palabraClaves':"",'res':{},'resul':" "})
        



