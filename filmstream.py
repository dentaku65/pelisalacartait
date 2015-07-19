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

__channel__ = "filmstream"
__category__ = "F"
__type__ = "generic"
__title__ = "Film-stream.org (IT)"
__language__ = "IT"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("pelisalacarta.filmstream mainlist")
    itemlist = []
    itemlist.append( Item(channel=__channel__, title="Ultimi film inseriti", action="peliculas", url="http://film-stream.org/"))
    itemlist.append( Item(channel=__channel__, title="Categorie film", action="categorias", url="http://film-stream.org/"))
    itemlist.append( Item(channel=__channel__, title="Cerca...", action="search"))
    return itemlist

def categorias(item):
    itemlist = []
    
    # Descarga la pagina
    data = scrapertools.cache_page(item.url)
    bloque = scrapertools.get_match(data,'<a href=".*?" title="Categories">Categories</a><ul>(.*?)</ul>')
    
    # Extrae las entradas (carpetas)
    patron  = '<a href="(.*?)" >(.*?)</a>'
    matches = re.compile(patron,re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle in matches:
        scrapedplot = ""
        scrapedthumbnail = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"]")
        itemlist.append( Item(channel=__channel__, action="peliculas", title=scrapedtitle , url=scrapedurl , folder=True) )

    return itemlist

def search(item,texto):
    logger.info("[filmstream.py] "+item.url+" search "+texto)
    item.url = "http://film-stream.org/"+texto
    try:
        return peliculas(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []

def peliculas(item):
    logger.info("pelisalacarta.filmstream peliculas")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)

    # Extrae las entradas (carpetas)
    patron  = '<div class="galleryitem".*?>\s*'
    patron += '<a href="?([^>"]+)"?.*?title="?([^>"]+)"?.*?<img.*?src="([^>"]+)'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle,scrapedthumbnail in matches:
        scrapedplot = ""
        scrapedtitle=scrapertools.decodeHtmlentities(scrapedtitle.replace("Streaming",""))
        if scrapedtitle.startswith("Permalink to "):
            scrapedtitle = scrapedtitle[8:]
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="findvideos", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True) )

    # Extrae el paginador
    patronvideos  = '<a href="([^"]+)"  >>>> Post più vecchi >>></a>'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    if len(matches)>0:
        scrapedurl = urlparse.urljoin(item.url,matches[0])
        itemlist.append( Item(channel=__channel__, action="peliculas", title="Next Page >>" , url=scrapedurl , folder=True) )

    return itemlist

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
