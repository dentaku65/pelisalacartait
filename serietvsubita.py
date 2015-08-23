# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para serietvsubita
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "serietvsubita"
__category__ = "F,S,D"
__type__ = "generic"
__title__ = "serietvsubita"
__language__ = "IT"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("pelisalacarta.channels.serietvsubita mainlist")

    itemlist = []
    itemlist.append( Item(channel=__channel__, action="episodios" , title="[COLOR azure]Novità[/COLOR]" , url="http://serietvsubita.net/", thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/New%20TV%20Shows.png", folder=True))
    itemlist.append( Item(channel=__channel__, action="series"    , title="[COLOR azure]Indice A-Z[/COLOR]" , url="http://serietvsubita.net/", thumbnail="http://repository-butchabay.googlecode.com/svn/branches/eden/skin.cirrus.extended.v2/extras/moviegenres/A-Z.png", folder=True))
    itemlist.append( Item(channel=__channel__, action="search"    , title="[COLOR yellow]Cerca...[/COLOR]", thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search", folder=True))
    return itemlist

def search(item,texto):
    logger.info("pelisalacarta.channels.serietvsubita search")
    item.url="http://serietvsubita.net/?s="+texto+"&op.x=0&op.y=0"

    try:
        return episodios(item)
    # Se captura la excepci?n, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []

def series(item):
    logger.info("pelisalacarta.channels.serietvsubita series")
    itemlist = []

    data = scrapertools.cachePage(item.url)
    logger.info("data="+data)

    data = scrapertools.find_single_match(data,'<li id="widget_categories" class="widget png_scale"><h2 class="blocktitle"><span>Serie</span>(.*?)</ul>')
    logger.info("data="+data)

    patron  = '<li class="cat-item[^<]+<a href="([^"]+)[^>]+>([^<]+)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        thumbnail = ""
        title = scrapedtitle.strip()
        url = urlparse.urljoin(item.url,scrapedurl)
        plot = ""

        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="episodios", title="[COLOR azure]" + title + "[/COLOR]", url=url , thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/New%20TV%20Shows.png", folder=True))

    ## paginación
    patron = '<div id="navigation">.*?\d+</a> <a href="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl in matches:
        itemlist.append( Item(channel=__channel__, title="[COLOR orange]Episodi precedenti...[/COLOR]", url=scrapedurl, action="series", extra=item.extra, thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png") )


    return itemlist

def episodios(item):
    logger.info("pelisalacarta.channels.serietvsubita episodios")
    itemlist = []

    data = scrapertools.cachePage(item.url)
    logger.info("data="+data)

    patron  = '</div><div class="clear"></div>.*?'
    patron += '<a href="([^"]+)" title="([^"]+)".*?<img.*?src="(.*?)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle,scrapedthumbnail in matches:
        scrapedplot = ""
        scrapedtitle=scrapertools.decodeHtmlentities(scrapedtitle.replace("Streaming",""))
        if scrapedtitle.startswith("Link to "):
            scrapedtitle = scrapedtitle[8:]
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="findvideos", title="[COLOR azure]" + scrapedtitle + "[/COLOR]" , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True) )

    ## paginación
    patron = '<div id="navigation">.*?\d+</a> <a href="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl in matches:
        itemlist.append( Item(channel=__channel__, title="[COLOR orange]Episodi precedenti...[/COLOR]", url=scrapedurl, action="episodios", extra=item.extra, thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png") )

    return itemlist
