# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para itastreaming
# by DrZ3r0
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# ------------------------------------------------------------
import urllib2
import urlparse
import re
import sys
import binascii
import time

from core import logger
from core import config
from core import scrapertools
from core.item import Item

__channel__ = "itastreaming"
__category__ = "F,S,A"
__type__ = "generic"
__title__ = "ItaStreaming"
__language__ = "IT"

sito = "http://itastreaming.co/"

headers = [
    ['User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:38.0) Gecko/20100101 Firefox/38.0'],
    ['Accept-Encoding', 'gzip, deflate'],
    ['Referer', 'http://itastreaming.co/'],
    ['Connection', 'keep-alive']
]

DEBUG = config.get_setting("debug")


def isGeneric():
    return True


def mainlist(item):
    logger.info("pelisalacarta.itastreaming mainlist")

    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Ultimi film inseriti[/COLOR]",
                     action="peliculas",
                     url=sito,
                     thumbnail="http://dc584.4shared.com/img/XImgcB94/s7/13feaf0b538/saquinho_de_pipoca_01"),
                Item(channel=__channel__,
                     title="[COLOR azure]Categorie film[/COLOR]",
                     action="categorias",
                     url=sito,
                     thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/All%20Movies%20by%20Genre.png"),
                Item(channel=__channel__,
                     action="listaaz",
                     title="[COLOR azure]Film - Lista A-Z[/COLOR]",
                     url=sito,
                     thumbnail="http://repository-butchabay.googlecode.com/svn/branches/eden/skin.cirrus.extended.v2/extras/moviegenres/A-Z.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca...[/COLOR]",
                     action="search",
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search")]

    return itemlist


def peliculas(item):
    logger.info("pelisalacarta.itastreaming peliculas")
    itemlist = []

    # Descarga la pagina
    data = anti_cloudflare(item.url)

    # Extrae las entradas (carpetas)
    patron = '<div class="item">\s*<a href="([^"]+)" title="([^"]+)">\s*<div class="img">\s*<img src="([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        html = scrapertools.cache_page(scrapedurl, headers=headers)
        start = html.find('<div class="post-content">')
        end = html.find('</div>', start)
        scrapedplot = html[start:end]
        scrapedplot = re.sub(r'<.*?>', '', scrapedplot)

        if DEBUG: logger.info(
            "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")

        itemlist.append(
            Item(channel=__channel__,
                 action="findvid",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 viewmode="movie_with_plot",
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True))

    # Extrae el paginador
    patronvideos = "class=previouspostslink' href='([^']+)'>Seguente &rsaquo;"
    matches = re.compile(patronvideos, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png",
                 folder=True))

    return itemlist


def peliculas_search(item):
    logger.info("pelisalacarta.itastreaming peliculas")
    itemlist = []

    # Descarga la pagina
    data = anti_cloudflare(item.url)

    # Extrae las entradas (carpetas)
    patron = '<img class="imx" style="margin-top:0px;" src="([^"]+)" alt=.*?'
    patron += '<h3><a href="([^"]+)">([^<]+)</a></h3>.*?'
    patron += '<p>([^<]+)</p>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedthumbnail, scrapedurl, scrapedtitle, scrapedplot in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)

        if DEBUG: logger.info(
            "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")

        itemlist.append(
            Item(channel=__channel__,
                 action="findvid",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 viewmode="movie_with_plot",
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True))

    # Extrae el paginador
    patronvideos = "class=previouspostslink' href='([^']+)'>Seguente &rsaquo;"
    matches = re.compile(patronvideos, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_search",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png",
                 folder=True))

    return itemlist


def categorias(item):
    logger.info("pelisalacarta.itastreaming categorias")
    itemlist = []

    data = anti_cloudflare(item.url)

    start = data.find('<ul id="menu-cat1"')
    end = data.find('<div class="br"></div>', start)
    bloque = data[start:end]

    patron = '<a href="([^"]+)">([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedtitle in matches:
        # scrapedurl = urlparse.urljoin(item.url, scrapedurl)
        scrapedthumbnail = ""
        scrapedplot = ""
        if DEBUG: logger.info(
            "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot))

    return itemlist


def listaaz(item):
    logger.info("pelisalacarta.itastreaming listaaz")
    itemlist = []

    data = anti_cloudflare(item.url)

    start = data.find('<ul class="abc">')
    end = data.find('<div class="br"></div>', start)
    bloque = data[start:end]

    patron = '<li><a href="([^"]+)">([^<]+)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedtitle in matches:
        scrapedplot = ""
        scrapedthumbnail = ""
        if (DEBUG): logger.info("title=[" + scrapedtitle + "], url=[" + scrapedurl + "]")
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot))

    return itemlist


def search(item, texto):
    logger.info("[itastreaming.py] " + item.url + " search " + texto)
    item.url = "%s?s=%s" % (sito, texto)
    try:
        return peliculas_search(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def findvid(item):
    logger.info("[itastreaming.py] findvideos")

    itemlist = []

    # Descarga la página
    data = anti_cloudflare(item.url)

    patron = r"DownloadName\s*=\s*'([^']+)';\s*DownloadURL\s*=\s*'([^']+)'"
    matches = re.compile(patron, re.DOTALL).findall(data)

    if len(matches) > 0:
        for scrapedtitle, scrapedurl in matches:
            scrapedurl = binascii.unhexlify(scrapedurl)

            itemlist.append(
                Item(channel=__channel__,
                     action="play",
                     server='googlevideo',
                     title=item.title + " [COLOR azure]" + scrapedtitle + "[/COLOR]",
                     url=scrapedurl,
                     fulltitle=item.title,
                     show=item.title,
                     folder=False))
    else:
        patron = r'<div id="usual1" class="usual1">\s*<p><iframe\s*(?:width="[^"]+")?\s*(?:height="[^"]+")?\s*src="([^"]+)"'
        matches1 = re.compile(patron, re.DOTALL).findall(data)
        for url in matches1:
            data = scrapertools.cache_page(url)
            patron = r'; eval\(unescape\("(.*?)",(\[".*?;"\]),(\[".*?\])\)\);'
            matches2 = re.compile(patron, re.DOTALL).findall(data)
            for par1, par2, par3 in matches2:
                par2 = eval(par2, {'__builtins__': None}, {})
                par3 = eval(par3, {'__builtins__': None}, {})
                data = unescape(par1, par2, par3)
                data = scrapertools.find_single_match(data, r'tvar Data = \\"([^\\]+)\\";')
                data = binascii.unhexlify(data).replace(r'\/', '/')
                patron = ',"width":"([^"]+)","url":"([^"]+)"'
                matches3 = re.compile(patron, re.DOTALL).findall(data)
                for scrapedtitle, scrapedurl in matches3:
                    itemlist.append(
                        Item(channel=__channel__,
                             action="play",
                             server='googlevideo',
                             title=item.title + " [COLOR azure]" + scrapedtitle + "[/COLOR]",
                             url=scrapedurl,
                             fulltitle=item.title,
                             show=item.title,
                             folder=False))

    return itemlist


def unescape(par1, par2, par3):
    var1 = par1
    for ii in xrange(0, len(par2)):
        var1 = re.sub(par2[ii], par3[ii], var1)

    var1 = re.sub("%26", "&", var1)
    var1 = re.sub("%3B", ";", var1)
    return var1.replace('<!--?--><?', '<!--?-->')


def anti_cloudflare(url):
    # global headers

    try:
        resp_headers = scrapertools.get_headers_from_response(url, headers=headers)
        resp_headers = {v[0]: v[1] for v in resp_headers}
    except urllib2.HTTPError, e:
        resp_headers = e.headers

    if 'refresh' in resp_headers:
        time.sleep(int(resp_headers['refresh'][:1]))

        # dict_headers = {v[0]: v[1] for v in headers}
        # dict_headers['cookie'] = resp_headers['set-cookie'].split(';')[0]

        # resp_headers = scrapertools.get_headers_from_response(sito + resp_headers['refresh'][7:], headers=[[k, v] for k, v in dict_headers.iteritems()])
        scrapertools.get_headers_from_response(sito + resp_headers['refresh'][7:], headers=headers)
        # resp_headers = {v[0]: v[1] for v in resp_headers}

        # dict_headers['cookie'] = dict_headers['cookie'] + resp_headers['set-cookie'].split(';')[0]
        # headers = [[k, v] for k, v in dict_headers.iteritems()]

    return scrapertools.cache_page(url, headers=headers)
