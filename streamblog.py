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

__channel__ = "streamblog"
__category__ = "F"
__type__ = "generic"
__title__ = "streamblog (IT)"
__language__ = "IT"

site="http://www.streamblog.tv"

headers = [
    ['Host','www.streamblog.tv'],
    ['User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0'],
    ['Accept-Encoding','gzip, deflate'],
    ['Cookie','']
]

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("pelisalacarta.streamblog mainlist")
    itemlist = []
    itemlist.append( Item(channel=__channel__, title="[COLOR azure]Novita'[/COLOR]", action="peliculas", url="http://www.streamblog.tv/"))
    itemlist.append( Item(channel=__channel__, title="[COLOR azure]Categorie[/COLOR]", action="categorias", url="http://www.streamblog.tv/"))
    itemlist.append( Item(channel=__channel__, title="[COLOR azure]Serie TV[/COLOR]", action="peliculas", url="http://www.streamblog.tv/serie-tv/"))
    itemlist.append( Item(channel=__channel__, title="[COLOR azure]Animazione[/COLOR]", action="peliculas", url="http://www.streamblog.tv/animazione/"))
    #itemlist.append( Item(channel=__channel__, title="[COLOR azure]Cerca...[/COLOR]", action="search"))

    
    return itemlist

def categorias(item):
    logger.info("pelisalacarta.streamblog categorias")
    itemlist = []
    
    data = scrapertools.cache_page(item.url)
    logger.info(data)

    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data,'<li class="drop"><a href="#" class="navlink">(.*?)<div class="bl_search">')
    
    # The categories are the options for the combo
    patron = '<li><a href="(.*?)">(.*?)</a></li>'
    matches = re.compile(patron,re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for url,titulo in matches:
        scrapedtitle = titulo
        scrapedurl = urlparse.urljoin(item.url,url)
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="peliculas" , title="[COLOR azure]"+scrapedtitle+"[/COLOR]" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot))

    return itemlist

def search(item,texto):
    logger.info("[streamblog.py] "+item.url+" search "+texto)
    item.url = "http://www.streamblog.tv/index.php?do=search"+texto
    try:
        return peliculas(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []

def peliculas(item):
    logger.info("pelisalacarta.streamblog peliculas")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url, headers=headers)

    # Extrae las entradas (carpetas)
    patron  = '<div class="poster"><a href="(.*?)"><img src="(.*?)" alt="(.*?)".*?</div>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        response = urllib2.urlopen(scrapedurl)
        html = response.read()
        start = html.find("<div class=\"fstory_descr clear decor\">")
        end = html.find("<div class=\"fstory_treyler decor\">", start)
        scrapedplot = html[start:end]
        scrapedplot = re.sub(r'<.*?>', '', scrapedplot)
        #scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="findvideos", title="[COLOR azure]"+scrapedtitle+"[/COLOR]" , url=scrapedurl , thumbnail=site+scrapedthumbnail , plot=scrapedplot , folder=True, fanart=site+scrapedthumbnail) )

    # Extrae el paginador
    patronvideos  = '<div class="navigation".*?<span.*?/span>.*?<a href="(.*?)">'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    if len(matches)>0:
        scrapedurl = urlparse.urljoin(item.url,matches[0])
        itemlist.append( Item(channel=__channel__, action="peliculas", title="[COLOR orange]Avanti >>[/COLOR]" , url=scrapedurl , folder=True) )

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
