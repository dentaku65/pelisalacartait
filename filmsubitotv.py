# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para filmsubito.tv
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse
import re
import sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "filmsubitotv"
__category__ = "F,A,S"
__type__ = "generic"
__title__ = "FilmSubito.tv"
__language__ = "IT"

sito="http://www.filmsubito.tv/"

DEBUG = config.get_setting("debug")


def isGeneric():
    return True


def mainlist(item):
    logger.info("pelisalacarta.filmsubitotv mainlist")
    itemlist = []
    itemlist.append( Item(channel=__channel__, title="[COLOR azure]Film - Novità[/COLOR]", action="peliculas", url=sito+"film-2015-streaming.html?&page=2", thumbnail="http://dc584.4shared.com/img/XImgcB94/s7/13feaf0b538/saquinho_de_pipoca_01"))
    itemlist.append( Item(channel=__channel__, title="[COLOR azure]Film per Genere[/COLOR]", action="genere", url=sito ))
    itemlist.append( Item(channel=__channel__, title="[COLOR azure]Film per Anno[/COLOR]", action="anno", url=sito ))
    itemlist.append( Item(channel=__channel__, title="[COLOR azure]Serie TV degli anni '80[/COLOR]", action="serie80", url=sito ))
    itemlist.append( Item(channel=__channel__, title="[COLOR azure]Cartoni animati degli anni '80[/COLOR]", action="cartoni80", url=sito ))
    itemlist.append( Item(channel=__channel__, title="[COLOR azure]Documentari[/COLOR]", action="documentari", url=sito ))
    itemlist.append( Item(channel=__channel__, title="[COLOR yellow]Cerca...[/COLOR]", action="search", thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search"))

    return itemlist

def search(item,texto):
    logger.info("[filmsubitotv.py] "+item.url+" search "+texto)
    item.url = "http://www.filmsubito.tv/search.php?keywords="+texto
    try:
        return peliculas(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []

def peliculas(item):
    logger.info("pelisalacarta.filmsubitotv peliculas")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)

    # Extrae las entradas (carpetas)
    patron = '</span>.*?<a href="(.*?)" class="pm-thumb-fix pm-thumb-145">.*?><img src="(.*?)" alt="(.*?)" width="145">'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        title = scrapertools.decodeHtmlentities( scrapedtitle )
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="findvideos", title=title, url=scrapedurl , thumbnail=scrapedthumbnail, folder=True, fanart=scrapedthumbnail) )

    # Extrae el paginador
    patronvideos = '<a href="([^"])">&raquo;</a>'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    if len(matches)>0:
        scrapedurl = urlparse.urljoin(item.url,matches[0])
        itemlist.append( Item(channel=__channel__, extra=item.extra, action="peliculas", title="[COLOR orange]Successivo>>[/COLOR]" , url=scrapedurl , thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png", folder=True) )

    return itemlist

def genere(item):
    logger.info("[itafilmtv.py] genere")
    itemlist = []

    data = scrapertools.cachePage(item.url)
    logger.info("data="+data)

    data = scrapertools.find_single_match(data,'<a href="#" class="dropdown-toggle wide-nav-link" data-toggle="dropdown">Genere <b class="caret"></b></a>(.*?)<li><a href="http://www.filmsubito.tv/film-2015-streaming.html" class="wide-nav-link">Novità</a></li>')
    logger.info("data="+data)

    patron  = '<a.*?href="(.*?)" class=".*?>(.*?)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle in matches:
        title = scrapertools.decodeHtmlentities( scrapedtitle )
        itemlist.append( Item(channel=__channel__, action="peliculas", title=title, url=scrapedurl, folder=True))

    return itemlist

def serie80(item):
    logger.info("[itafilmtv.py] genere")
    itemlist = []

    data = scrapertools.cachePage(item.url)
    logger.info("data="+data)

    data = scrapertools.find_single_match(data,'<a href="#" class="dropdown-toggle wide-nav-link" data-toggle="dropdown">Serie anni 80<b class="caret"></b></a>(.*?)<li class="dropdown">')
    logger.info("data="+data)

    patron  = '<a.*?href="(.*?)">(.*?)</a></li>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle in matches:
        title = scrapertools.decodeHtmlentities( scrapedtitle )
        itemlist.append( Item(channel=__channel__, action="peliculas", title=title, url=scrapedurl, folder=True))

    return itemlist

def anno(item):
    logger.info("[itafilmtv.py] genere")
    itemlist = []

    data = scrapertools.cachePage(item.url)
    logger.info("data="+data)

    data = scrapertools.find_single_match(data,'<a href="#" class="dropdown-toggle wide-nav-link" data-toggle="dropdown">Anno<b class="caret"></b></a>(.*?)<li class="dropdown">')
    logger.info("data="+data)

    patron  = '<a.*?href="(.*?)">(.*?)</a></li>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle in matches:
        title = scrapertools.decodeHtmlentities( scrapedtitle )
        itemlist.append( Item(channel=__channel__, action="peliculas", title=title, url=scrapedurl, folder=True))

    return itemlist

def cartoni80(item):
    logger.info("[itafilmtv.py] genere")
    itemlist = []

    data = scrapertools.cachePage(item.url)
    logger.info("data="+data)

    data = scrapertools.find_single_match(data,'<a href="#" class="dropdown-toggle wide-nav-link" data-toggle="dropdown">Cartoni anni 80<b class="caret"></b></a>(.*?)<li class="dropdown">')
    logger.info("data="+data)

    patron  = '<a.*?href="(.*?)">(.*?)</a></li>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle in matches:
        title = scrapertools.decodeHtmlentities( scrapedtitle )
        itemlist.append( Item(channel=__channel__, action="peliculas", title=title, url=scrapedurl, folder=True))

    return itemlist

def documentari(item):
    logger.info("[itafilmtv.py] genere")
    itemlist = []

    data = scrapertools.cachePage(item.url)
    logger.info("data="+data)

    data = scrapertools.find_single_match(data,'<a href="#" class="dropdown-toggle wide-nav-link" data-toggle="dropdown">Documentari<b class="caret"></b></a>(.*?)<li class="dropdown">')
    logger.info("data="+data)

    patron  = '<a.*?href="(.*?)">(.*?)</a></li>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle in matches:
        title = scrapertools.decodeHtmlentities( scrapedtitle )
        itemlist.append( Item(channel=__channel__, action="peliculas", title=title, url=scrapedurl, folder=True))

    return itemlist

def serie(item):
    logger.info("pelisalacarta.filmsubitotv peliculas")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)

    # Extrae las entradas (carpetas)
    patron = '</span>.*?<a href="(.*?)" class="pm-thumb-fix pm-thumb-145">.*?"><img.*?src="(.*?)" title="Young and Hungry " alt="(.*?)" width="145">'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        title = scrapertools.decodeHtmlentities( scrapedtitle )
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="findvideos", title=title, url=scrapedurl , thumbnail=scrapedthumbnail, folder=True, fanart=scrapedthumbnail) )

    # Extrae el paginador
    patronvideos = '<a href="([^"])">&raquo;</a>'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    if len(matches)>0:
        scrapedurl = urlparse.urljoin(item.url,matches[0])
        itemlist.append( Item(channel=__channel__, extra=item.extra, action="peliculas", title="[COLOR orange]Successivo>>[/COLOR]" , url=scrapedurl , thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png", folder=True) )

    return itemlist
