# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para cineblog01
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os
import sys
import re, htmlentitydefs

from core import scrapertools
from core import logger
from core import config
from core.item import Item

__channel__ = "cineblog01"
__category__ = "F,S,A"
__type__ = "generic"
__title__ = "CineBlog 01"
__language__ = "IT"
sito="http://www.cb01.eu"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("[cineblog01.py] mainlist")
    itemlist = []
	

    # Main options
    itemlist.append( Item(channel=__channel__, action="peliculas"  , title="[COLOR azure]Cinema - Novita'[/COLOR]" , url=sito))
    itemlist.append( Item(channel=__channel__, action="menugeneros", title="[COLOR azure]Per Genere[/COLOR]" , url=sito))
    itemlist.append( Item(channel=__channel__, action="menuanyos"  , title="[COLOR azure]Per Anno[/COLOR]" , url=sito))
    itemlist.append( Item(channel=__channel__, action="search"     , title="[COLOR azure]Cerca Film[/COLOR]" ))
    itemlist.append( Item(channel=__channel__, action="listserie"  , title="[COLOR azure]Serie Tv - Novita'[/COLOR]" , url="http://www.cb01.eu/serietv/" ))
    itemlist.append( Item(channel=__channel__, action="search", title="[COLOR azure]Cerca Serie Tv[/COLOR]" , extra="serie"))
    itemlist.append( Item(channel=__channel__, action="listanime"  , title="[COLOR azure]Anime - Novita'[/COLOR]" , url="http://www.cineblog01.cc/anime/" ))
    itemlist.append( Item(channel=__channel__, action="animegenere"  , title="[COLOR azure]Anime Per Genere[/COLOR]" , url="http://www.cineblog01.cc/anime/" ))
    itemlist.append( Item(channel=__channel__, action="search", title="[COLOR azure]Cerca Anime[/COLOR]" , extra="cartoni"))

    return itemlist

def peliculas(item):
    logger.info("[cineblog01.py] mainlist")
    itemlist = []

    if item.url =="":
        item.url = sito

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    logger.info(data)

    # Extrae las entradas (carpetas)
    patronvideos = '<div class="span4".*?<a.*?<p><img src="([^"]+)".*?'                    
    patronvideos += '<div class="span8">.*?<a href="([^"]+)"> <h1>([^"]+)</h1></a>.*?'
    patronvideos += '<p><strong>.*?</strong>.*?<br />([^"]+)<a href'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for match in matches:
        scrapedtitle = scrapertools.unescape(match[2])
        scrapedurl = urlparse.urljoin(item.url,match[1])
        scrapedthumbnail = urlparse.urljoin(item.url,match[0])
        scrapedthumbnail = scrapedthumbnail.replace(" ", "%20");
        scrapedplot = scrapertools.unescape(match[3])
        scrapedplot = scrapertools.htmlclean(scrapedplot).strip()
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="findvideos" , title=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot, viewmode="movie_with_plot", fanart=scrapedthumbnail))

    # Next page mark
    try:
        bloque = scrapertools.get_match(data,"<div id='wp_page_numbers'>(.*?)</div>")
        patronvideos = '<a href="([^"]+)">></a></li>'
        matches = re.compile (patronvideos, re.DOTALL).findall (data)
        scrapertools.printMatches (matches)
    
        if len(matches)>0:
            scrapedtitle = "[COLOR orange]Successivo>>[/COLOR]"
            scrapedurl = matches[0]
            scrapedthumbnail = ""
            scrapedplot = ""
            if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
    
            itemlist.append( Item(channel=__channel__, action="peliculas" , title=scrapedtitle , url=scrapedurl, thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png", plot=scrapedplot))
    except:
        pass

    return itemlist

def menugeneros(item):
    logger.info("[cineblog01.py] menugeneros")
    itemlist = []
    
    data = scrapertools.cache_page(item.url)
    logger.info(data)

    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data,'<select name="select2"(.*?)</select')
    
    # The categories are the options for the combo  
    patron = '<option value="([^"]+)">([^<]+)</option>'
    matches = re.compile(patron,re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for url,titulo in matches:
        scrapedtitle = titulo
        scrapedurl = urlparse.urljoin(item.url,url)
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="peliculas" , title=scrapedtitle , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot))

    return itemlist


def menuanyos(item):
    logger.info("[cineblog01.py] menuvk")
    itemlist = []
    
    data = scrapertools.cache_page(item.url)
    logger.info(data)
    
    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data,'<select name="select3"(.*?)</select')
    
    # The categories are the options for the combo  
    patron = '<option value="([^"]+)">([^<]+)</option>'
    matches = re.compile(patron,re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for url,titulo in matches:
        scrapedtitle = titulo
        scrapedurl = urlparse.urljoin(item.url,url)
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="peliculas" , title=scrapedtitle , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot))

    return itemlist

# Al llamarse "search" la función, el launcher pide un texto a buscar y lo añade como parámetro
def search(item,texto):
    logger.info("[cineblog01.py] "+item.url+" search "+texto)

    try:

        if item.extra=="serie":
            item.url = "http://www.cb01.org/serietv/?s="+texto
            return listserie(item)
        if item.extra=="cartoni":
            item.url = "http://www.cineblog01.cc/anime/?s="+texto
            return listanime(item)        
        else:
            item.url = "http://www.cb01.org/?s="+texto
            return peliculas(item)

    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []

def listserie(item):
    logger.info("[cineblog01.py] mainlist")
    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    logger.info(data)

    # Extrae las entradas (carpetas)
    patronvideos = '<div class="span4".*?<a.*?<p><img src="(.*?)".*?'                    
    patronvideos += '<div class="span8">.*?<a href="(.*?)">.*?'
    patronvideos += '<h1>(.*?)</h1>(.*?)</a>'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for match in matches:
        scrapedtitle = scrapertools.unescape(match[2])
        scrapedurl = urlparse.urljoin(item.url,match[1])
        scrapedthumbnail = urlparse.urljoin(item.url,match[0])
        scrapedplot = scrapertools.unescape(match[3])
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")

        # Añade al listado de XBMC
        itemlist.append( Item(channel=__channel__, action="findvideos" , title=scrapedtitle , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot))

    # Put the next page mark
    try:
        next_page = scrapertools.get_match(data,"<link rel='next' href='([^']+)'")
        itemlist.append( Item(channel=__channel__, action="listserie" , title="[COLOR orange]Successivo>>[/COLOR]" , url=next_page, thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png", plot=scrapedplot))
    except:
        pass

    return itemlist

def animestream(item):
    logger.info("[cineblog01.py] mainlist")
    itemlist = []

    if item.url =="":
        item.url = sito

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    logger.info(data)

    # Extrae las entradas (carpetas)
    patronvideos  = '<div class="span4"> <a.*?<p><img.*?src="(.*?)".*?'
    patronvideos += '<div class="span8">.*?<a href="(.*?)">.*?'
    patronvideos += '<h1>(.*?)</h1></a>.*?<br>-->(.*?)<br>.*?'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for match in matches:
        scrapedtitle = scrapertools.unescape(match[2])
        scrapedurl = urlparse.urljoin(item.url,match[1])
        scrapedthumbnail = urlparse.urljoin(item.url,match[0])
        scrapedthumbnail = scrapedthumbnail.replace(" ", "%20");
        scrapedplot = scrapertools.unescape(match[3])
        scrapedplot = scrapertools.htmlclean(scrapedplot).strip()
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="findvideos" , title=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot, viewmode="movie_with_plot", fanart=scrapedthumbnail))

    # Next page mark
    try:
        bloque = scrapertools.get_match(data,"<div id='wp_page_numbers'>(.*?)</div>")
        patronvideos = '<a href="([^"]+)">></a></li>'
        matches = re.compile (patronvideos, re.DOTALL).findall (data)
        scrapertools.printMatches (matches)
    
        if len(matches)>0:
            scrapedtitle = "[COLOR orange]Successivo>>[/COLOR]"
            scrapedurl = matches[0]
            scrapedthumbnail = ""
            scrapedplot = ""
            if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
    
            itemlist.append( Item(channel=__channel__, action="peliculas" , title=scrapedtitle , url=scrapedurl, thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png", plot=scrapedplot))
    except:
        pass

    return itemlist

def animegenere(item):
    logger.info("[cineblog01.py] animegenere")
    itemlist = []
    
    data = scrapertools.cache_page(item.url)
    logger.info(data)

    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data,'<select name="select2"(.*?)</select')
    
    # The categories are the options for the combo  
    patron = '<option value="([^"]+)">([^<]+)</option>'
    matches = re.compile(patron,re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for url,titulo in matches:
        scrapedtitle = titulo
        scrapedurl = urlparse.urljoin(item.url,url)
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="animestream" , title=scrapedtitle , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot))

    return itemlist

def listanime(item):
    logger.info("[cineblog01.py] mainlist")
    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    logger.info(data)

    # Extrae las entradas (carpetas)
    patronvideos  = '<div class="span4"> <a.*?<p><img.*?src="(.*?)".*?'
    patronvideos += '<div class="span8">.*?<a href="(.*?)">.*?'
    patronvideos += '<h1>(.*?)</h1></a>.*?<br>-->(.*?)<br>.*?'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for match in matches:
        scrapedthumbnail = urlparse.urljoin(item.url,match[0])
        scrapedurl = urlparse.urljoin(item.url,match[1])
        scrapedtitle = scrapertools.unescape(match[2])
        scrapedplot = scrapertools.unescape(match[3])
        if scrapedplot.startswith(""):
           scrapedplot = scrapedplot[159:]
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")

        # Añade al listado de XBMC
        itemlist.append( Item(channel=__channel__, action="findvideos" , title=scrapedtitle , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot))

    # Put the next page mark
    try:
        next_page = scrapertools.get_match(data,"<link rel='next' href='([^']+)'")
        itemlist.append( Item(channel=__channel__, action="listanime" , title="[COLOR orange]Successivo>>[/COLOR]" , url=next_page, thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png", plot=scrapedplot))
    except:
        pass

    return itemlist

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():
    bien = True
    
    # mainlist
    mainlist_items = mainlist(Item())
    
    # Comprueba que todas las opciones por categorias tengan algo (excepto los buscadores)
    for mainlist_item in mainlist_items:
        if mainlist_item.action.startswith("menu"):
            exec "itemlist = "+mainlist_item.action+"(mainlist_item)"
            
            # Lee la primera categoría sólo
            exec "itemlist2 ="+itemlist[0].action+"(itemlist[0])"
            if len(itemlist2)==0:
                return false

    # Comprueba si alguno de los vídeos de "Novedades" devuelve mirrors
    for mainlist_item in mainlist_items:
        if mainlist_item.action=="peliculas" or mainlist_item.action=="listserie":
            exec "itemlist = "+mainlist_item.action+"(mainlist_item)"
    
            bien = False
            for episodio_item in itemlist:
                from servers import servertools
                mirrors = servertools.find_video_items(item=episodio_item)
                if len(mirrors)>0:
                    bien = True
                    break

    return bien
