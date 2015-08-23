# -*- coding: iso-8859-1 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para italiafilm
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os
import sys
import re, htmlentitydefs

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "italiafilm"
__category__ = "F,S,A"
__type__ = "generic"
__title__ = "Italia-Film.co"
__language__ = "IT"

DEBUG = True #config.get_setting("debug")
EVIDENCE = "   "

def isGeneric():
    return True

def mainlist(item):
    logger.info("[italiafilm.py] mainlist")
    itemlist = []
    itemlist.append( Item(channel=__channel__, title="[COLOR azure]Film - Novita'[/COLOR]" , action="peliculas", url="http://www.italia-film.co/category/film-del-2015-streaming/",thumbnail="http://dc584.4shared.com/img/XImgcB94/s7/13feaf0b538/saquinho_de_pipoca_01"))
    itemlist.append( Item(channel=__channel__, title="[COLOR azure]Serie TV[/COLOR]" , action="peliculas", url="http://www.italia-film.co/category/telefilm/", thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/New%20TV%20Shows.png"))
    itemlist.append( Item(channel=__channel__, title="[COLOR azure]Anime e Cartoon[/COLOR]" , action="peliculas", url="http://www.italia-film.co/category/anime-e-cartoon/", thumbnail="http://orig09.deviantart.net/df5a/f/2014/169/2/a/fist_of_the_north_star_folder_icon_by_minacsky_saya-d7mq8c8.png"))
    itemlist.append( Item(channel=__channel__, title="[COLOR azure]Contenuti per Genere[/COLOR]" , action="categorias", url="http://www.italia-film.co/", thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/All%20Movies%20by%20Genre.png"))
    itemlist.append( Item(channel=__channel__, title="[COLOR yellow]Cerca...[/COLOR]" , action="search", thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search"))
    return itemlist

def categorias(item):
    logger.info("[italiafilm.py] categorias")
    itemlist = []
    logger.error("io")

    data = scrapertools.cache_page(item.url)
    data = scrapertools.find_single_match(data,'<a href=".">Categorie</a>(.*?)</div>')

    patron = '<li class="[^"]+"><a href="([^"]+)">([^<]+)</a></li>'
    patron = '<li[^>]+><a href="([^"]+)">([^<]+)</a></li>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    
    for url,title in matches:
        scrapedtitle = title
        scrapedurl = urlparse.urljoin(item.url,url)
        scrapedplot = ""
        scrapedthumbnail = ""
        if DEBUG: logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action='peliculas', title="[COLOR azure]" + scrapedtitle + "[/COLOR]", url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True) )

    return itemlist

def search(item,texto):
    logger.info("[italiafilm.py] search "+texto)
    itemlist = []
    texto = texto.replace(" ","%20")
    item.url = "http://www.italia-film.co/?s="+texto

    try:
        return peliculas(item)
    # Se captura la excepcion, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []


def peliculas(item):
    logger.info("[italiafilm.py] peliculas")
    itemlist = []

    data = scrapertools.cachePage(item.url)
    patron = '<article(.*?)</article>'
    matches = re.compile(patron,re.DOTALL).findall(data)

    for match in matches:

        title = scrapertools.find_single_match(match,'<h3[^<]+<a href="[^"]+"[^<]+>([^<]+)</a>')
        title = scrapertools.htmlclean(title).strip()
        url = scrapertools.find_single_match(match,'<h3[^<]+<a href="([^"]+)"')
        html = scrapertools.cache_page(url)
        start = html.find("<p><br/>")
        end = html.find("</h2>", start)
        plot = html[start:end]
        plot = re.sub(r'<[^>]*>', '', plot)
        plot = scrapertools.decodeHtmlentities(plot)
        thumbnail = scrapertools.find_single_match(match,'data-echo="([^"]+)"')

        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")

        itemlist.append( Item(channel=__channel__, action='findvideos', title="[COLOR azure]" + title + "[/COLOR]", url=url , thumbnail=thumbnail , fanart=thumbnail, plot=plot , viewmode="movie_with_plot", folder=True) )

    # Siguiente
    try:
        pagina_siguiente = scrapertools.get_match(data,'<a class="next page-numbers" href="([^"]+)"')
        itemlist.append( Item(channel=__channel__, action="peliculas", title="[COLOR orange]Successivo >> [/COLOR]" , url=pagina_siguiente , thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png", folder=True) )
    except:
        pass

    return itemlist

def test():
    from servers import servertools
    # mainlist
    mainlist_items = mainlist(Item())
    # Da por bueno el canal si alguno de los vídeos de "Novedades" devuelve mirrors
    peliculas_items = peliculas(mainlist_items[0])
    bien = False
    for pelicula_item in peliculas_items:
        mirrors = servertools.find_video_items( item=pelicula_item )
        if len(mirrors)>0:
            bien = True
            break

    return bien
