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

__channel__ = "italiaserie"
__category__ = "F"
__type__ = "generic"
__title__ = "italiaserie"
__language__ = "IT"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("pelisalacarta.filmpertutti mainlist")
    itemlist = []
    itemlist.append( Item(channel=__channel__, title="[COLOR floralwhite]Home[/COLOR]", action="peliculas", url="http://www.italiaserie.co/"))
    #itemlist.append( Item(channel=__channel__, title="Home", action="peliculas", url="http://www.italiaserie.co/genere/serie-tv/"))
    #itemlist.append( Item(channel=__channel__, title="Lista Completa", action="series", url="http://www.italiaserie.co/lista-completa/"))
    #itemlist.append( Item(channel=__channel__, title="Serie TV" , action="peliculas", url="http://www.italiaserie.co/"))
    #itemlist.append( Item(channel=__channel__, title="Anime Cartoon Italiani", action="peliculas", url="http://www.italiaserie.co/"))
    itemlist.append( Item(channel=__channel__, title="[COLOR yellow]Cerca...[/COLOR]", action="search"))
    return itemlist

def peliculas(item):
    logger.info("pelisalacarta.italiaserie peliculas")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)

    # Extrae las entradas (carpetas)
    patron  = '<div class="post-thumb">\s*'
    patron += '<a href="?([^>"]+)"?.*?title="?([^>"]+)"?.*?<img.*?src="([^>"]+)'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle,scrapedthumbnail in matches:
        scrapedplot = ""
        scrapedtitle=scrapertools.decodeHtmlentities(scrapedtitle.replace("Streaming",""))
        if scrapedtitle.startswith("Link to "):
            scrapedtitle = scrapedtitle[8:]
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="findvideos", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True) )

    # Extrae el paginador
    patronvideos  = '<a class="next page-numbers" href="([^"]+)">Next &raquo;</a>'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    if len(matches)>0:
        scrapedurl = urlparse.urljoin(item.url,matches[0])
        itemlist.append( Item(channel=__channel__, action="peliculas", title="[COLOR orange]Next Page >>[/COLOR]" , url=scrapedurl , folder=True) )

    return itemlist

def series(item):
    logger.info("pelisalacarta.italiaserie series")
    itemlist = []

    data = scrapertools.cachePage(item.url)
    logger.info("data="+data)

    data = scrapertools.find_single_match(data,'<div class="ddsg-wrapper">\s*')
    logger.info("data="+data)

    patron  = '<a href="?([^>"]+)"?.*?title="?([^>"]+)">?([^>"]+)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle in matches:

        thumbnail = ""
        title = scrapedtitle.strip()
        url = urlparse.urljoin(item.url,scrapedurl)
        plot = ""

        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="episodios", title=title , fulltitle = title, url=url , thumbnail=thumbnail , plot=plot , folder=True, show=title))

    return itemlist

def search(item,texto):
    logger.info("[italiaserie.py] "+item.url+" search "+texto)
    item.url = "http://www.italiaserie.co/?s="+texto
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
