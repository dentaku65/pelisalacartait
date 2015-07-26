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

__channel__ = "pianetastreaming"
__category__ = "F"
__type__ = "generic"
__title__ = "pianetastreaming.net (IT)"
__language__ = "IT"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("pelisalacarta.pianetastreaming mainlist")
    itemlist = []
    itemlist.append( Item(channel=__channel__, title="Ultimi Film Inseriti", action="peliculas", url="http://www.pianetastreaming.net/"))
    itemlist.append( Item(channel=__channel__, title="Scegli Per Genere", action="categorias", url="http://www.pianetastreaming.net/"))
    itemlist.append( Item(channel=__channel__, title="Cerca...", action="search"))
    return itemlist

def peliculas(item):
    logger.info("pelisalacarta.pianetastreaming peliculas")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)

    # Extrae las entradas (carpetas)
    patron  = '<div class="moviefilm">.*?<a href="(.*?)">.*?<img src="(.*?)"[^>]+></a>[^>]+[^<]+<a[^>]+>(.*?)</a></div>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        response = urllib2.urlopen(scrapedurl)
        html = response.read()
        start = html.find("Anno:")
        end = html.find("<h2>", start)
        scrapedplot = html[start:end]
        if scrapedplot.startswith(""):
           scrapedplot = scrapedplot[28:]
        #scrapedtitle=scrapertools.decodeHtmlentities(scrapedtitle.replace("http://www.pianetastreaming.tv",""))
        if (DEBUG): logger.info("url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"], title=["+scrapedtitle+"]")
        itemlist.append( Item(channel=__channel__, action="findvideos", url=scrapedurl , thumbnail=scrapedthumbnail , title=scrapedtitle , plot=scrapedplot , folder=True, fanart=scrapedthumbnail) )

    # Extrae el paginador
    patronvideos  = '<a class="nextpostslink" href="(.*?)">&raquo;</a>'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    if len(matches)>0:
        scrapedurl = urlparse.urljoin(item.url,matches[0])
        itemlist.append( Item(channel=__channel__, action="peliculas", title="[COLOR orange]Successivo >>[/COLOR]" , url=scrapedurl , folder=True) )

    return itemlist


def categorias(item):
    logger.info("pelisalacarta.pianetastreaming categorias")
    itemlist = []
    
    data = scrapertools.cache_page(item.url)
    logger.info(data)

    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data,'<ul class="sub-menu">(.*?)</ul>')
    
    # The categories are the options for the combo  
    patron = '<a href="(.*?)">(.*?)</a>'
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
    logger.info("[pianetastreaming.py] "+item.url+" search "+texto)
    item.url = "http://www.pianetastreaming.net/?s="+texto
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
