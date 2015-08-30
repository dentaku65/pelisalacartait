# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para altadefinizioneclick
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# ------------------------------------------------------------
import urllib2, re, urlparse
import time

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "altadefinizioneclick"
__category__ = "F,S,A"
__type__ = "generic"
__title__ = "AltaDefinizioneclick"
__language__ = "IT"

host = "http://www.altadefinizione.click"

headers = [
    ['User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:38.0) Gecko/20100101 Firefox/38.0'],
    ['Accept-Encoding', 'gzip, deflate'],
    ['Referer', 'http://altadefinizione.click/'],
    ['Connection', 'keep-alive']
]

def isGeneric():
    return True


def mainlist( item ):
    logger.info( "[altadefinizioneclick.py] mainlist" )

    itemlist = []

    itemlist.append( Item( channel=__channel__, title="Al Cinema", action="fichas", url=host + "/al-cinema/" ) )
    itemlist.append( Item( channel=__channel__, title="Nuove Uscite", action="fichas", url=host + "/nuove-uscite/" ) )
    itemlist.append( Item( channel=__channel__, title="Sub-ITA", action="fichas", url=host + "/sub-ita/" ) )
    itemlist.append( Item( channel=__channel__, title="Genere", action="categorias", url=host ) )	
    itemlist.append( Item( channel=__channel__, title="Anno", action="categorias1", url=host ) )
    itemlist.append( Item( channel=__channel__, title="Qualità", action="categorias2", url=host ) )
    itemlist.append( Item( channel=__channel__, title="Ricerca...", action="search", url=host ) )
	
    return itemlist

def search( item, texto ):
    logger.info( "[altadefinizioneclick.py] " + item.url + " search " + texto )

    item.url+= "/?s=" + texto

    try:
        return fichas( item )

    ## Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

def fichas( item ):
    logger.info( "[altadefinizioneclick.py] fichas" )

    itemlist = []

    # Descarga la pagina
    data = anti_cloudflare( item.url )

    ## ------------------------------------------------
    cookies = ""
    matches = re.compile( '(.altadefinizione.click.*?)\n', re.DOTALL ).findall( config.get_cookie_data() )
    for cookie in matches:
        name = cookie.split( '\t' )[5]
        value = cookie.split( '\t' )[6]
        cookies+= name + "=" + value + ";"
    headers.append( ['Cookie',cookies[:-1]] )
    import urllib
    _headers = urllib.urlencode( dict( headers ) )
    ## ------------------------------------------------

    if "/?s=" in item.url:
        patron = '<div class="col-lg-3 col-md-3 col-xs-3">.*?'
        patron+= 'href="([^"]+)".*?'
        patron+= '<div class="wrapperImage"[^<]+'
        patron+= '<[^>]+>([^<]+)<.*?'
        patron+= 'src="([^"]+)".*?'
        patron+= 'class="titleFilm">([^<]+)<.*?'
        patron+= 'IMDB: ([^<]+)<'
    else:
        patron = '<div class="wrapperImage"[^<]+'
        patron+= '<[^>]+>([^<]+)<.*?'
        patron+= 'href="([^"]+)".*?'
        patron+= 'src="([^"]+)".*?'
        patron+= 'href[^>]+>([^<]+)</a>.*?'
        patron+= 'IMDB: ([^<]+)<'

    matches = re.compile( patron, re.DOTALL ).findall( data )

    for scraped_1, scraped_2, scrapedthumbnail, scrapedtitle, scrapedpuntuacion in matches:

        scrapedurl = scraped_2
        scrapedcalidad = scraped_1
        if "/?s=" in item.url:
            scrapedurl = scraped_1
            scrapedcalidad = scraped_2

        title = scrapertools.decodeHtmlentities( scrapedtitle )
        title+= " (" + scrapedcalidad + ") (" + scrapedpuntuacion + ")"

        ## ------------------------------------------------
        scrapedthumbnail+= "|" + _headers
        ## ------------------------------------------------

        itemlist.append( Item( channel=__channel__, action="findvideos", title=title, url=scrapedurl, thumbnail=scrapedthumbnail, fulltitle=title, show=scrapedtitle ) )

    ## Paginación
    next_page = scrapertools.find_single_match( data, '<a class="next page-numbers" href="([^"]+)">' )
    if next_page != "":
        itemlist.append( Item( channel=__channel__, action="fichas" , title=">> Successivo" , url=next_page ) )

    return itemlist
	
def categorias(item):
    logger.info("[altadefinizioneclick.py] categorias")
    itemlist = []

    data = anti_cloudflare(item.url)

 

    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data, '<ul class="listSubCat" id="Film">(.*?)</ul>')

    # The categories are the options for the combo  
    patron = '<li><a href="([^"]+)">([^<]+)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for url, titulo in matches:
        scrapedtitle = titulo
        scrapedurl = urlparse.urljoin(item.url, url)
        scrapedthumbnail = ""

        itemlist.append(
            Item(channel=__channel__,
                 action="fichas",
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail))

    return itemlist
	
def categorias1(item):
    logger.info("[altadefinizioneclick.py] categorias1")
    itemlist = []

    data = anti_cloudflare(item.url)

 

    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data, '<ul class="listSubCat" id="Anno">(.*?)</ul>')

    # The categories are the options for the combo  
    patron = '<li><a href="([^"]+)">([^<]+)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for url, titulo in matches:
        scrapedtitle = titulo
        scrapedurl = urlparse.urljoin(item.url, url)
        scrapedthumbnail = ""

        itemlist.append(
            Item(channel=__channel__,
                 action="fichas",
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail))

    return itemlist
	
def categorias2(item):
    logger.info("[altadefinizioneclick.py] categorias2")
    itemlist = []

    data = anti_cloudflare(item.url)

 

    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data, '<ul class="listSubCat" id="Qualita">(.*?)</ul>')

    # The categories are the options for the combo  
    patron = '<li><a href="([^"]+)">([^<]+)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for url, titulo in matches:
        scrapedtitle = titulo
        scrapedurl = urlparse.urljoin(item.url, url)
        scrapedthumbnail = ""

        itemlist.append(
            Item(channel=__channel__,
                 action="fichas",
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail))

    return itemlist
		


# def findvideos( item ):
#     logger.info( "[altadefinizioneclick.py] findvideos" )
#
#     itemlist = []
#
#     ## Descarga la página
#     data = anti_cloudflare( item.url )
#
#     locate = scrapertools.get_match( data, '<iframe width="100%" height="500px" src="([^"]+)" allowfullscreen></iframe>' )
#
#     try:
#         data = anti_cloudflare( locate )
#         scrapedurl = scrapertools.get_match( data, '<source src="([^"]+)"' )
#     except: scrapedurl = locate
#
#     server = scrapedurl.split( '/' )[2].split( '.' )
#     if len(server) == 3: server = server[1]
#     else: server = server[0]
#
#     title = "[" + server + "] " + item.fulltitle
#
#     itemlist.append( Item( channel=__channel__, action="play" , title=title, url=scrapedurl, thumbnail=item.thumbnail, fulltitle=item.fulltitle, show=item.show, folder=False ) )
#
#     return itemlist


def findvideos( item ):
    logger.info( "[altadefinizioneclick.py] findvideos" )

    ## Descarga la página
    data = anti_cloudflare( item.url )

    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        videoitem.title = "".join([item.title, videoitem.title])
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.show = item.show
        videoitem.channel = __channel__

    return itemlist


def anti_cloudflare(url):
    # global headers

    try:
        resp_headers = scrapertools.get_headers_from_response(url, headers=headers)
        resp_headers = dict(resp_headers)
    except urllib2.HTTPError, e:
        resp_headers = e.headers

    if 'refresh' in resp_headers:
        time.sleep(int(resp_headers['refresh'][:1]))

        # dict_headers = {v[0]: v[1] for v in headers}
        # dict_headers['cookie'] = resp_headers['set-cookie'].split(';')[0]

        # resp_headers = scrapertools.get_headers_from_response(sito + resp_headers['refresh'][7:], headers=[[k, v] for k, v in dict_headers.iteritems()])
        scrapertools.get_headers_from_response(host + "/" + resp_headers['refresh'][7:], headers=headers)
        # resp_headers = {v[0]: v[1] for v in resp_headers}

        # dict_headers['cookie'] = dict_headers['cookie'] + resp_headers['set-cookie'].split(';')[0]
        # headers = [[k, v] for k, v in dict_headers.iteritems()]

    return scrapertools.cache_page(url, headers=headers)
