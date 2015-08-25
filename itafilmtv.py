# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canale per itafilmtv
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# Info tradotte per aiutare chi volesse cimentarsi 
#------------------------------------------------------------

# Si definiscono le librerie che si useranno per far funzionare il canale
import urlparse,urllib2,urllib,re
import os, sys

from core import scrapertools
from core import logger
from core import config
from core.item import Item
from servers import servertools

# Informazioni sul canale
__channel__ = "itafilmtv"
__category__ = "F,S"
__type__ = "generic"
__title__ = "ITA Film TV"
__language__ = "IT"

# Si definisce la pagina principale del sito su cui si lavora
host = "http://www.itafilm.tv"
# Si definiscono gli headers, richiesti da alcuni siti per accedervi
headers = [
    ['Host','www.itafilm.tv'],
    ['User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0'],
    ['Accept-Encoding','gzip, deflate'],
    ['Cookie','_ddn_intercept_2_=b33473ad0b70b320a9f7546e213a396a']
]

def isGeneric():
    return True
# Struttura del menù principale del canale
def mainlist( item ):
    logger.info( "[itafilmtv.py] mainlist" )

    itemlist = []

    itemlist.append( Item( channel=__channel__, action="film", title="[COLOR azure]Home[/COLOR]", url=host ) )
    itemlist.append( Item( channel=__channel__, action="genere", title="[COLOR azure]Film Per Genere[/COLOR]", url=host ) )
    itemlist.append( Item( channel=__channel__, action="serietv", title="[COLOR azure]Serie TV[/COLOR]", url="http://www.itafilm.tv/telefilm-serie-tv-streaming/" ) )
    itemlist.append( Item( channel=__channel__, action="search", title="[COLOR orange]Cerca...[/COLOR]", url=host ) )

    return itemlist

# Chiamando una funzione "search", il launcher chiede un testo da inserire e lo agiunge come parametro
def search( item, texto ):
    logger.info( "[itafilmtv.py] " + item.url + " search " + texto )

    item.url = "http://www.itafilm.tv/index.php?story="+texto+"&do=search&subaction=search"

    try:
        return film( item )

    # Si aggiunge una eccezione, per non interrompere la ricerca globale se un canale fallisce per qualche motivo
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []

def film( item ):
    logger.info( "[itafilmtv.py] mainlist" )

    itemlist = []

    # Scarica l'HTML della pagina
    data = scrapertools.cache_page( item.url, headers=headers )

    # Ne estrae i dati
    patron = '<div class="main-news">.*?'
    patron += '<div class="main-news-image"[^<]+'
    patron += '<a href="([^"]+)">'
    patron += '<img src="([^"]+)" '
    patron += 'alt="([^"]+)"'

    matches = re.compile( patron, re.DOTALL ).findall( data )
    # Si definiscono i "matches" individuati nei patron, rispettivamente:
    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:

        scrapedtitle = scrapertools.decodeHtmlentities( scrapedtitle )

        itemlist.append( Item( channel=__channel__, action="trova_video" , title=scrapedtitle, url=scrapedurl, thumbnail=urlparse.urljoin( host, scrapedthumbnail ), fulltitle=scrapedtitle, show=scrapedtitle ) )

    # Si individua l'url per indirizzare alla pagina successiva
    next_page = scrapertools.find_single_match( data, '<span>\d+</span> <a href="([^"]+)">' )
    if next_page != "":
        itemlist.append( Item( channel=__channel__, action="film" , title="[COLOR orange]Successivo >>>[/COLOR]" , url=next_page ) )

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
        itemlist.append( Item(channel=__channel__, action="film", title="[COLOR azure]"+scrapedtitle+"[/COLOR]", url=host+scrapedurl, folder=True))

    return itemlist

def serietv( item ):
    logger.info( "[itafilmtv.py] mainlist" )

    itemlist = []

    # Scarica l'HTML della pagina
    data = scrapertools.cache_page( item.url, headers=headers )

    # Ne estrae i dati
    patron = '<div class="main-news">.*?'
    patron += '<div class="main-news-image"[^<]+'
    patron += '<a href="([^"]+)">'
    patron += '<img src="([^"]+)" '
    patron += 'alt="([^"]+)"'

    matches = re.compile( patron, re.DOTALL ).findall( data )
    # Si definiscono i "matches" individuati nei patron, rispettivamente:
    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:

        scrapedtitle = scrapertools.decodeHtmlentities( scrapedtitle )

        itemlist.append( Item( channel=__channel__, action="trova_ep_serie" , title=scrapedtitle, url=scrapedurl, thumbnail=urlparse.urljoin( host, scrapedthumbnail ), fulltitle=scrapedtitle, show=scrapedtitle ) )

    # Si individua l'url per indirizzare il canale alla pagina successiva del sito
    next_page = scrapertools.find_single_match( data, '<span>\d+</span> <a href="([^"]+)">' )
    if next_page != "":
        itemlist.append( Item( channel=__channel__, action="film" , title="[COLOR orange]Successivo >>>[/COLOR]" , url=next_page ) )

    return itemlist

def trova_video( item ):
    logger.info( "[itafilmtv.py] findvideos" )

    itemlist = []

    data = scrapertools.cache_page( item.url, headers=headers )

    sources = scrapertools.get_match( data, '(<noindex> <div class="video-player-plugin">.*?</noindex>)')

    patron = 'src="([^"]+)"'

    matches = re.compile( patron, re.DOTALL ).findall( sources )

    for scrapedurl in matches:

        server = scrapedurl.split( '/' )[2].split( '.' )
        if len(server) == 3: server = server[1]
        else: server = server[0]

        title = "[" + server + "] " + item.fulltitle

        itemlist.append( Item( channel=__channel__, action="play" , title=title, url=scrapedurl, thumbnail=item.thumbnail, fulltitle=item.fulltitle, show=item.show, folder=False ) )

    return itemlist

def trova_ep_serie(item):
    logger.info("[itafilmtv.py] trova_ep_serie")

    itemlist = []

    ## Descarga la página
    data = scrapertools.cache_page(item.url)
    data = scrapertools.decodeHtmlentities(data)

    patron1 = '<!--colorstart:#009900--><span style="color:#009900">(.+?)<div style="clear: both;height: 1px;"></div>'
    matches1 = re.compile(patron1, re.DOTALL).findall(data)
    for match1 in matches1:
        for data in match1.split('<br/>'):
            ## Extrae las entradas
            scrapedtitle = data.split('<a ')[0]
            scrapedtitle = re.sub(r'<[^>]*>', '', scrapedtitle)
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

def play( item ):
    logger.info( "[itafilmtv.py] play" )

    ## Serve soltanto l'url
    data = item.url

    itemlist = servertools.find_video_items( data=data )

    for videoitem in itemlist:
        videoitem.title = item.show
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = __channel__

    return itemlist
