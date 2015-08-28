# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para seriehd - based on guardaserie channel
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "seriehd"
__category__ = "S"
__type__ = "generic"
__title__ = "Serie HD"
__language__ = "IT"

headers = [
    ['Host','www.seriehd.org'],
    ['User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0'],
    ['Accept-Encoding','gzip, deflate']
]

host = "http://www.seriehd.org"

def isGeneric():
    return True

def mainlist( item ):
    logger.info( "pelisalacarta.channels.seriehd mainlist" )

    itemlist = []

    itemlist.append( Item( channel=__channel__, action="fichas", title="Serie TV", url=host ) )
    itemlist.append( Item( channel=__channel__, action="search", title="Cerca..." ) )


    return itemlist

def search( item,texto ):
    logger.info("pelisalacarta.channels.seriehd search")

    item.url=host + "/?s=" + texto

    try:
        ## Se tiene que incluir aquí el nuevo scraper o crear una nueva función para ello
        return fichas( item )

    ## Se captura la excepción, para no interrumpir al buscador global si un canal falla.
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []

def fichas( item ):
    logger.info( "pelisalacarta.channels.seriehd fichas" )
    itemlist = []

    if item.url == "":
        item.url = host

    data = scrapertools.cache_page( item.url )
    logger.info(data)

    patron  = '<h2>(.*?)</h2>\s*'
    patron += '<img src="(.*?)" alt=".*?"/>\s*'
    patron += '<A HREF="(.*?)"><span class="player"></span></A>'
    matches = re.compile( patron, re.DOTALL ).findall( data )

    for scrapedtitle, scrapedthumbnail, scrapedurl in matches:

        itemlist.append( Item( channel=__channel__, action="episodios", title="[COLOR azure]" + scrapedtitle + "[/COLOR]", fulltitle=scrapedtitle, url=scrapedurl, show=scrapedtitle, thumbnail=scrapedthumbnail ) )

    return itemlist

def cerca( item ):
    logger.info( "pelisalacarta.channels.seriehd fichas" )
    itemlist = []

    if item.url == "":
        item.url = host

    data = scrapertools.cache_page( item.url )
    logger.info(data)

    patron  = '<h2>(.*?)</h2>\s*'
    patron += '<img src="(.*?)" alt=".*?" pagespeed_url_hash=".*?"/>\s*'
    patron += '<A HREF="(.*?)"><span class="player"><span class="cp-title">.*?</span></span></A>'
    matches = re.compile( patron, re.DOTALL ).findall( data )

    for scrapedtitle, scrapedthumbnail, scrapedurl in matches:

        itemlist.append( Item( channel=__channel__, action="episodios", title="[COLOR azure]" + scrapedtitle + "[/COLOR]", fulltitle=scrapedtitle, url=scrapedurl, show=scrapedtitle, thumbnail=scrapedthumbnail ) )

    return itemlist

def episodios(item):
    logger.info("pelisalacarta.channels.seriehd episodios")

    itemlist = []

    data = scrapertools.cache_page( item.url )

    serie_id = scrapertools.get_match( data, '?idFilm=(\d+)" allowfullscreen>' )

    data = scrapertools.get_match( data, '<select name="puntata" class="selEp">(.*?)</select>' )

    seasons_episodes = re.compile( '<option data-id="(\d+)" value=".*?">(.*?)</option>', re.DOTALL ).findall( data )

    for scrapedseason, scrapedepisodes in seasons_episodes:

        episodes = re.compile( 'data-id="(\d+)"', re.DOTALL ).findall( scrapedepisodes )
        for scrapedepisode in episodes:

            season = str ( int( scrapedseason ) + 1 )
            episode = str ( int( scrapedepisode ) + 1 )
            if len( episode ) == 1: episode = "0" + episode

            title = season + "x" + episode + " - " + item.title

            ## Le pasamos a 'findvideos' la url con tres partes divididas por el caracter "?"
            ## [host+path]?[argumentos]?[Referer]
            url = host + "/wp-admin/admin-ajax.php?action=get_episode&id=" + serie_id + "&season=" + scrapedseason + "&episode=" + scrapedepisode + "?" + item.url

            itemlist.append( Item( channel=__channel__, action="findvideos", title=title, url=url, fulltitle=item.title, show=item.title ) )

    return itemlist

def findvideos( item ):
    logger.info("pelisalacarta.channels.seriehd findvideos")

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

    itemlist.append( Item( channel=__channel__, action="play",title=title, url=url, server=server , fulltitle=item.fulltitle, show=item.show, folder=False ) )

    return itemlist
