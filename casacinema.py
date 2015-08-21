# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para casacinema
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "casacinema"
__category__ = "F,S,A"
__type__ = "generic"
__title__ = "casacinema"
__language__ = "IT"

sito="http://casa-cinema.net/"

def isGeneric():
    return True

def mainlist( item ):
    logger.info( "pelisalacarta.casacinema mainlist" )

    itemlist = []

    itemlist.append( Item( channel=__channel__, title="[COLOR azure]Film - Novita'[/COLOR]", action="peliculas", url=sito, thumbnail="http://dc584.4shared.com/img/XImgcB94/s7/13feaf0b538/saquinho_de_pipoca_01" ) )
    itemlist.append( Item( channel=__channel__, title="[COLOR azure]Categorie[/COLOR]", action="categorias", url=sito, thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/All%20Movies%20by%20Genre.png" ) )
    itemlist.append( Item( channel=__channel__, title="[COLOR azure]Film Sub - Ita[/COLOR]", action="peliculas", url="http://casa-cinema.net/genere/sub-ita", thumbnail="http://i.imgur.com/qUENzxl.png" ) )
    itemlist.append( Item( channel=__channel__, title="[COLOR yellow]Cerca...[/COLOR]", action="search", thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search" ) )
    return itemlist

def search( item, texto ):
    logger.info( "[casacinema.py] " + item.url + " search " + texto )

    item.url = sito + "?s=" + texto

    try:
        return peliculas( item )

    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []

def peliculas( item ):
    logger.info( "pelisalacarta.casacinema peliculas" )

    itemlist = []

    ## Descarga la pagina
    data = scrapertools.cache_page( item.url )

    ## Extrae las entradas (carpetas)
    patron  = '<div class="box-single-movies">\s*'
    patron += '<a href="([^>"]+)".*?title="([^>"]+)" >.*?<img class.*?<img.*?src="([^>"]+)"'

    matches = re.compile( patron, re.DOTALL ).findall( data )

    for scrapedurl,scrapedtitle,scrapedthumbnail in matches:
        title = scrapertools.decodeHtmlentities( scrapedtitle )
        html = scrapertools.cache_page(scrapedurl)
        start = html.find("<div class=\"row content-post\" >")
        end = html.find("<a class=\"addthis_button_facebook_like\" fb:like:layout=\"button_count\"></a>", start)
        scrapedplot = html[start:end]
        scrapedplot = re.sub(r'<.*?>', '', scrapedplot)
        scrapedplot = scrapertools.decodeHtmlentities(scrapedplot)
        itemlist.append( Item( channel=__channel__, action="findvideos", title="[COLOR azure]" + title + "[/COLOR]", url=scrapedurl, thumbnail=scrapedthumbnail, fulltitle=title, show=title , plot=scrapedplot , viewmode="movie_with_plot") )

    ## Paginación
    next_page  = scrapertools.find_single_match( data, 'rel="next" href="([^"]+)"' )

    if next_page != "":
        itemlist.append( Item( channel=__channel__, action="peliculas", title="[COLOR orange]Successivo >>[/COLOR]", url=next_page, thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png") )

    return itemlist

def categorias(item):
    logger.info("pelisalacarta.casacinema categorias")

    itemlist = []

    data = scrapertools.cache_page( item.url )

    # The categories are the options for the combo
    patron = '<td[^<]+<a href="([^"]+)">[^>]+>([^<]+)</a>[^/]+/td>'

    matches = re.compile(patron,re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:

        itemlist.append( Item( channel=__channel__, action="peliculas" , title="[COLOR azure]" + scrapedtitle + "[/COLOR]", url=urlparse.urljoin( sito, scrapedurl ) ) )

    return itemlist
