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

__channel__ = "ildocumento"
__category__ = "F,D"
__type__ = "generic"
__title__ = "ildocumento (TV)"
__language__ = "IT"

sito="http://ildocumento.it/"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("pelisalacarta.ildocumento mainlist")
    itemlist = []
    itemlist.append( Item(channel=__channel__, title="[COLOR azure]Aggiornamenti[/COLOR]", action="peliculas", url=sito,thumbnail="http://dc584.4shared.com/img/XImgcB94/s7/13feaf0b538/saquinho_de_pipoca_01"))
#    itemlist.append( Item(channel=__channel__, title="[COLOR azure]Categorie[/COLOR]", action="categorias", url=sito, thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/All%20Movies%20by%20Genre.png"))
    return itemlist

def peliculas(item):
    logger.info("pelisalacarta.ildocumento peliculas")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)

    # Extrae las entradas (carpetas)
    patron  = '<h2 class="entry-title"><a href="(.*?)".*?>(.*?)</a></h2><p.*?<.*?/p>.*?><p>(.*?)</p></p></div></div>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle,scrapedplot in matches:
        scrapedthumbnail = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="findvideos", title="[COLOR azure]" + scrapedtitle + "[/COLOR]", url=scrapedurl , viewmode="movie_with_plot", thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True) )

    # Extrae el paginador
    patronvideos  = '...</span><a class="nextpostslink" rel="next" href="(.*?)">»'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    if len(matches)>0:
        scrapedurl = urlparse.urljoin(item.url,matches[0])
        itemlist.append( Item(channel=__channel__, action="peliculas", title="[COLOR orange]Successivo >>[/COLOR]" , url=scrapedurl , thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png", folder=True) )

    return itemlist

def categorias(item):
    logger.info("pelisalacarta.ildocumento categorias")
    itemlist = []
    
    data = scrapertools.cache_page(item.url)
    logger.info(data)

    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data,'<ul class="sub-menu sub-menu-2">(.*?)<div id="wrapper">')
    
    # The categories are the options for the combo  
    patron = '<li.*?><a href="(.*?)">.*?>(.*?)<.*?/li>'
    matches = re.compile(patron,re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for url,titulo in matches:
        scrapedtitle = titulo
        scrapedurl = urlparse.urljoin(item.url,url)
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="peliculas" , title="[COLOR azure]" + scrapedtitle + "[/COLOR]", url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot))

    return itemlist

def search(item,texto):
    logger.info("[ildocumento.py] "+item.url+" search "+texto)
    item.url = "http://www.ildocumento.tv/index.php/?s="+texto
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
