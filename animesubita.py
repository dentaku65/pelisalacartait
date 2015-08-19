# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para animesubita
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "animesubita"
__category__ = "A"
__type__ = "generic"
__title__ = "animesubita"
__language__ = "IT"

sito="http://www.animesubita.info/"

headers = [
    ['Host','www.animesubita.info'],
    ['User-Agent','Mozilla/5.0 (Windows NT 6.3; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0'],
    ['Accept-Encoding','gzip, deflate']
]

def isGeneric():
    return True

def mainlist( item ):
    logger.info( "pelisalacarta.animesubita mainlist" )

    itemlist = []

    itemlist.append( Item( channel=__channel__, title="[COLOR azure]Anime - Novita'[/COLOR]", action="novedades", url=sito, thumbnail="http://repository-butchabay.googlecode.com/svn/branches/eden/skin.cirrus.extended.v2/extras/moviegenres/Anime.png" ) )
    itemlist.append( Item( channel=__channel__, title="[COLOR azure]Anime - Per Genere[/COLOR]", action="categorias", url=sito+"cerca-per-genere/", thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/Genre.png" ) )
    itemlist.append( Item( channel=__channel__, title="[COLOR azure]Anime - Lista A-Z[/COLOR]", action="categorias", url=sito+"lista-anime-streaming/", thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/A-Z.png") )
    itemlist.append( Item( channel=__channel__, title="[COLOR yellow]Cerca Anime...[/COLOR]", action="search", thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search" ) )

    return itemlist

def novedades( item ):
    logger.info( "pelisalacarta.animesubita peliculas" )

    itemlist = []

    ## Descarga la pagina
    data = scrapertools.cache_page( item.url )

    ## Extrae las entradas (carpetas)
    patron  = '<div class="video-item">.*?<div class="item-thumbnail">.*?<a href="(.*?)" title="(.*?)"><img src="(.*?)" '
    matches = re.compile( patron, re.DOTALL ).findall( data )
   
    for scrapedurl,scrapedtitle,scrapedthumbnail in matches:
        title = scrapertools.decodeHtmlentities( scrapedtitle )
      
        itemlist.append( Item( channel=__channel__, action="findvideos", title=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail, viewmode="movie_with_plot") )

    return itemlist

def categorias(item):
    logger.info("pelisalacarta.animesubita categorias")

    itemlist = []

    data = scrapertools.cache_page( item.url )

    # The categories are the options for the combo
    patron = '<li><a title="(.*?)" href="(.*?)">.*?</a> <span class="mctagmap_count">.*?</span></li>'

    matches = re.compile(patron,re.DOTALL).findall(data)

    for scrapedtitle, scrapedurl in matches:

        itemlist.append( Item( channel=__channel__, action="selection" , title=scrapedtitle, url=scrapedurl ) )

    return itemlist
   
def selection( item ):
    logger.info( "pelisalacarta.animesubita peliculas" )

    itemlist = []

    ## Descarga la pagina
    data = scrapertools.cache_page( item.url )

    ## Extrae las entradas (carpetas)
    patron  = '<div class="item-head">.*?<h3><a href="(.*?)".*?rel=.*?title="(.*?)">.*?</h3>'
    matches = re.compile( patron, re.DOTALL ).findall( data )
   
    for scrapedurl,scrapedtitle in matches:
        itemlist.append( Item( channel=__channel__, action="episodios", title=scrapedtitle, url=scrapedurl) )

    return itemlist   

def episodios( item ):
    logger.info( "pelisalacarta.animesubita peliculas" )

    itemlist = []

    ## Descarga la pagina
    data = scrapertools.cache_page( item.url )

    ## Extrae las entradas (carpetas)
    patron  = '<div class="col-md-3 col-sm-6 col-xs-6 ">.*?<div class="item-head">.*?<h3><a href="(.*?)".*?title="(.*?)">.*?</a>'
    matches = re.compile( patron, re.DOTALL ).findall( data )
   
    for scrapedurl,scrapedtitle in matches:
      
        itemlist.append( Item( channel=__channel__, action="findvideos", title=scrapedtitle, url=scrapedurl) )

    return itemlist

def search( item, texto ):
    logger.info( "[animesubita.py] " + item.url + " search " + texto )

    item.url = sito + "?s=" + texto

    try:
        return selection( item )

    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []


def findvideos(item):
    logger.info("pelisalacarta.channels.animesubita findvideos")

    headers.append(['Referer', item.url])

    ## Descarga la pagina
    data = scrapertools.cache_page(item.url)

    patron = 'return\s*gnarty_player\((\d+)\);'
    matches = re.compile(patron, re.DOTALL).findall(data)
    url = sito + 'wp-admin/admin-ajax.php'
    li = []
    for vid in matches:
        li.append(scrapertools.cache_page(url, post='action=loadPlayer&id=' + vid, headers=headers))

    data = ''.join(li)

    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        videoitem.title = item.title + videoitem.title
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = __channel__

    return itemlist
