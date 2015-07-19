# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para piratestreaming
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "tantifilm"
__category__ = "F,S,A"
__type__ = "generic"
__title__ = "TantiFilm.Net"
__language__ = "IT"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("pelisalacarta.tantifilm mainlist")
    itemlist = []
    itemlist.append( Item(channel=__channel__, title="Ultimi film inseriti", action="peliculas", url="http://www.tantifilm.net/"))
    itemlist.append( Item(channel=__channel__, title="Film HD Streaming Consigliati", action="peliculas", url="http://www.tantifilm.net/watch-genre/hd-alta-qualita/"))
    itemlist.append( Item(channel=__channel__, title="Categorie film", action="categorias", url="http://www.tantifilm.net/"))
    itemlist.append( Item(channel=__channel__, title="Serie TV" , action="peliculas", url="http://www.tantifilm.net/serie-tv/"))
    itemlist.append( Item(channel=__channel__, title="Cerca...", action="search"))
    return itemlist

def peliculas(item):
    logger.info("pelisalacarta.tantifilm peliculas")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)

    # Extrae las entradas (carpetas)
    patron  = '<div class="mediaWrap mediaWrapAlt">\s*'
    patron += '<a href="?([^>"]+)"?.*?title="?([^>"]+)"?.*?<img.*?src="([^>"]+)'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle,scrapedthumbnail in matches:
        scrapedplot = ""
        scrapedtitle=scrapertools.decodeHtmlentities(scrapedtitle.replace("Streaming",""))
        if scrapedtitle.startswith("Permalink to "):
            scrapedtitle = scrapedtitle[13:]
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="findvideos", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True) )

    # Extrae el paginador
    patronvideos  = '<a.*?href="([^"]+)">»</a>'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    if len(matches)>0:
        scrapedurl = urlparse.urljoin(item.url,matches[0])
        itemlist.append( Item(channel=__channel__, action="peliculas", title="[COLOR orange]Avanti>>[/COLOR]" , url=scrapedurl , folder=True) )

    return itemlist

def categorias(item):
    logger.info("pelisalacarta.tantifilm categorias")
    itemlist = []
    
    data = scrapertools.cache_page(item.url)
    logger.info(data)

    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data,'<select class="select_join" onchange="location.href = this.value" size="1" name="linkIole2">(.*?)</select')
    
    # The categories are the options for the combo  
    patron = '<option value="([^"]+)".*?>([^<]+)</a></option>'
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


#def categorias(item):
    logger.info("pelisalacarta.tantifilm categorias")
    itemlist = []
    
    data = scrapertools.cache_page(item.url)
    
    data = scrapertools.find_single_match(data,'<div id="wpwm_genres_widget-3"(.*?)</div>')

    patron = '<ul><li><a href="([^"]+)">([^>"]+)</a></li>'

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

def search(item,texto):
    logger.info("[tantifilm.py] "+item.url+" search "+texto)
    item.url = "http://www.tantifilm.net/?s="+texto
    try:
        return peliculas(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []

def test():
    from servers import servertools
    
    # mainlist
    mainlist_items = mainlist(Item())
    # Da por bueno el canal si alguno de los videos de "Novedades" devuelve mirrors
    novedades_items = peliculas(mainlist_items[0])
    bien = False
    for novedades_item in novedades_items:
        mirrors = servertools.find_video_items( item=novedades_item )
        if len(mirrors)>0:
            bien = True
            break

    return bien
