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

__channel__ = "hubberfilm"
__category__ = "F,S"
__type__ = "generic"
__title__ = "hubberfilm (IT)"
__language__ = "IT"
sito="http://hubberfilm.org/"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("pelisalacarta.hubberfilm mainlist")
    itemlist = []
    itemlist.append( Item(channel=__channel__, title="Ultimi film inseriti", action="peliculas", url=sito))
    itemlist.append( Item(channel=__channel__, title="Serie TV" , action="peliculas", url=sito+"index.php?h=t&tipo=home&pagina=1"))
    itemlist.append( Item(channel=__channel__, title="Anime" , action="peliculas", url=sito+"?h=a&tipo=popolari&pagina=1"))
    itemlist.append( Item(channel=__channel__, title="Cerca...", action="search"))
    return itemlist

def peliculas(item):
    logger.info("pelisalacarta.hubberfilm peliculas")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)

    # Extrae las entradas (carpetas)
    patron = '<!-- Stampo i dati -->.*?<a href="(.*?)">.*?title="(.*?)">.*?<img.*?src="(.*?)">'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle,scrapedthumbnail in matches:
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="findvideos", title=scrapedtitle , url=sito+scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True) )

    # Extrae el paginador
    try:
        bloque = scrapertools.get_match(data,'<div id="listaPagine">(.*?)<!-- Barra laterale destra -->')
        patronvideos = '</a><a href="([^"]+)"><div class="non">></div></a>.*?</div>'
        matches = re.compile (patronvideos, re.DOTALL).findall (data)
        scrapertools.printMatches (matches)
    
        if len(matches)>0:
            scrapedtitle = "[COLOR orange]Successivo>>[/COLOR]"
            scrapedurl = matches[0]
            scrapedthumbnail = ""
            scrapedplot = ""
            if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
    
            itemlist.append( Item(channel=__channel__, action="peliculas" , title="[COLOR orange]Avanti >>>[/COLOR]" , url=sito+scrapedurl , folder=True))
    except:
        pass

    return itemlist

def search(item,texto):
    logger.info("[hubberfilm.py] "+item.url+" search "+texto)
    item.url = "http://hubberfilm.org/index.php?h=c&cerca="+texto
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
