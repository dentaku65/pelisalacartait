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

__channel__ = "piratestreaming"
__category__ = "F,S,A"
__type__ = "generic"
__title__ = "piratestreaming"
__language__ = "IT"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("[piratestreaming.py] mainlist")
    itemlist = []
    itemlist.append( Item(channel=__channel__, title="Ultimi Aggiunti"     , action="peliculas", url="http://www.piratestreaming.co/film-aggiornamenti.php"))
    itemlist.append( Item(channel=__channel__, title="Per genere" , action="categorias", url="http://www.piratestreaming.co/"))
    itemlist.append( Item(channel=__channel__, title="Serie TV"     , action="peliculas", url="http://www.piratestreaming.co/serietv-aggiornamenti.php"))
    itemlist.append( Item(channel=__channel__, title="Cerca", action="search"))
    return itemlist

def peliculas(item):
    logger.info("pelisalacarta.piratestreaming peliculas")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)

    # Extrae las entradas (carpetas)
    patron  = '<div class="featuredItem">.*?<a href="(.*?)".*?<img src="(.*?)".*?<a href=.*?>(.*?)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        scrapedplot = ""
        logger.info("scrapedurl="+scrapedurl)
        if scrapedtitle.startswith(""):
            scrapedtitle=scrapedtitle[0:]
        #if scrapedurl.startswith("\""):
        #    scrapedurl=scrapedurl[1:-1]
        #logger.info("scrapedurl="+scrapedurl)

        try:
            res = urllib2.urlopen(scrapedurl)
            daa = res.read()
            da = daa.split('justify;">');
            da = da[1].split('</p>')
            scrapedplot = scrapertools.htmlclean(da[0]).strip()
        except:
            scrapedplot= "Trama non disponibile"
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="findvideos", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True) )

    # Extrae el paginador
    patronvideos  = '<td align="center">[^<]+</td>[^<]+<td align="center">\s*<a href="([^"]+)">[^<]+</a>'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    if len(matches)>0:
        scrapedurl = urlparse.urljoin(item.url,matches[0])
        itemlist.append( Item(channel=__channel__, action="peliculas", title="[COLOR orange]Successivo >>[/COLOR]" , url=scrapedurl , folder=True) )

    return itemlist
    
def categorias(item):
    itemlist = []
    data = scrapertools.cache_page(item.url)
    data = scrapertools.get_match(data,'<a href="#">Film</a>[^<]+<ul>(.*?)</ul>')
    patron = '<li><a href="([^"]+)">([^<]+)</a></li>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle in matches:
        scrapedplot = ""
        scrapedthumbnail = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="peliculas", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True) )

    return itemlist

def search(item,texto):
    logger.info("[piratestreaming.py] search "+texto)
    itemlist = []
    texto = texto.replace(" ","%20")
    item.url = "http://www.piratestreaming.co/cerca.php?all="+texto
    item.extra = ""

    try:
        return cerca(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []

def cerca(item):
    itemlist = []
    
    # Descarga la pagina
    data = scrapertools.cache_page(item.url)
    bloque = scrapertools.get_match(data,'<!-- Featured Item -->(.*?)<!-- End of Content -->')
    
    # Extrae las entradas (carpetas)
    patron  = '<b><a href=(.*?)>(.*?)</b>'
    matches = re.compile(patron,re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle in matches:
        scrapedplot = ""
        scrapedthumbnail = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"]")
        itemlist.append( Item(channel=__channel__, action="findvideos", title=scrapedtitle , url=scrapedurl , folder=True) )

    return itemlist



# Verificaciòn automàtica de canales: Esta funciòn debe devolver "True" si estàok el canal.
def test():
    from servers import servertools
    
    # mainlist
    mainlist_items = mainlist(Item())
    # Da por bueno el canal si alguno de los vìdeos de "Novedades" devuelve mirrors
    novedades_items = peliculas(mainlist_items[0])
    bien = False
    for novedades_item in novedades_items:
        mirrors = servertools.find_video_items( item=novedades_item )
        if len(mirrors)>0:
            bien = True
            break

    return bien
