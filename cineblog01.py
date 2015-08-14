# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para cineblog01
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# ------------------------------------------------------------
import urlparse
import sys
import re

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

sito = "http://www.cb01.eu"

DEBUG = config.get_setting("debug")


def isGeneric():
    return True


def mainlist(item):
    logger.info("[cineblog01.py] mainlist")

    # Main options
    itemlist = [Item(channel=__channel__,
                     action="peliculasrobalo",
                     title="[COLOR azure]Cinema - Novita'[/COLOR]",
                     url=sito,
                     thumbnail="http://dc584.4shared.com/img/XImgcB94/s7/13feaf0b538/saquinho_de_pipoca_01"),
				Item(channel=__channel__,
                     action="peliculasrobalo",
                     title="[COLOR azure]Alta Definizione [HD][/COLOR]",
                     url="http://www.cb01.eu/tag/film-hd-altadefinizione/",
                     thumbnail="http://jcrent.com/apple%20tv%20final/HD.png"),
                Item(channel=__channel__,
                     action="menugeneros",
                     title="[COLOR azure]Per Genere[/COLOR]",
                     url=sito,
                     thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/All%20Movies%20by%20Genre.png"),
                Item(channel=__channel__,
                     action="menuanyos",
                     title="[COLOR azure]Per Anno[/COLOR]",
                     url=sito,
                     thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/Movie%20Year.png"),
                Item(channel=__channel__,
                     action="search",
                     title="[COLOR azure]Cerca Film[/COLOR]",
                     extra="newsearch",
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search"),
                Item(channel=__channel__,
                     action="listserie",
                     title="[COLOR azure]Serie Tv - Novita'[/COLOR]",
                     url="http://www.cb01.eu/serietv/",
                     thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/New%20TV%20Shows.png"),
                Item(channel=__channel__,
                     action="search",
                     title="[COLOR azure]Cerca Serie Tv[/COLOR]",
                     extra="serie",
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search"),
                Item(channel=__channel__,
                     action="listanime",
                     title="[COLOR azure]Anime - Novita'[/COLOR]",
                     url="http://www.cineblog01.cc/anime/",
                     thumbnail="http://orig09.deviantart.net/df5a/f/2014/169/2/a/fist_of_the_north_star_folder_icon_by_minacsky_saya-d7mq8c8.png"),
                Item(channel=__channel__,
                     action="listaaz",
                     title="[COLOR azure]Anime - Lista A-Z[/COLOR]",
                     url="http://www.cineblog01.cc/anime/lista-completa-anime-cartoon/",
                     thumbnail="http://i.imgur.com/IjCmx5r.png"),
                Item(channel=__channel__,
                     action="animegenere",
                     title="[COLOR azure]Anime Per Genere[/COLOR]",
                     url="http://www.cineblog01.cc/anime/",
                     thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/Genres.png"),
                Item(channel=__channel__,
                     action="search",
                     title="[COLOR azure]Cerca Anime[/COLOR]",
                     extra="cartoni",
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search")]

    return itemlist


def peliculasrobalo(item):
    logger.info("[cineblog01.py] mainlist")
    itemlist = []

    if item.url == "":
        item.url = sito

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    logger.info(data)

    # Extrae las entradas (carpetas)
    patronvideos = '<div class="span4".*?<a.*?<p><img src="([^"]+)".*?'
    patronvideos += '<div class="span8">.*?<a href="([^"]+)"> <h1>([^"]+)</h1></a>.*?'
    patronvideos += '<p><strong>.*?</strong>.*?<br />([^"]+)<a href'
    matches = re.compile(patronvideos, re.DOTALL).finditer(data)

    for match in matches:
        scrapedtitle = scrapertools.unescape(match.group(3))
        scrapedurl = urlparse.urljoin(item.url, match.group(2))
        scrapedthumbnail = urlparse.urljoin(item.url, match.group(1))
        scrapedthumbnail = scrapedthumbnail.replace(" ", "%20")
        scrapedplot = scrapertools.unescape(match.group(4))
        scrapedplot = scrapertools.htmlclean(scrapedplot).strip()
        if DEBUG: logger.info(
            "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(
            Item(channel=__channel__,
                 action="findvid",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot, viewmode="movie_with_plot",
                 fanart=scrapedthumbnail))

    # Next page mark
    try:
        bloque = scrapertools.get_match(data, "<div id='wp_page_numbers'>(.*?)</div>")
        patronvideos = '<a href="([^"]+)">></a></li>'
        matches = re.compile(patronvideos, re.DOTALL).findall(bloque)
        scrapertools.printMatches(matches)

        if len(matches) > 0:
            scrapedtitle = "[COLOR orange]Successivo>>[/COLOR]"
            scrapedurl = matches[0]
            scrapedthumbnail = ""
            scrapedplot = ""
            if (DEBUG): logger.info(
                "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")

            itemlist.append(
                Item(channel=__channel__,
                     action="peliculasrobalo",
                     title=scrapedtitle,
                     url=scrapedurl,
                     thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png",
                     plot=scrapedplot))
    except:
        pass

    return itemlist


def peliculas(item):
    logger.info("[cineblog01.py] mainlist")
    itemlist = []

    if item.url == "":
        item.url = sito

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    logger.info(data)

    # Extrae las entradas (carpetas)
    patronvideos = '<div class="span4".*?<a.*?<p><img src="([^"]+)".*?'
    patronvideos += '<div class="span8">.*?<a href="([^"]+)"> <h1>([^"]+)</h1></a>.*?'
    patronvideos += '<p><strong>.*?</strong>.*?<br />([^"]+)<a href'
    matches = re.compile(patronvideos, re.DOTALL).finditer(data)

    for match in matches:
        scrapedtitle = scrapertools.unescape(match.group(3))
        scrapedurl = urlparse.urljoin(item.url, match.group(2))
        scrapedthumbnail = urlparse.urljoin(item.url, match.group(1))
        scrapedthumbnail = scrapedthumbnail.replace(" ", "%20")
        scrapedplot = scrapertools.unescape(match.group(4))
        scrapedplot = scrapertools.htmlclean(scrapedplot).strip()
        if DEBUG: logger.info(
            "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 viewmode="movie_with_plot",
                 fanart=scrapedthumbnail))

    # Next page mark
    try:
        bloque = scrapertools.get_match(data, "<div id='wp_page_numbers'>(.*?)</div>")
        patronvideos = '<a href="([^"]+)">></a></li>'
        matches = re.compile(patronvideos, re.DOTALL).findall(bloque)
        scrapertools.printMatches(matches)

        if len(matches) > 0:
            scrapedtitle = "[COLOR orange]Successivo>>[/COLOR]"
            scrapedurl = matches[0]
            scrapedthumbnail = ""
            scrapedplot = ""
            if (DEBUG): logger.info(
                "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")

            itemlist.append(
                Item(channel=__channel__,
                     action="peliculas",
                     title=scrapedtitle,
                     url=scrapedurl,
                     thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png",
                     plot=scrapedplot))
    except:
        pass

    return itemlist


def menugeneros(item):
    logger.info("[cineblog01.py] menugeneros")
    itemlist = []

    data = scrapertools.cache_page(item.url)
    logger.info(data)

    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data, '<select name="select2"(.*?)</select')

    # The categories are the options for the combo  
    patron = '<option value="([^"]+)">([^<]+)</option>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for url, titulo in matches:
        scrapedtitle = titulo
        scrapedurl = urlparse.urljoin(item.url, url)
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info(
            "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculasrobalo",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot))

    return itemlist


def menuanyos(item):
    logger.info("[cineblog01.py] menuvk")
    itemlist = []

    data = scrapertools.cache_page(item.url)
    logger.info(data)

    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data, '<select name="select3"(.*?)</select')

    # The categories are the options for the combo  
    patron = '<option value="([^"]+)">([^<]+)</option>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for url, titulo in matches:
        scrapedtitle = titulo
        scrapedurl = urlparse.urljoin(item.url, url)
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info(
            "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculasrobalo",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot))

    return itemlist


# Al llamarse "search" la función, el launcher pide un texto a buscar y lo añade como parámetro
def search(item, texto):
    logger.info("[cineblog01.py] " + item.url + " search " + texto)

    try:

        if item.extra == "serie":
            item.url = "http://www.cb01.eu/serietv/?s=" + texto
            return listserie(item)
        if item.extra == "cartoni":
            item.url = "http://www.cineblog01.cc/anime/?s=" + texto
            return listanime(item)
        if item.extra == "newsearch":
            item.url = "http://www.cb01.eu/?s=" + texto
            return peliculasrobalo(item)
        else:
            item.url = "http://www.cb01.eu/?s=" + texto
            return peliculas(item)

    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def listserie(item):
    logger.info("[cineblog01.py] mainlist")
    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    logger.info(data)

    # Extrae las entradas (carpetas)
    patronvideos = '<div class="span4">\s*<a href="([^"]+)"><img src="([^"]+)".*?<div class="span8">.*?<h1>([^<]+)</h1></a>(.*?)<br><a'
    matches = re.compile(patronvideos, re.DOTALL).finditer(data)

    for match in matches:
        scrapedtitle = scrapertools.unescape(match.group(3))
        scrapedurl = match.group(1)
        scrapedthumbnail = match.group(2)
        scrapedplot = scrapertools.unescape(match.group(4))
        scrapedplot = scrapertools.htmlclean(scrapedplot).strip()
        if (DEBUG): logger.info(
            "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")

        # Añade al listado de XBMC
        itemlist.append(
            Item(channel=__channel__,
                 action="findvid_serie",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot))

    # Put the next page mark
    try:
        next_page = scrapertools.get_match(data, "<link rel='next' href='([^']+)'")
        itemlist.append(
            Item(channel=__channel__,
                 action="listserie",
                 title="[COLOR orange]Successivo>>[/COLOR]",
                 url=next_page,
                 thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png", ))
    except:
        pass

    return itemlist


def animestream(item):
    logger.info("[cineblog01.py] mainlist")
    itemlist = []

    if item.url == "":
        item.url = sito

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    logger.info(data)

    # Extrae las entradas (carpetas)
    patronvideos = '<div class="span4"> <a.*?<p><img.*?src="(.*?)".*?'
    patronvideos += '<div class="span8">.*?<a href="(.*?)">.*?'
    patronvideos += '<h1>(.*?)</h1></a>.*?<br>-->(.*?)<br>.*?'
    matches = re.compile(patronvideos, re.DOTALL).finditer(data)

    for match in matches:
        scrapedtitle = scrapertools.unescape(match.group(3))
        scrapedurl = urlparse.urljoin(item.url, match.group(2))
        scrapedthumbnail = urlparse.urljoin(item.url, match.group(1))
        scrapedthumbnail = scrapedthumbnail.replace(" ", "%20")
        scrapedplot = scrapertools.unescape(match.group(4))
        scrapedplot = scrapertools.htmlclean(scrapedplot).strip()
        if (DEBUG): logger.info(
            "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(
            Item(channel=__channel__,
                 action="findvid_anime",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 viewmode="movie_with_plot",
                 fanart=scrapedthumbnail))

    # Next page mark
    try:
        bloque = scrapertools.get_match(data, "<div id='wp_page_numbers'>(.*?)</div>")
        patronvideos = '<a href="([^"]+)">></a></li>'
        matches = re.compile(patronvideos, re.DOTALL).findall(bloque)
        scrapertools.printMatches(matches)

        if len(matches) > 0:
            scrapedtitle = "[COLOR orange]Successivo>>[/COLOR]"
            scrapedurl = matches[0]
            scrapedthumbnail = ""
            scrapedplot = ""
            if (DEBUG): logger.info(
                "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")

            itemlist.append(
                Item(channel=__channel__,
                     action="animestream",
                     title=scrapedtitle,
                     url=scrapedurl,
                     thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png",
                     plot=scrapedplot))
    except:
        pass

    return itemlist


def listaaz(item):
    logger.info("[cineblog01.py] listaaz")
    itemlist = []

    data = scrapertools.cache_page(item.url)
    logger.info(data)

    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data, '<a href="#char_5a" title="Go to the letter Z">Z</a></span></div>(.*?)</ul></div><div style="clear:both;"></div></div>')

    # The categories are the options for the combo  
    patron = '<li><a href="([^"]+)"><span class="head">([^<]+)</span></a></li>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for url, titulo in matches:
        scrapedtitle = titulo
        scrapedurl = url
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info("title=[" + scrapedtitle + "], url=[" + scrapedurl + "]")
        itemlist.append(
            Item(channel=__channel__,
                 action="findvid_anime",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail="http://www.justforpastime.net/uploads/3/8/1/5/38155083/273372_orig.jpg",
                 plot=scrapedplot))

    return itemlist


def animegenere(item):
    logger.info("[cineblog01.py] animegenere")
    itemlist = []

    data = scrapertools.cache_page(item.url)
    logger.info(data)

    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data, '<select name="select2"(.*?)</select')

    # The categories are the options for the combo  
    patron = '<option value="([^"]+)">([^<]+)</option>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for url, titulo in matches:
        scrapedtitle = titulo
        scrapedurl = url
        scrapedthumbnail = ""
        scrapedplot = ""
        if DEBUG: logger.info(
            "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(
            Item(channel=__channel__,
                 action="animestream",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot))

    return itemlist


def listanime(item):
    logger.info("[cineblog01.py] mainlist")
    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    logger.info(data)

    # Extrae las entradas (carpetas)
    patronvideos = '<div class="span4"> <a.*?<img.*?src="(.*?)".*?'
    patronvideos += '<div class="span8">.*?<a href="(.*?)">.*?'
    patronvideos += '<h1>(.*?)</h1></a>.*?<br />(.*?)<br>.*?'
    matches = re.compile(patronvideos, re.DOTALL).finditer(data)

    for match in matches:
        scrapedthumbnail = match.group(1)
        scrapedurl = match.group(2)
        scrapedtitle = scrapertools.unescape(match.group(3))
        scrapedplot = scrapertools.unescape(match.group(4))
        if scrapedplot.startswith(""):
            scrapedplot = scrapedplot[149:]
        if DEBUG: logger.info("title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")

        # Añade al listado de XBMC
        itemlist.append(
            Item(channel=__channel__,
                 action="findvid_anime",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot))

    # Put the next page mark
    try:
        next_page = scrapertools.get_match(data, "<link rel='next' href='([^']+)'")
        itemlist.append(
            Item(channel=__channel__,
                 action="listanime",
                 title="[COLOR orange]Successivo>>[/COLOR]",
                 url=next_page,
                 thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png"))
    except:
        pass

    return itemlist


def findvid(item):
    logger.info("[cineblog01.py] findvideos")

    itemlist = []

    ## Descarga la página
    data = scrapertools.cache_page(item.url)
    data = scrapertools.decodeHtmlentities(data).replace('http://cineblog01.pw', 'http://k4pp4.pw')

    ## Extrae las entradas

    streaming = scrapertools.find_single_match(data, '<strong>Streaming:</strong>(.*?)<table height="30">')
    patron = '<td><a href="([^"]+)" target="_blank">([^<]+)</a></td>'
    matches = re.compile(patron, re.DOTALL).findall(streaming)
    for scrapedurl, scrapedtitle in matches:
        print "##### findvideos Streaming ## %s ## %s ##" % (scrapedurl, scrapedtitle)
        title = "[COLOR orange]Streaming:[/COLOR] " + item.title + " [COLOR blue][" + scrapedtitle + "][/COLOR]"
        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 title=title,
                 url=scrapedurl,
                 fulltitle=item.title,
                 show=item.title,
                 folder=False))

    streaming_hd = scrapertools.find_single_match(data, '<strong>Streaming HD[^<]+</strong>(.*?)<table height="30">')
    patron = '<td><a href="([^"]+)" target="_blank">([^<]+)</a></td>'
    matches = re.compile(patron, re.DOTALL).findall(streaming_hd)
    for scrapedurl, scrapedtitle in matches:
        print "##### findvideos Streaming HD ## %s ## %s ##" % (scrapedurl, scrapedtitle)
        title = "[COLOR yellow]Streaming HD:[/COLOR] " + item.title + " [COLOR blue][" + scrapedtitle + "][/COLOR]"
        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 title=title,
                 url=scrapedurl,
                 fulltitle=item.title,
                 show=item.title,
                 folder=False))

    download = scrapertools.find_single_match(data, '<strong>Download:</strong>(.*?)<table height="30">')
    patron = '<td><a href="([^"]+)" target="_blank">([^<]+)</a></td>'
    matches = re.compile(patron, re.DOTALL).findall(download)
    for scrapedurl, scrapedtitle in matches:
        print "##### findvideos Download ## %s ## %s ##" % (scrapedurl, scrapedtitle)
        title = "[COLOR aqua]Download:[/COLOR] " + item.title + " [COLOR blue][" + scrapedtitle + "][/COLOR]"
        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 title=title,
                 url=scrapedurl,
                 fulltitle=item.title,
                 show=item.title,
                 folder=False))

    download_hd = scrapertools.find_single_match(data, '<strong>Download HD[^<]+</strong>(.*?)<table width="100%" height="20">')
    patron = '<td><a href="([^"]+)" target="_blank">([^<]+)</a></td>'
    matches = re.compile(patron, re.DOTALL).findall(download_hd)
    for scrapedurl, scrapedtitle in matches:
        print "##### findvideos Download HD ## %s ## %s ##" % (scrapedurl, scrapedtitle)
        title = "[COLOR azure]Download HD:[/COLOR] " + item.title + " [COLOR blue][" + scrapedtitle + "][/COLOR]"
        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 title=title,
                 url=scrapedurl,
                 fulltitle=item.title,
                 show=item.title,
                 folder=False))

    if len(itemlist) == 0:
        itemlist = servertools.find_video_items(item=item)

    return itemlist


def findvid_serie(item):
    logger.info("[cineblog01.py] findvideos")

    itemlist = []

    ## Descarga la página
    data = scrapertools.cache_page(item.url)
    data = scrapertools.decodeHtmlentities(data).replace('http://cineblog01.pw', 'http://k4pp4.pw')

    patron1 = '<p(?:\s*style="[^"]*")?>(?:<strong>)?([^<]+)(<a.*?)(?:</strong>)?</p>'
    patron2 = '<a\s*href="([^"]+)"\s*target="_blank">([^<]+)</a>'
    matches1 = re.compile(patron1, re.DOTALL).finditer(data)
    for match1 in matches1:
        titulo = match1.group(1)
        links = match1.group(2)
        ## Extrae las entradas
        matches2 = re.compile(patron2, re.DOTALL).finditer(links)
        for match2 in matches2:
            scrapedurl = match2.group(1)
            scrapedtitle = match2.group(2)
            title = item.title + " " + titulo + " [COLOR blue][" + scrapedtitle + "][/COLOR]"
            itemlist.append(
                Item(channel=__channel__,
                     action="play",
                     title=title,
                     url=scrapedurl,
                     fulltitle=item.title,
                     show=item.title,
                     folder=False))

    return itemlist


def findvid_anime(item):
    logger.info("[cineblog01.py] findvideos")

    itemlist = []

    ## Descarga la página
    data = scrapertools.cache_page(item.url)
    data = scrapertools.decodeHtmlentities(data).replace('http://cineblog01.pw', 'http://k4pp4.pw')

    patron1 = '(?:<p>|<td bgcolor="#ECEAE1">)<span class="txt_dow">(.*?)</p>(?:\s*</span>)?\s*</td>'
    patron2 = '<a.+?href="([^"]+)"[^>]*>([^<]+)</a>'
    matches1 = re.compile(patron1, re.DOTALL).findall(data)

    if len(matches1) > 0:
        for match1 in re.split('<br />|<p>', matches1[0]):
            if len(match1) > 0:
                ## Extrae las entradas
                titulo = None
                matches2 = re.compile(patron2, re.DOTALL).finditer(match1)
                for match2 in matches2:
                    if titulo is None:
                        titulo = match2.group(2)
                    scrapedurl = match2.group(1)
                    scrapedtitle = match2.group(2)
                    title = item.title + " " + titulo + " [COLOR blue][" + scrapedtitle + "][/COLOR]"
                    itemlist.append(
                        Item(channel=__channel__,
                             action="play",
                             title=title,
                             url=scrapedurl,
                             fulltitle=item.title,
                             show=item.title,
                             folder=False))

    return itemlist


def play(item):
    logger.info("[cineblog01.py] play")

    data = scrapertools.cache_page(item.url)

    print "##############################################################"
    if "go.php" in item.url:
        data = scrapertools.get_match(data, 'window.location.href = "([^"]+)";')
        print "##### play go.php data ##\n%s\n##" % data
    elif "/link/" in item.url:
        from lib.jsbeautifier.unpackers import packer

        try:
            data = scrapertools.get_match(data, "(eval.function.p,a,c,k,e,.*?)</script>")
            data = packer.unpack(data)
            print "##### play /link/ unpack ##\n%s\n##" % data
        except IndexError:
            print "##### The content is yet unpacked"

        data = scrapertools.get_match(data, 'var link(?:\s)?=(?:\s)?"([^"]+)";')
        print "##### play /link/ data ##\n%s\n##" % data
    else:
        data = item.url
        print "##### play else data ##\n%s\n##" % data
    print "##############################################################"

    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        videoitem.title = item.show
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = __channel__

    return itemlist