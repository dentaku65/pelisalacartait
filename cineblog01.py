# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para cineblog01
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os
import sys
import re, htmlentitydefs

from servers import servertools
from core import scrapertools
from core import logger
from core import config
from core.item import Item

__channel__ = "cineblog01"
__category__ = "F,S,A"
__type__ = "generic"
__title__ = "CineBlog 01"
__language__ = "IT"

sito="http://www.cb01.eu"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("[cineblog01.py] mainlist")
    itemlist = []


    # Main options
    itemlist.append( Item(channel=__channel__, action="peliculasrobalo"  , title="[COLOR azure]Cinema - Novita'[/COLOR]" , url=sito, extra="newsearch",thumbnail="http://dc584.4shared.com/img/XImgcB94/s7/13feaf0b538/saquinho_de_pipoca_01"))
    itemlist.append( Item(channel=__channel__, action="menugeneros", title="[COLOR azure]Per Genere[/COLOR]" , url=sito , thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/All%20Movies%20by%20Genre.png"))
    itemlist.append( Item(channel=__channel__, action="menuanyos"  , title="[COLOR azure]Per Anno[/COLOR]" , url=sito , thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/Movie%20Year.png"))
    itemlist.append( Item(channel=__channel__, action="search"     , title="[COLOR azure]Cerca Film[/COLOR]", extra="newsearch", thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search"))
    itemlist.append( Item(channel=__channel__, action="listserie"  , title="[COLOR azure]Serie Tv - Novita'[/COLOR]" , url="http://www.cb01.eu/serietv/" , thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/New%20TV%20Shows.png"))
    itemlist.append( Item(channel=__channel__, action="search", title="[COLOR azure]Cerca Serie Tv[/COLOR]" , extra="serie" , thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search"))
    itemlist.append( Item(channel=__channel__, action="listanime"  , title="[COLOR azure]Anime - Novita'[/COLOR]" , url="http://www.cineblog01.cc/anime/" , thumbnail="http://orig09.deviantart.net/df5a/f/2014/169/2/a/fist_of_the_north_star_folder_icon_by_minacsky_saya-d7mq8c8.png"))
    itemlist.append( Item(channel=__channel__, action="listaaz"  , title="[COLOR azure]Anime - Lista A-Z[/COLOR]" , url="http://www.cineblog01.cc/anime/lista-completa-anime-cartoon/" , thumbnail="http://th07.deviantart.net/fs71/PRE/i/2012/046/0/1/lamu_chan_by_akakit-d32zg1w.png"))
    itemlist.append( Item(channel=__channel__, action="animegenere"  , title="[COLOR azure]Anime Per Genere[/COLOR]" , url="http://www.cineblog01.cc/anime/" , thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/Genres.png"))
    itemlist.append( Item(channel=__channel__, action="search", title="[COLOR azure]Cerca Anime[/COLOR]" , extra="cartoni", thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search"))

    return itemlist

def peliculasrobalo(item):
    logger.info("[cineblog01.py] mainlist")
    itemlist = []

    if item.url =="":
        item.url = sito

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    logger.info(data)

    # Extrae las entradas (carpetas)
    patronvideos = '<div class="span4".*?<a.*?<p><img src="([^"]+)".*?'                    
    patronvideos += '<div class="span8">.*?<a href="([^"]+)"> <h1>([^"]+)</h1></a>.*?'
    patronvideos += '<p><strong>.*?</strong>.*?<br />([^"]+)<a href'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for match in matches:
        scrapedtitle = scrapertools.unescape(match[2])
        scrapedurl = urlparse.urljoin(item.url,match[1])
        scrapedthumbnail = urlparse.urljoin(item.url,match[0])
        scrapedthumbnail = scrapedthumbnail.replace(" ", "%20");
        scrapedplot = scrapertools.unescape(match[3])
        scrapedplot = scrapertools.htmlclean(scrapedplot).strip()
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="findvid" , title="[COLOR azure]"+scrapedtitle+"[/COLOR]", url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot, viewmode="movie_with_plot", fanart=scrapedthumbnail))

    # Next page mark
    try:
        bloque = scrapertools.get_match(data,"<div id='wp_page_numbers'>(.*?)</div>")
        patronvideos = '<a href="([^"]+)">></a></li>'
        matches = re.compile (patronvideos, re.DOTALL).findall (data)
        scrapertools.printMatches (matches)
    
        if len(matches)>0:
            scrapedtitle = "[COLOR orange]Successivo>>[/COLOR]"
            scrapedurl = matches[0]
            scrapedthumbnail = ""
            scrapedplot = ""
            if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
    
            itemlist.append( Item(channel=__channel__, action="peliculasrobalo" , title=scrapedtitle , url=scrapedurl, thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png", plot=scrapedplot))
    except:
        pass

    return itemlist

def peliculas(item):
    logger.info("[cineblog01.py] mainlist")
    itemlist = []

    if item.url =="":
        item.url = sito

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    logger.info(data)

    # Extrae las entradas (carpetas)
    patronvideos = '<div class="span4".*?<a.*?<p><img src="([^"]+)".*?'                    
    patronvideos += '<div class="span8">.*?<a href="([^"]+)"> <h1>([^"]+)</h1></a>.*?'
    patronvideos += '<p><strong>.*?</strong>.*?<br />([^"]+)<a href'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for match in matches:
        scrapedtitle = scrapertools.unescape(match[2])
        scrapedurl = urlparse.urljoin(item.url,match[1])
        scrapedthumbnail = urlparse.urljoin(item.url,match[0])
        scrapedthumbnail = scrapedthumbnail.replace(" ", "%20");
        scrapedplot = scrapertools.unescape(match[3])
        scrapedplot = scrapertools.htmlclean(scrapedplot).strip()
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="findvideos" , title="[COLOR azure]"+scrapedtitle+"[/COLOR]", url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot, viewmode="movie_with_plot", fanart=scrapedthumbnail))

    # Next page mark
    try:
        bloque = scrapertools.get_match(data,"<div id='wp_page_numbers'>(.*?)</div>")
        patronvideos = '<a href="([^"]+)">></a></li>'
        matches = re.compile (patronvideos, re.DOTALL).findall (data)
        scrapertools.printMatches (matches)
    
        if len(matches)>0:
            scrapedtitle = "[COLOR orange]Successivo>>[/COLOR]"
            scrapedurl = matches[0]
            scrapedthumbnail = ""
            scrapedplot = ""
            if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
    
            itemlist.append( Item(channel=__channel__, action="peliculas" , title=scrapedtitle , url=scrapedurl, thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png", plot=scrapedplot))
    except:
        pass

    return itemlist

def menugeneros(item):
    logger.info("[cineblog01.py] menugeneros")
    itemlist = []
    
    data = scrapertools.cache_page(item.url)
    logger.info(data)

    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data,'<select name="select2"(.*?)</select')
    
    # The categories are the options for the combo  
    patron = '<option value="([^"]+)">([^<]+)</option>'
    matches = re.compile(patron,re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for url,titulo in matches:
        scrapedtitle = titulo
        scrapedurl = urlparse.urljoin(item.url,url)
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="peliculasrobalo" , title="[COLOR azure]"+scrapedtitle+"[/COLOR]" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot))

    return itemlist


def menuanyos(item):
    logger.info("[cineblog01.py] menuvk")
    itemlist = []
    
    data = scrapertools.cache_page(item.url)
    logger.info(data)
    
    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data,'<select name="select3"(.*?)</select')
    
    # The categories are the options for the combo  
    patron = '<option value="([^"]+)">([^<]+)</option>'
    matches = re.compile(patron,re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for url,titulo in matches:
        scrapedtitle = titulo
        scrapedurl = urlparse.urljoin(item.url,url)
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="peliculasrobalo" , title="[COLOR azure]"+scrapedtitle+"[/COLOR]" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot))

    return itemlist

# Al llamarse "search" la función, el launcher pide un texto a buscar y lo añade como parámetro
def search(item,texto):
    logger.info("[cineblog01.py] "+item.url+" search "+texto)

    try:

        if item.extra=="serie":
            item.url = "http://www.cb01.eu/serietv/?s="+texto
            return listserie(item)
        if item.extra=="cartoni":
            item.url = "http://www.cineblog01.cc/anime/?s="+texto
            return listanime(item)
        if item.extra=="newsearch":
            item.url = "http://www.cb01.eu/?s="+texto
            return peliculasrobalo(item)
        else:
            item.url = "http://www.cb01.eu/?s="+texto
            return peliculas(item)

    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []

def listserie(item):
    logger.info("[cineblog01.py] mainlist")
    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    logger.info(data)

    # Extrae las entradas (carpetas)
    patronvideos = '<div class="span4".*?<a.*?<p><img src="(.*?)".*?'                    
    patronvideos += '<div class="span8">.*?<a href="(.*?)">.*?'
    patronvideos += '<h1>(.*?)</h1>(.*?)</a>'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for match in matches:
        scrapedtitle = scrapertools.unescape(match[2])
        scrapedurl = urlparse.urljoin(item.url,match[1])
        scrapedthumbnail = urlparse.urljoin(item.url,match[0])
        scrapedplot = scrapertools.unescape(match[3])
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")

        # Añade al listado de XBMC
        itemlist.append( Item(channel=__channel__, action="findvideos" , title="[COLOR azure]"+scrapedtitle+"[/COLOR]", url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot))

    # Put the next page mark
    try:
        next_page = scrapertools.get_match(data,"<link rel='next' href='([^']+)'")
        itemlist.append( Item(channel=__channel__, action="listserie" , title="[COLOR orange]Successivo>>[/COLOR]" , url=next_page, thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png", plot=scrapedplot))
    except:
        pass

    return itemlist

def animestream(item):
    logger.info("[cineblog01.py] mainlist")
    itemlist = []

    if item.url =="":
        item.url = sito

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    logger.info(data)

    # Extrae las entradas (carpetas)
    patronvideos  = '<div class="span4"> <a.*?<p><img.*?src="(.*?)".*?'
    patronvideos += '<div class="span8">.*?<a href="(.*?)">.*?'
    patronvideos += '<h1>(.*?)</h1></a>.*?<br>-->(.*?)<br>.*?'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for match in matches:
        scrapedtitle = scrapertools.unescape(match[2])
        scrapedurl = urlparse.urljoin(item.url,match[1])
        scrapedthumbnail = urlparse.urljoin(item.url,match[0])
        scrapedthumbnail = scrapedthumbnail.replace(" ", "%20");
        scrapedplot = scrapertools.unescape(match[3])
        scrapedplot = scrapertools.htmlclean(scrapedplot).strip()
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="findvideos" ,title="[COLOR azure]"+scrapedtitle+"[/COLOR]", url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot, viewmode="movie_with_plot", fanart=scrapedthumbnail))

    # Next page mark
    try:
        bloque = scrapertools.get_match(data,"<div id='wp_page_numbers'>(.*?)</div>")
        patronvideos = '<a href="([^"]+)">></a></li>'
        matches = re.compile (patronvideos, re.DOTALL).findall (data)
        scrapertools.printMatches (matches)
    
        if len(matches)>0:
            scrapedtitle = "[COLOR orange]Successivo>>[/COLOR]"
            scrapedurl = matches[0]
            scrapedthumbnail = ""
            scrapedplot = ""
            if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
    
            itemlist.append( Item(channel=__channel__, action="peliculas" , title=scrapedtitle , url=scrapedurl, thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png", plot=scrapedplot))
    except:
        pass

    return itemlist

def listaaz(item):
    logger.info("[cineblog01.py] listaaz")
    itemlist = []
    
    data = scrapertools.cache_page(item.url)
    logger.info(data)

    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data,'<a href="#char_5a" title="Go to the letter Z">Z</a></span></div>(.*?)</ul></div><div style="clear:both;"></div></div>')
    
    # The categories are the options for the combo  
    patron = '<li><a href="([^"]+)"><span class="head">([^<]+)</span></a></li>'
    matches = re.compile(patron,re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for url,titulo in matches:
        scrapedtitle = titulo
        scrapedurl = urlparse.urljoin(item.url,url)
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"]")
        itemlist.append( Item(channel=__channel__, action="findvideos" , title="[COLOR azure]"+scrapedtitle+"[/COLOR]" , url=scrapedurl, thumbnail="http://www.justforpastime.net/uploads/3/8/1/5/38155083/273372_orig.jpg", plot=scrapedplot))

    return itemlist

def animegenere(item):
    logger.info("[cineblog01.py] animegenere")
    itemlist = []
    
    data = scrapertools.cache_page(item.url)
    logger.info(data)

    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data,'<select name="select2"(.*?)</select')
    
    # The categories are the options for the combo  
    patron = '<option value="([^"]+)">([^<]+)</option>'
    matches = re.compile(patron,re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for url,titulo in matches:
        scrapedtitle = titulo
        scrapedurl = urlparse.urljoin(item.url,url)
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="animestream" ,title="[COLOR azure]"+scrapedtitle+"[/COLOR]", url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot))

    return itemlist

def listanime(item):
    logger.info("[cineblog01.py] mainlist")
    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    logger.info(data)

    # Extrae las entradas (carpetas)
    patronvideos  = '<div class="span4"> <a.*?<img.*?src="(.*?)".*?'
    patronvideos += '<div class="span8">.*?<a href="(.*?)">.*?'
    patronvideos += '<h1>(.*?)</h1></a>.*?<br />(.*?)<br>.*?'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for match in matches:
        scrapedthumbnail = urlparse.urljoin(item.url,match[0])
        scrapedurl = urlparse.urljoin(item.url,match[1])
        scrapedtitle = scrapertools.unescape(match[2])
        scrapedplot = scrapertools.unescape(match[3])
        if scrapedplot.startswith(""):
           scrapedplot = scrapedplot[149:]
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")

        # Añade al listado de XBMC
        itemlist.append( Item(channel=__channel__, action="findvideos" ,title="[COLOR azure]"+scrapedtitle+"[/COLOR]" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot))

    # Put the next page mark
    try:
        next_page = scrapertools.get_match(data,"<link rel='next' href='([^']+)'")
        itemlist.append( Item(channel=__channel__, action="listanime" , title="[COLOR orange]Successivo>>[/COLOR]" , url=next_page, thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png", plot=scrapedplot))
    except:
        pass

    return itemlist


def findvid( item ):
    logger.info( "[cineblog01.py] findvideos" )

    itemlist = []

    ## Descarga la página
    data = scrapertools.cache_page( item.url )
    data = scrapertools.decodeHtmlentities( data ).replace( 'http://cineblog01.pw', 'http://k4pp4.pw' )

    ## Extrae las entradas

    streaming = scrapertools.find_single_match( data, '<strong>Streaming:</strong>(.*?)<table height="30">' )
    patron = '<td><a href="([^"]+)" target="_blank">([^<]+)</a></td>'
    matches = re.compile( patron, re.DOTALL ).findall( streaming )
    for scrapedurl, scrapedtitle in matches:
        print "##### findvideos Streaming ## %s ## %s ##" % ( scrapedurl, scrapedtitle )
        title = "[COLOR orange]Streaming:[/COLOR] " + item.title + " [COLOR blue][" + scrapedtitle + "][/COLOR]"
        itemlist.append( Item( channel=__channel__, action="play", title=title, url=scrapedurl, folder=False ) )

    streaming_hd = scrapertools.find_single_match( data, '<strong>Streaming HD[^<]+</strong>(.*?)<table height="30">' )
    patron = '<td><a href="([^"]+)" target="_blank">([^<]+)</a></td>'
    matches = re.compile( patron, re.DOTALL ).findall( streaming_hd )
    for scrapedurl, scrapedtitle in matches:
        print "##### findvideos Streaming HD ## %s ## %s ##" % ( scrapedurl, scrapedtitle )
        title = "[COLOR yellow]Streaming HD:[/COLOR] " + item.title + " [COLOR blue][" + scrapedtitle + "][/COLOR]"
        itemlist.append( Item( channel=__channel__, action="play", title=title, url=scrapedurl, folder=False ) )

    download = scrapertools.find_single_match( data, '<strong>Download:</strong>(.*?)<table height="30">' )
    patron = '<td><a href="([^"]+)" target="_blank">([^<]+)</a></td>'
    matches = re.compile( patron, re.DOTALL ).findall( download )
    for scrapedurl, scrapedtitle in matches:
        print "##### findvideos Download ## %s ## %s ##" % ( scrapedurl, scrapedtitle )
        title = "[COLOR aqua]Download:[/COLOR] " + item.title + " [COLOR blue][" + scrapedtitle + "][/COLOR]"
        itemlist.append( Item( channel=__channel__, action="play", title=title, url=scrapedurl, folder=False ) )

    download_hd = scrapertools.find_single_match( data, '<strong>Download HD[^<]+</strong>(.*?)<table width="100%" height="20">' )
    patron = '<td><a href="([^"]+)" target="_blank">([^<]+)</a></td>'
    matches = re.compile( patron, re.DOTALL ).findall( download_hd )
    for scrapedurl, scrapedtitle in matches:
        print "##### findvideos Download HD ## %s ## %s ##" % ( scrapedurl, scrapedtitle )
        title = "[COLOR azure]Download HD:[/COLOR] " + item.title + " [COLOR blue][" + scrapedtitle + "][/COLOR]"
        itemlist.append( Item( channel=__channel__, action="play", title=title, url=scrapedurl, folder=False ) )

    if len(itemlist) == 0:
        itemlist = servertools.find_video_items(item=item)

    return itemlist

def play( item ):
    
    logger.info( "[cineblog01.py] play" )

    data = scrapertools.cache_page( item.url )

    print "##############################################################"
    if "go.php" in item.url:
        data = scrapertools.get_match( data, 'window.location.href = "([^"]+)";' )
        print "##### play go.php data ##\n%s\n##" % data
    elif "/link/" in item.url:
        from lib.jsbeautifier.unpackers import packer

        try:
            data = scrapertools.get_match( data, "(eval.function.p,a,c,k,e,.*?)</script>" )
            data = packer.unpack( data )
            print "##### play /link/ unpack ##\n%s\n##" % data
        except IndexError:
            print "##### The content is yet unpacked"

        data = scrapertools.get_match( data, 'var link(?:\s)?=(?:\s)?"([^"]+)";' )
        print "##### play /link/ data ##\n%s\n##" % data
    else:
        data = item.url
        print "##### play else data ##\n%s\n##" % data
    print "##############################################################"

    itemlist = servertools.find_video_items( data=data )
    
    for videoitem in itemlist:
        videoitem.title = item.show
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = __channel__

    return itemlist    


# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():
    bien = True
    
    # mainlist
    mainlist_items = mainlist(Item())
    
    # Comprueba que todas las opciones por categorias tengan algo (excepto los buscadores)
    for mainlist_item in mainlist_items:
        if mainlist_item.action.startswith("menu"):
            exec "itemlist = "+mainlist_item.action+"(mainlist_item)"
            
            # Lee la primera categoría sólo
            exec "itemlist2 ="+itemlist[0].action+"(itemlist[0])"
            if len(itemlist2)==0:
                return false

    # Comprueba si alguno de los vídeos de "Novedades" devuelve mirrors
    for mainlist_item in mainlist_items:
        if mainlist_item.action=="peliculas" or mainlist_item.action=="listserie":
            exec "itemlist = "+mainlist_item.action+"(mainlist_item)"
    
            bien = False
            for episodio_item in itemlist:
                from servers import servertools
                mirrors = servertools.find_video_items(item=episodio_item)
                if len(mirrors)>0:
                    bien = True
                    break

    return bien
