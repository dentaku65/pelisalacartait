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

__channel__ = "italianstream"
__category__ = "F,S"
__type__ = "generic"
__title__ = "Italian-Stream (IT)"
__language__ = "IT"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("pelisalacarta.italianstream mainlist")
    itemlist = []
    itemlist.append( Item(channel=__channel__, title="Al Cinema", action="peliculas", url="http://italian-stream.tv/category/news/"))
    itemlist.append( Item(channel=__channel__, title="HD Quality", action="peliculas", url="http://italian-stream.tv/category/dvd-rip/"))
    itemlist.append( Item(channel=__channel__, title="Serie TV", action="peliculas", url="http://italian-stream.tv/category/serie-tv/"))
    itemlist.append( Item(channel=__channel__, title="Categorie", action="categorias", url="http://italian-stream.tv/categorie-film/"))
    itemlist.append( Item(channel=__channel__, title="Cerca...", action="search"))
    return itemlist

def peliculas(item):
    logger.info("pelisalacarta.italianstream peliculas")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)

    # Extrae las entradas (carpetas)
    patron = '<div class="arch-thumb">[^<]+<a href="(.*?)" title="(.*?)"><img[^src]+src="(.*?)"[^<]+</a>[^<]+</div>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle,scrapedthumbnail in matches:
        response = urllib2.urlopen(scrapedurl)
        html = response.read()
        start = html.find("Trama:")
        end = html.find("</div>", start)
        scrapedplot = html[start:end]
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="findvideos", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True, fanart=scrapedthumbnail) )

    # Extrae el paginador
    patronvideos  = '<link rel="next" href="(.*?)" />'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    if len(matches)>0:
        scrapedurl = urlparse.urljoin(item.url,matches[0])
        itemlist.append( Item(channel=__channel__, action="peliculas", title="[COLOR orange]Avanti>>[/COLOR]" , url=scrapedurl , folder=True) )

    return itemlist

def categorias(item):
    logger.info("pelisalacarta.italianstream categorias")
    itemlist = []
    
    data = scrapertools.cache_page(item.url)
    logger.info(data)

    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data,'<ul class="sub-menu">(.*?)</ul>')
    
    # The categories are the options for the combo  
    patron = '<li[^7]+[^<]+<a href="(.*?)">[^>]+>(.*?)</span></a></li>'
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
    logger.info("[italianstream.py] "+item.url+" search "+texto)
    item.url = "http://italian-stream.tv/?s="+texto
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
