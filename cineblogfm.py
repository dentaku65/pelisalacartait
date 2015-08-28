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

__channel__ = "cineblogfm"
__category__ = "F,S"
__type__ = "generic"
__title__ = "CineBlog01.FM"
__language__ = "IT"

sito="http://www.cineblog01.fm"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("pelisalacarta.cineblogfm mainlist")
    itemlist = []
    itemlist.append( Item(channel=__channel__, title="[COLOR azure]Nuovi Film[/COLOR]", action="peliculas", url=sito+"/new-film-streaming/", thumbnail="http://dc584.4shared.com/img/XImgcB94/s7/13feaf0b538/saquinho_de_pipoca_01"))
    itemlist.append( Item(channel=__channel__, title="[COLOR azure]Film Per Genere[/COLOR]", action="categorias", url=sito, thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/All%20Movies%20by%20Genre.png"))
    itemlist.append( Item(channel=__channel__, title="[COLOR azure]Film Per Paese[/COLOR]", action="catpays", url=sito , thumbnail="http://missindependent-movie.com/wp-content/uploads/2011/07/movie-clapper-board-hi.png"))
    itemlist.append( Item(channel=__channel__, title="[COLOR azure]Film Per Anno[/COLOR]", action="catyear", url=sito, thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/Movie%20Year.png"))
    itemlist.append( Item(channel=__channel__, title="[COLOR azure]Serie TV[/COLOR]", extra="serie", action="peliculas", url=sito+"/telefilm-serie-tv-streaming/", thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/New%20TV%20Shows.png"))
    itemlist.append( Item(channel=__channel__, title="[COLOR yellow]Cerca...[/COLOR]", action="search"))

    
    return itemlist

def categorias(item):
    logger.info("pelisalacarta.cineblogfm categorias")
    itemlist = []
    
    data = scrapertools.cache_page(item.url)
    logger.info(data)

    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data,'<li class="drop"><a href="/" class="link1"><b>Film Streaming </b></a>.*?<ul>(.*?)<li class="drop">')
    
    # The categories are the options for the combo
    patron = '<li><a href="(.*?)">(.*?)</a></li>'
    matches = re.compile(patron,re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for url,titulo in matches:
        scrapedtitle = titulo
        scrapedurl = urlparse.urljoin(item.url,url)
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="peliculas" , title="[COLOR azure]"+scrapedtitle+"[/COLOR]" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot))

    return itemlist

def catpays(item):
    logger.info("pelisalacarta.cineblogfm categorias")
    itemlist = []
    
    data = scrapertools.cache_page(item.url)
    logger.info(data)

    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data,'<li class="drop"><a href="/" class="link1"><b>Film per paese</b></a>(.*?)<li class="drop">')
    
    # The categories are the options for the combo
    patron = '<li><a.*?href="(.*?)">(.*?)</a></li>'
    matches = re.compile(patron,re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for url,titulo in matches:
        scrapedtitle = titulo
        scrapedurl = urlparse.urljoin(item.url,url)
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="peliculas" ,title="[COLOR azure]"+scrapedtitle+"[/COLOR]" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot, folder=True ))

    return itemlist

def catyear(item):
    logger.info("pelisalacarta.cineblogfm categorias")
    itemlist = []
    
    data = scrapertools.cache_page(item.url)
    logger.info(data)

    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data,'<li class="drop"><a href="/" class="link1"><b>Film per anno</b></a>(.*?)<li class="drop">')
    
    # The categories are the options for the combo
    patron = '<li><a.*?href="(.*?)">(.*?)</a></li>'
    matches = re.compile(patron,re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for url,titulo in matches:
        scrapedtitle = titulo
        scrapedurl = urlparse.urljoin(item.url,url)
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="peliculas" , title="[COLOR azure]"+scrapedtitle+"[/COLOR]", url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot, folder=True ))

    return itemlist

def search(item,texto):
    logger.info("[itafilmtv.py] "+item.url+" search "+texto)
    item.url = "http://www.cineblog01.fm/xfsearch/" + texto
    try:
        return peliculas(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []

def peliculas(item):
    logger.info("pelisalacarta.cineblogfm peliculas")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)

    # Extrae las entradas (carpetas)
    patron = '<div class="short-story">\s*'
    patron += '<a href="(.*?)" title="(.*?)">\s*'
    patron += '<img.*?:url\((.*?)\)'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle,scrapedthumbnail in matches:
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="episodios" if item.extra == "serie" else "findvideos", title=scrapedtitle, url=scrapedurl , thumbnail=scrapedthumbnail , viewmode="movie_with_plot", fanart=scrapedthumbnail , folder=True ) )


    # Extrae el paginador
    patronvideos  = '<span class="nav_ext">...</span> <a href=".*?">.*?</a> <a href="(.*?)">Avanti</a></div></div>'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    if len(matches)>0:
        scrapedurl = urlparse.urljoin(item.url,matches[0])
        itemlist.append( Item(channel=__channel__, extra=item.extra, action="peliculas", title="[COLOR orange]Avanti >>[/COLOR]" , url=scrapedurl , thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png", folder=True) )

    return itemlist

def episodios( item ):
    logger.info( "[itafilmtv.py] episodios" )

    itemlist = []

    ## Descarga la página
    data = scrapertools.cache_page( item.url )

    plot = scrapertools.htmlclean(
        scrapertools.get_match( data, '</span></h1></div>(.*?)<td class="full-right">' )
    ).strip()

    ## Extrae las datos - Episodios
    patron = '<br />(\d+x\d+).*?href="//ads.ad-center.com/[^<]+</a>(.*?)<a href="//ads.ad-center.com/[^<]+</a>'
    matches = re.compile( patron, re.DOTALL ).findall( data )
    if len( matches ) == 0:
        patron = ' />(\d+x\d+)(.*?)<br'
        matches = re.compile( patron, re.DOTALL ).findall( data )

    print "##### episodios matches ## %s ##" % matches

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
            itemlist.append( Item( channel=__channel__, action="findvid_series", title=title, url=urls[:-1], thumbnail=item.thumbnail, plot=plot, fulltitle=item.fulltitle, show=item.show ) )

    return itemlist

def findvid_series( item ):
    logger.info( "[cineblogfm.py] findvideos" )

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
    logger.info( "[cineblogfm.py] play" )

    ## Sólo es necesario la url
    data = item.url

    itemlist = servertools.find_video_items( data=data )

    for videoitem in itemlist:
        videoitem.title = item.show
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = __channel__

    return itemlist
