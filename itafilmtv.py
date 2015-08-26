# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para itafilmtv
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os, sys

from core import scrapertools
from core import logger
from core import config
from core.item import Item
from servers import servertools

__channel__ = "itafilmtv"
__category__ = "F,S"
__type__ = "generic"
__title__ = "ITA Film TV"
__language__ = "IT"

host = "http://www.itafilm.tv"

headers = [
    ['Host','www.itafilm.tv'],
    ['User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0'],
    ['Accept-Encoding','gzip, deflate'],
    ['Cookie','_ddn_intercept_2_=b33473ad0b70b320a9f7546e213a396a']
]

def isGeneric():
    return True

def mainlist( item ):
    logger.info( "[itafilmtv.py] mainlist" )

    itemlist = []

    itemlist.append( Item( channel=__channel__, action="fichas", title="[COLOR azure]Home[/COLOR]", url=host, thumbnail="http://dc584.4shared.com/img/XImgcB94/s7/13feaf0b538/saquinho_de_pipoca_01" ) )
    itemlist.append( Item( channel=__channel__, action="genere", title="[COLOR azure]Film Per Genere[/COLOR]", url=host, thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/All%20Movies%20by%20Genre.png" ) )
    itemlist.append( Item( channel=__channel__, action="serietv", title="[COLOR azure]Serie TV[/COLOR]", url=host + "/telefilm-serie-tv-streaming/", thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/New%20TV%20Shows.png") )
    itemlist.append( Item(channel=__channel__, action="search", title="[COLOR yellow]Cerca...[/COLOR]", url=host, thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search"))

    return itemlist

## Al llamarse "search" la función, el launcher pide un texto a buscar y lo añade como parámetro
def search( item, texto ):
    logger.info( "[itafilmtv.py] " + item.url + " search " + texto )

    item.url+= "/?do=search&subaction=search&story=" + texto

    try:
        return fichas( item )

    ## Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []

def fichas( item ):
    logger.info( "[itafilmtv.py] fichas" )

    itemlist = []

    ## Descarga la página
    data = scrapertools.cache_page( item.url, headers=headers )

    action = "findvideos"

    ## Extrae las datos
    patron = '<div class="main-news">.*?'
    patron+= '<div class="main-news-image"[^<]+'
    patron += '<a href="([^"]+)">'
    patron += '<img src="([^"]+)" '
    patron += 'alt="([^"]+)"'

    matches = re.compile( patron, re.DOTALL ).findall( data )

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:

        scrapedtitle = scrapertools.decodeHtmlentities( scrapedtitle )

        itemlist.append( Item( channel=__channel__, action=action, title=scrapedtitle, url=scrapedurl, thumbnail=urlparse.urljoin( host, scrapedthumbnail ), fulltitle=scrapedtitle, show=scrapedtitle ) )

    ## Paginación
    next_page = scrapertools.find_single_match( data, '<span>\d+</span> <a href="([^"]+)">' )
    if next_page != "":
        itemlist.append( Item( channel=__channel__, action="fichas" , title="[COLOR orange]Successivo >>[/COLOR]" , url=next_page ) )

    return itemlist

def serietv( item ):
    logger.info( "[itafilmtv.py] fichas" )

    itemlist = []

    ## Descarga la página
    data = scrapertools.cache_page( item.url, headers=headers )

    action = "episodios"

    ## Extrae las datos
    patron = '<div class="main-news">.*?'
    patron+= '<div class="main-news-image"[^<]+'
    patron += '<a href="([^"]+)">'
    patron += '<img src="([^"]+)" '
    patron += 'alt="([^"]+)"'

    matches = re.compile( patron, re.DOTALL ).findall( data )

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:

        scrapedtitle = scrapertools.decodeHtmlentities( scrapedtitle )

        itemlist.append( Item( channel=__channel__, action=action, title=scrapedtitle, url=scrapedurl, thumbnail=urlparse.urljoin( host, scrapedthumbnail ), fulltitle=scrapedtitle, show=scrapedtitle ) )

    ## Paginación
    next_page = scrapertools.find_single_match( data, '<span>\d+</span> <a href="([^"]+)">' )
    if next_page != "":
        itemlist.append( Item( channel=__channel__, action="fichas" , title="[COLOR orange]Successivo >>[/COLOR]" , url=next_page ) )

    return itemlist

def genere(item):
    logger.info("[itafilmtv.py] genere")
    itemlist = []

    data = scrapertools.cachePage(item.url, headers=headers )
    logger.info("data="+data)

    data = scrapertools.find_single_match(data,'<div class="menu2">(.*?)<div class="left-wrap">')
    logger.info("data="+data)

    patron  = '<a href="(.*?)">(.*?)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle in matches:
        itemlist.append( Item(channel=__channel__, action="fichas", title="[COLOR azure]"+scrapedtitle+"[/COLOR]", url=host+scrapedurl, folder=True))

    return itemlist


def episodios( item ):
    logger.info( "[itafilmtv.py] episodios" )

    itemlist = []

    ## Descarga la página
    data = scrapertools.cache_page( item.url, headers=headers )

    plot = scrapertools.htmlclean(
        scrapertools.get_match( data, '<div class="main-news-text main-news-text2">(.*?)</div>' )
    ).strip()

    ## Extrae las datos - Episodios
    patron = '<br />(\d+x\d+).*?href="//ads.ad-center.com/[^<]+</a>(.*?)<a href="//ads.ad-center.com/[^<]+</a>'
    matches = re.compile( patron, re.DOTALL ).findall( data )

    ## Extrae las datos - sub ITA/ITA
    patron = '<b>.*?STAGIONE.*?(sub|ITA).*?</b>'
    lang = re.compile( patron, re.IGNORECASE ).findall( data )

    lang_index = 0
    for scrapedepisode, scrapedurls in matches:

        if int( scrapertools.get_match( scrapedepisode, '\d+x(\d+)' ) ) == 1:
            lang_title = lang[lang_index]
            if lang_title.lower() == "sub": lang_title+= " ITA"
            lang_index+= 1

        title = scrapedepisode + " - " + item.show + " (" + lang_title + ")"
        scrapedurls = scrapedurls.replace( "playreplay", "moevideo" )

        matches_urls = re.compile( 'href="([^"]+)"', re.DOTALL ).findall( scrapedurls )
        urls = ""
        for url in matches_urls:
            urls+= url + "|"

        if urls != "":
            itemlist.append( Item( channel=__channel__, action="findvideos", title=title, url=urls[:-1], thumbnail=item.thumbnail, plot=plot, fulltitle=item.fulltitle, show=item.show ) )

    return itemlist

def findvideos( item ):
    logger.info( "[itafilmtv.py] findvideos" )

    itemlist = []

    ## Extrae las datos
    if "|" not in item.url:
        ## Descarga la página
        data = scrapertools.cache_page( item.url, headers=headers )

        sources = scrapertools.get_match( data, '(<noindex> <div class="video-player-plugin">.*?</noindex>)')

        patron = 'src="([^"]+)"'
        matches = re.compile( patron, re.DOTALL ).findall( sources )
    else:
        matches = item.url.split( '|' )

    for scrapedurl in matches:

        server = scrapedurl.split( '/' )[2].split( '.' )
        if len(server) == 3: server = server[1]
        else: server = server[0]

        title = "[" + server + "] " + item.fulltitle

        itemlist.append( Item( channel=__channel__, action="play" , title=title, url=scrapedurl, thumbnail=item.thumbnail, fulltitle=item.fulltitle, show=item.show, folder=False ) )

    return itemlist

def play( item ):
    logger.info( "[itafilmtv.py] play" )

    ## Sólo es necesario la url
    data = item.url

    itemlist = servertools.find_video_items( data=data )

    for videoitem in itemlist:
        videoitem.title = item.show
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = __channel__

    return itemlist
