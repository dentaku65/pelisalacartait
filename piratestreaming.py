# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para piratestreaming
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse
import urllib2
import re
import sys

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
    itemlist.append( Item(channel=__channel__, title="[COLOR azure]Aggiornamenti[/COLOR]" , action="peliculas", url="http://www.piratestreaming.co/film-aggiornamenti.php", thumbnail="http://dc584.4shared.com/img/XImgcB94/s7/13feaf0b538/saquinho_de_pipoca_01" ))
    itemlist.append( Item(channel=__channel__, title="[COLOR azure]Contenuti per Genere[/COLOR]" , action="categorias", url="http://www.piratestreaming.co/", thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/All%20Movies%20by%20Genre.png"))
    itemlist.append( Item(channel=__channel__, title="[COLOR azure]Archivio Serie TV[/COLOR]" , action="categoryarchive", url="http://www.piratestreaming.co/archivio-serietv.php", thumbnail="http://repository-butchabay.googlecode.com/svn/branches/eden/skin.cirrus.extended.v2/extras/moviegenres/TV%20Series.png"))
    itemlist.append( Item(channel=__channel__, title="[COLOR azure]Serie TV[/COLOR]" , extra="serie", action="peliculas", url="http://www.piratestreaming.co/serietv-aggiornamenti.php", thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/New%20TV%20Shows.png"))
    itemlist.append( Item(channel=__channel__, title="[COLOR yellow]Cerca...[/COLOR]", action="search", thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search"))
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
        scrapedtitle="[COLOR azure]" + scrapedtitle + "[/COLOR]"
        logger.info("scrapedurl="+scrapedurl)
        if scrapedtitle.startswith(""):
            scrapedtitle=scrapedtitle[0:]

        try:
            res = urllib2.urlopen(scrapedurl)
            daa = res.read()
            da = daa.split('justify;">')
            da = da[1].split('</p>')
            scrapedplot = scrapertools.htmlclean(da[0]).strip()
        except:
            scrapedplot= "Trama non disponibile"
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="findvid_serie" if item.extra == "serie" else "findvideos", title="[COLOR azure]" + scrapedtitle + "[/COLOR]" , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True) )

    # Extrae el paginador
    patronvideos  = '<td align="center">[^<]+</td>[^<]+<td align="center">\s*<a href="([^"]+)">[^<]+</a>'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    if len(matches)>0:
        scrapedurl = urlparse.urljoin(item.url,matches[0])
        itemlist.append( Item(channel=__channel__,  extra=item.extra, action="peliculas", title="[COLOR orange]Successivo >>[/COLOR]" , url=scrapedurl , thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png", folder=True) )

    return itemlist
    
def categorias(item):
    itemlist = []
    data = scrapertools.cache_page(item.url)
    data = scrapertools.get_match(data,'<a href="#">Film</a>[^<]+<ul>(.*?)</ul>')
    patron = '<li><a href="([^"]+)">([^<]+)</a></li>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle in matches:
        scrapedtitle="[COLOR azure]" + scrapedtitle + "[/COLOR]"
        scrapedplot = ""
        scrapedthumbnail = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="peliculas", title="[COLOR azure]" + scrapedtitle + "[/COLOR]", url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True) )

    return itemlist


def categoryarchive(item):
    itemlist = []
    data = scrapertools.cache_page(item.url)
    data = scrapertools.get_match(data,'<b>0-9</b><hr />(.*?)<div class="clear"></div>')
    patron = '<a href=([^>]+)>([^<]+)</a><br />'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle in matches:
        scrapedtitle="[COLOR azure]" + scrapedtitle + "[/COLOR]"
        scrapedplot = ""
        scrapedthumbnail = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="findvid_serie", title="[COLOR azure]" + scrapedtitle + "[/COLOR]", url=scrapedurl , thumbnail="http://repository-butchabay.googlecode.com/svn/branches/eden/skin.cirrus.extended.v2/extras/moviegenres/TV%20Series.png" , plot=scrapedplot , folder=True) )

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
        itemlist.append( Item(channel=__channel__, action="findvideos",title="[COLOR azure]" + scrapedtitle + "[/COLOR]" , url=scrapedurl , folder=True) )

    return itemlist


def findvid_serie(item):
    logger.info("[piratestreaming.py] findvideos")

    itemlist = []

    ## Descarga la página
    data = scrapertools.cache_page(item.url)
    data = scrapertools.decodeHtmlentities(data)

    patron1 = '<span style="font-size:12px;"><span style="font-family:\s*arial,\s*helvetica,\s*sans-serif;\s*">(.+?)</a></span></span>'
    matches1 = re.compile(patron1, re.DOTALL).findall(data)
    for match1 in matches1:
        for data in match1.split('<br />'):
            ## Extrae las entradas
            scrapedtitle = data.split('<a ')[0]
            scrapedtitle = re.sub(r'<[^>]*>', '', scrapedtitle).strip()
            li = servertools.find_video_items(data=data)

            for videoitem in li:
                videoitem.title = scrapedtitle + videoitem.title
                videoitem.fulltitle = item.fulltitle
                videoitem.thumbnail = item.thumbnail
                videoitem.show = item.show
                videoitem.plot = item.plot
                videoitem.channel = __channel__

            itemlist.extend(li)

    if len(itemlist) == 0:
        patron2 = '<a rel="nofollow" target="_blank" href="([^"]+)">([^<]+)</a><br />'
        for data, scrapedtitle in re.compile(patron2, re.DOTALL).findall(data):
            li = servertools.find_video_items(data=data)

            for videoitem in li:
                videoitem.title = scrapedtitle + videoitem.title
                videoitem.fulltitle = item.fulltitle
                videoitem.thumbnail = item.thumbnail
                videoitem.show = item.show
                videoitem.plot = item.plot
                videoitem.channel = __channel__

            itemlist.extend(li)

    return itemlist
