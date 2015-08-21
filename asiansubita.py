# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para asiansubita
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools
from servers import adfly

__channel__ = "asiansubita"
__category__ = "F,A"
__type__ = "generic"
__title__ = "asiansubita"
__language__ = "IT"

sito="http://asiansubita.altervista.org/"

def isGeneric():
    return True

def mainlist( item ):
    logger.info( "pelisalacarta.asiansubita mainlist" )

    itemlist = []

    itemlist.append( Item( channel=__channel__, title="[COLOR azure]Home[/COLOR]", action="peliculas", url=sito, thumbnail="http://dc584.4shared.com/img/XImgcB94/s7/13feaf0b538/saquinho_de_pipoca_01" ) )
    itemlist.append( Item( channel=__channel__, title="[COLOR azure]Genere - Nazione[/COLOR]", action="categorias", url=sito, thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/All%20Movies%20by%20Genre.png" ) )
    itemlist.append( Item( channel=__channel__, title="[COLOR yellow]Cerca...[/COLOR]", action="search", thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search" ) )
    return itemlist

def search( item, texto ):
    logger.info( "[asiansubita.py] " + item.url + " search " + texto )

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
    logger.info( "pelisalacarta.asiansubita peliculas" )

    itemlist = []

    ## Descarga la pagina
    data = scrapertools.cache_page( item.url )

    ## Extrae las entradas (carpetas)
    patron  = '<!-- Post Type 3 -->\s*'
    patron += '<a.*?href="(.*?)" title="(.*?)" rel="bookmark">.*?<img src="(.*?)".*?<div class="entry-summary">\s*'
    patron += '(.*?)<a class="more-link"'

    matches = re.compile( patron, re.DOTALL ).findall( data )

    for scrapedurl,scrapedtitle,scrapedthumbnail,scrapedplot in matches:
        scrapedplot = scrapertools.decodeHtmlentities(scrapedplot)
        title = scrapertools.decodeHtmlentities( scrapedtitle )
 
        itemlist.append( Item( channel=__channel__, action="findvideos", title=title, url=scrapedurl, thumbnail=scrapedthumbnail, fulltitle=title, show=title , plot=scrapedplot , viewmode="movie_with_plot") )


    ## Paginación
    next_page  = scrapertools.find_single_match( data, '<div class="nav-previous"><a href="(.*?)" ><span class="meta-nav">&larr;</span> Articoli precedenti</a></div>' )

    if next_page != "":
        itemlist.append( Item( channel=__channel__, action="peliculas", title="[COLOR orange]Post piu' vecchi >>[/COLOR]", url=next_page, thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png") )

    return itemlist

def categorias(item):
    logger.info("pelisalacarta.asiansubita categorias")

    itemlist = []

    data = scrapertools.cache_page(item.url)

    # The categories are the options for the combo
    patron = '<li id="menu-item-[^>"]+" class="menu-item menu-item-type-taxonomy menu-item-object-category menu-item-[^>"]+"><a href="(.*?)">(.*?)</a></li>'

    matches = re.compile(patron,re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:

        itemlist.append( Item( channel=__channel__, action="peliculas" , title="[COLOR azure]" + scrapedtitle + "[/COLOR]", url=urlparse.urljoin( sito, scrapedurl ) ) )

    return itemlist
	
	
def findvideos( item ):
    logger.info( "[asiansubita.py] findvideos" )

    itemlist = []

    ## Descarga la página
    data = scrapertools.cache_page( item.url )

    ## Extrae las datos
    thumbnail = scrapertools.find_single_match( data, 'src="([^"]+)"[^<]+</p>' )
    plot = scrapertools.decodeHtmlentities(scrapertools.find_single_match( data, '<p style="text-align: justify;">(.*?)</p>' ))

    patron = 'href="(http://adf.ly/[^"]+)" target="_blank">([^<]+)</a>'

    matches = re.compile( patron, re.DOTALL ).findall( data )

    for scrapedurl, scrapedtitle in matches:

        scrapedtitle = scrapertools.decodeHtmlentities( scrapedtitle )
        title = "[" + scrapedtitle + "] " + item.fulltitle

        itemlist.append( Item( channel=__channel__, action="play" , title=title, url=scrapedurl, thumbnail=thumbnail, plot=plot, fulltitle=item.fulltitle, show=item.show ) )

    return itemlist

def play( item ):
    logger.info( "[asiansubita.py] play" )

    data = adfly.get_long_url( item.url )

    itemlist = servertools.find_video_items( data=data )

    for videoitem in itemlist:
        videoitem.title = item.show
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = __channel__

    return itemlist
