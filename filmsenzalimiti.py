# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para filmsenzalimiti
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "filmsenzalimiti"
__category__ = "F"
__type__ = "generic"
__title__ = "Film Senza Limiti (IT)"
__language__ = "IT"
__creationdate__ = "20120605"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("[filmsenzalimiti.py] mainlist")
    
    itemlist = []
    itemlist.append( Item(channel=__channel__, title="[COLOR azure]Film Del Cinema[/COLOR]", action="novedades", url="http://www.filmsenzalimiti.co/genere/film", thumbnail="http://dc584.4shared.com/img/XImgcB94/s7/13feaf0b538/saquinho_de_pipoca_01"))
    itemlist.append( Item(channel=__channel__, title="[COLOR azure]Film Dvdrip[/COLOR]", action="novedades", url="http://www.filmsenzalimiti.co/genere/dvd-rip", thumbnail="http://repository-butchabay.googlecode.com/svn/branches/eden/skin.cirrus.extended.v2/extras/moviegenres/Box%20Sets%20HD.png"))
    itemlist.append( Item(channel=__channel__, title="[COLOR azure]Film Sub Ita[/COLOR]", action="novedades", url="http://www.filmsenzalimiti.co/genere/subita", thumbnail="http://i.imgur.com/qUENzxl.png"))
    itemlist.append( Item(channel=__channel__, title="[COLOR azure]Serie TV[/COLOR]", action="novedades", url="http://www.filmsenzalimiti.co/genere/serie-tv", thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/New%20TV%20Shows.png"))
    itemlist.append( Item(channel=__channel__, action="search", title="[COLOR yellow]Cerca...[/COLOR]", thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search" ))
    return itemlist

def categorias(item):
    logger.info("[filmsenzalimiti.py] novedades")
    itemlist = []

    # Descarga la página
    data = scrapertools.cachePage(item.url)
    data = scrapertools.get_match(data,'<li><a href\="\#">Dvdrip per Genere</a>(.*?)</ul>')
    patron = '<li><a href="([^"]+)">([^<]+)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle in matches:
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="novedades", title="[COLOR azure]" + scrapedtitle + "[/COLOR]" , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True) )

    return itemlist


def search(item,texto):
    logger.info("[filmsenzalimiti.py] "+item.url+" search "+texto)
    item.url = "http://www.filmsenzalimiti.co/?s="+texto
    try:
        return novedades(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []


def novedades(item):
    logger.info("[filmsenzalimiti.py] novedades")
    itemlist = []

    # Descarga la página
    data = scrapertools.cachePage(item.url)

    patronvideos  = '<div class="post-item-side"[^<]+'
    patronvideos += '<a href="([^"]+)"[^<]+<img src="([^"]+)"'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for scrapedurl,scrapedthumbnail in matches:
        html = scrapertools.cache_page(scrapedurl)
        start = html.find("</center><br />")
        end = html.find("</p>", start)
        scrapedplot = html[start:end]
        scrapedplot = re.sub(r'<.*?>', '', scrapedplot)
        scrapedplot = scrapertools.decodeHtmlentities(scrapedplot)
        #scrapedplot = ""
        scrapedtitle = scrapertools.get_filename_from_url(scrapedurl).replace("-"," ").replace("/","").replace(".html","").capitalize().strip()
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="findvideos", title="[COLOR azure]" + scrapedtitle + "[/COLOR]" , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True) )

    # Siguiente
    try:
        pagina_siguiente = scrapertools.get_match(data,'class="nextpostslink" rel="next" href="([^"]+)"')
        itemlist.append( Item(channel=__channel__, action="novedades", title="[COLOR orange]Successivo >>[/COLOR]" , url=pagina_siguiente , thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png", folder=True) )
    except:
        pass

    return itemlist

# Verificación automática de canales: Esta función debe devolver "True" si está ok el canal.
def test():
    from servers import servertools
    # mainlist
    mainlist_items = mainlist(Item())
    # Da por bueno el canal si alguno de los vídeos de "Novedades" devuelve mirrors
    items = novedades(mainlist_items[0])
    bien = False
    for singleitem in items:
        mirrors = servertools.find_video_items( item=singleitem )
        if len(mirrors)>0:
            bien = True
            break

    return bien
