# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para piratestreaming
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# by dentaku65, DrZ3r0
# ------------------------------------------------------------
import urlparse, urllib2, urllib, re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "documentaristreaming"
__category__ = "F,D"
__type__ = "generic"
__title__ = "documentaristreaming (TV)"
__language__ = "IT"

sito = "http://documentaristreaming.net/"

DEBUG = config.get_setting("debug")


def isGeneric():
    return True


def mainlist(item):
    logger.info("pelisalacarta.documentaristreaming mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Aggiornamenti[/COLOR]",
                     action="peliculas",
                     url=sito,
                     thumbnail="http://dc584.4shared.com/img/XImgcB94/s7/13feaf0b538/saquinho_de_pipoca_01"),
                Item(channel=__channel__,
                     title="[COLOR azure]Categorie[/COLOR]",
                     action="categorias",
                     url=sito,
                     thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/All%20Movies%20by%20Genre.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca...[/COLOR]",
                     action="search",
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search")]

    return itemlist


def peliculas(item):
    logger.info("pelisalacarta.documentaristreaming peliculas")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)


    # Extrae las entradas (carpetas)
    patron = '<div class="vw-block-grid-item">\s*'
    patron += '<div[^>]+>\s*'
    patron += '<a class="vw-post-box-thumbnail" href="(.*?)"[^>]+>\s*'
    patron += '<img.*?src="(.*?)"[^<]+<span[^<]+<[^<]+<[^<]+<[^<]+</a>\s*'
    patron += '<div[^>]+>\s*'
    patron += '<div[^<]+<[^<]+<[^<]+<[^>]+>\s*'
    patron += '<h3[^>]+>\s*'
    patron += '<a[^>]+>\s*'
    patron += '(.*?)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedplot = ""
        if (DEBUG): logger.info(
            "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 viewmode="movie_with_plot",
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True))

    # Extrae el paginador
    patronvideos = '<a class="next page-numbers" href="(.*?)"><i class="icon-iconic-right"></i></a>'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png",
                 folder=True))

    return itemlist


def categorias(item):
    logger.info("pelisalacarta.documentaristreaming categorias")
    itemlist = []

    data = scrapertools.cache_page(item.url)
    logger.info(data)

    # Narrow search by selecting only the combo
    start = data.find('<ul class="sub-menu menu-odd  menu-depth-1">')
    end = data.find('</ul>', start)
    bloque = data[start:end]

    # The categories are the options for the combo  
    patron = '<li class=[^>]+><a.*?href="(.*?)"[^>]+><span>(.*?)</span></a></li>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for url, titulo in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(titulo)
        scrapedurl = urlparse.urljoin(item.url, url)
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info(
            "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot))

    return itemlist

def search(item,texto):
    logger.info("[documentaristreaming.py] "+item.url+" search "+texto)
    item.url = "http://documentaristreaming.net/?s="+texto
    try:
        return peliculas(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []


def play(item):
    logger.info("[documentaristreaming.py] play")
    itemlist = []
    video_url = ""
    server = None

    data = scrapertools.cache_page(item.url)
    url = scrapertools.find_single_match(data, '<iframe\s+(?:width="[^"]*"\s*height="[^"]*"\s*)?src="([^"]+)"')

    if 'youtu' in url:
        data = scrapertools.cache_page(url)
        vid = scrapertools.find_single_match(data, '\'VIDEO_ID\'\s*:\s*"([^"]+)')
        if vid != "":
            video_url = "http://www.youtube.com/watch?v=%s" % vid
            server = 'youtube'
    elif 'rai.tv' in url:
        data = scrapertools.cache_page(url)
        video_url = scrapertools.find_single_match(data, '<meta\s+name="videourl_m3u8"\s*content="([^"]+)"')

    if video_url != "":
        item.url = video_url
        item.server = server
        itemlist.append(item)

    return itemlist

