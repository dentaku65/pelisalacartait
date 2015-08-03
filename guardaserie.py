# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para guardaserie - Thank you robalo!
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "guardaserie"
__category__ = "S"
__type__ = "generic"
__title__ = "Guarda Serie"
__language__ = "IT"

headers = [
    ['Host','www.guardaserie.net'],
    ['User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0'],
    ['Accept-Encoding','gzip, deflate']
]

host = "http://www.guardaserie.net"

def isGeneric():
    return True

def mainlist( item ):
    logger.info( "pelisalacarta.channels.guardaserie mainlist" )

    itemlist = []

    itemlist.append( Item( channel=__channel__, action="fichas", title="[COLOR azure]Serie TV[/COLOR]", url=host + "/lista-serie-tv-guardaserie/" , thumbnail="http://i58.tinypic.com/2zs64cz.jpg" ) )
    itemlist.append( Item( channel=__channel__, action="anime", title="[COLOR azure]Anime[/COLOR]", url=host + "/lista-serie-tv-guardaserie/" , thumbnail="http://2.bp.blogspot.com/-4AeDx37c3uQ/VAxIHDhm-9I/AAAAAAAABRA/BUnctEGpVYM/s1600/528900971.gif" ) )
    itemlist.append( Item( channel=__channel__, action="cartoni", title="[COLOR azure]Cartoni Animati[/COLOR]", url=host + "/lista-serie-tv-guardaserie/" , thumbnail="http://www.badtv.it/wp-content/uploads/2011/04/family-guy-american-dad-cleveland-show-cross-over.jpg" ) )
    itemlist.append( Item( channel=__channel__, action="progs", title="[COLOR azure]Programmi TV[/COLOR]", url=host + "/lista-serie-tv-guardaserie/" , thumbnail="http://mujakovic.weebly.com/uploads/1/4/7/9/14799472/3787546.png" ) )
    itemlist.append( Item( channel=__channel__, action="search", title="[COLOR yellow]Cerca...[/COLOR]" , thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search" ) )

    return itemlist

def search( item,texto ):
    logger.info("pelisalacarta.channels.guardaserie search")

    item.url=host + "/?s=" + texto

    try:
        ## Se tiene que incluir aquí el nuevo scraper o crear una nueva función para ello
        return cerca( item )

    ## Se captura la excepción, para no interrumpir al buscador global si un canal falla.
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []

def fichas( item ):
    logger.info( "pelisalacarta.channels.guardaserie fichas" )

    itemlist = []

    data = scrapertools.cache_page( item.url )

    data = scrapertools.find_single_match( data, '<a[^>]+>Serie Tv</a><ul>(.*?)</ul>' )

    patron  = '<li><a href="([^"]+)[^>]+>([^<]+)</a></li>'

    matches = re.compile( patron, re.DOTALL ).findall( data )

    for scrapedurl, scrapedtitle in matches:

        itemlist.append( Item( channel=__channel__, action="episodios", title="[COLOR azure][" + scrapedtitle + "][/COLOR]", fulltitle=scrapedtitle, url=scrapedurl, show=scrapedtitle ) )

    return itemlist

def anime( item ):
    logger.info( "pelisalacarta.channels.guardaserie fichas" )

    itemlist = []

    data = scrapertools.cache_page( item.url )

    data = scrapertools.find_single_match( data, '<a[^>]+>Anime</a><ul>(.*?)</ul>' )

    patron  = '<li><a href="([^"]+)[^>]+>([^<]+)</a></li>'

    matches = re.compile( patron, re.DOTALL ).findall( data )

    for scrapedurl, scrapedtitle in matches:

        itemlist.append( Item( channel=__channel__, action="episodios", title="[COLOR azure][" + scrapedtitle + "][/COLOR]", fulltitle=scrapedtitle, url=scrapedurl, show=scrapedtitle, thumbnail="http://www.itrentenni.com/wp-content/uploads/2015/02/tv-series.jpg" ) )

    return itemlist

def cartoni( item ):
    logger.info( "pelisalacarta.channels.guardaserie fichas" )

    itemlist = []

    data = scrapertools.cache_page( item.url )

    data = scrapertools.find_single_match( data, '<a[^>]+>Cartoni</a><ul>(.*?)</ul>' )

    patron  = '<li><a href="([^"]+)[^>]+>([^<]+)</a></li>'

    matches = re.compile( patron, re.DOTALL ).findall( data )

    for scrapedurl, scrapedtitle in matches:

        itemlist.append( Item( channel=__channel__, action="episodios", title="[COLOR azure][" + scrapedtitle + "][/COLOR]", fulltitle=scrapedtitle, url=scrapedurl, show=scrapedtitle, thumbnail="http://www.itrentenni.com/wp-content/uploads/2015/02/tv-series.jpg" ) )

    return itemlist

def progs( item ):
    logger.info( "pelisalacarta.channels.guardaserie fichas" )

    itemlist = []

    data = scrapertools.cache_page( item.url )

    data = scrapertools.find_single_match( data, '<a[^>]+>Programmi TV</a><ul>(.*?)</ul>' )

    patron  = '<li><a href="([^"]+)[^>]+>([^<]+)</a></li>'

    matches = re.compile( patron, re.DOTALL ).findall( data )

    for scrapedurl, scrapedtitle in matches:

        itemlist.append( Item( channel=__channel__, action="episodios",title="[COLOR azure][" + scrapedtitle + "][/COLOR]", fulltitle=scrapedtitle, url=scrapedurl, show=scrapedtitle, thumbnail="http://www.itrentenni.com/wp-content/uploads/2015/02/tv-series.jpg" ) )

    return itemlist

def cerca( item ):
    logger.info( "pelisalacarta.channels.guardaserie fichas" )

    itemlist = []

    data = scrapertools.cache_page( item.url )

    data = scrapertools.find_single_match( data, '<div class="search_post">(.*?)</div>' )

    patron  = '<a.*?href="(.*?)".*?title="(.*?)".*?<img src="(.*?)" />'

    matches = re.compile( patron, re.DOTALL ).findall( data )

    for scrapedurl, scrapedtitle, scrapedthumbnail in matches:

        if scrapedtitle.startswith("Guarda "):

           scrapedtitle = scrapedtitle[7:]
           
        itemlist.append( Item( channel=__channel__, action="episodios",title="[COLOR azure][" + scrapedtitle + "][/COLOR]", fulltitle=scrapedtitle, url=scrapedurl, show=scrapedtitle , thumbnail=scrapedthumbnail ) )

    return itemlist

def episodios(item):
    logger.info("pelisalacarta.channels.guardaserie episodios")

    itemlist = []

    data = scrapertools.cache_page( item.url )

    serie_id = scrapertools.get_match( data, '/?id=(\d+)" rel="nofollow"' )

    data = scrapertools.get_match( data, '<div id="episode">(.*?)</div>' )

    seasons_episodes = re.compile( '<select name="episode" id="(\d+)">(.*?)</select>', re.DOTALL ).findall( data )

    for scrapedseason, scrapedepisodes in seasons_episodes:

        episodes = re.compile( '<option value="(\d+)"', re.DOTALL ).findall( scrapedepisodes )
        for scrapedepisode in episodes:

            season = str ( int( scrapedseason ) + 1 )
            episode = str ( int( scrapedepisode ) + 1 )
            if len( episode ) == 1: episode = "0" + episode

            title = season + "x" + episode + " - " + item.title

            ## Le pasamos a 'findvideos' la url con tres partes divididas por el caracter "?"
            ## [host+path]?[argumentos]?[Referer]
            url = host + "/wp-admin/admin-ajax.php?action=get_episode&id=" + serie_id + "&season=" + scrapedseason + "&episode=" + scrapedepisode + "?" + item.url 

            itemlist.append( Item( channel=__channel__, action="findvideos", title="[COLOR azure][" + title + "][/COLOR]", url=url, fulltitle=item.title, show=item.title ) )

    return itemlist

def findvideos( item ):
    logger.info("pelisalacarta.channels.guardaserie findvideos")

    itemlist = []

    url = item.url.split( '?' )[0]
    post = item.url.split( '?' )[1]
    referer = item.url.split( '?' )[2]

    headers.append( [ 'Referer', referer ] )

    data = scrapertools.cache_page( url, post=post, headers=headers )

    url = scrapertools.get_match( data.lower(), 'src="([^"]+)"' )
    url = re.sub( r'embed\-|\-607x360\.html', '', url)

    server = url.split( '/' )[2].split( '.' )
    server = server[1] if len( server ) == 3 else server[0]

    title = "[" + server + "] " + item.title

    itemlist.append( Item( channel=__channel__, action="play",title="[COLOR azure][" + title + "][/COLOR]", url=url, server=server , fulltitle=item.fulltitle, show=item.show, folder=False ) )

    return itemlist
