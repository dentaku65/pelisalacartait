# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Server per youwatch
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config
from core import unpackerjs3

def test_video_exists( page_url ):
    logger.info("youwatch test_video_exists(page_url='%s')" % page_url)
    return True,""

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("youwatch get_video_url(page_url='%s')" % page_url)
    if not "embed" in page_url:
      #page_url = page_url.replace("http://youwatch.org/","http://youwatch.org/embed-") + ".html"
      ## - fix ------------------------------------------------------
      page_url = page_url.replace("http://youwatch.org/","http://youwatch.org/embed-") + "-640x360.html"
      ## ------------------------------------------------------------

    data = scrapertools.cache_page(page_url)

    ## - fix ------------------------------------------------------
    patron_new_url = '<body[^<]+<iframe.*?src="([^"]+)"'
    new_url = scrapertools.find_single_match( data, patron_new_url )

    while new_url != "":
        host = scrapertools.get_match( new_url, '//([^/]+)/' )
        headers = [
            ['User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0'],
            ['Accept-Encoding','gzip, deflate'],
            ['Host',host],
            ['Referer',new_url]
        ]
        data = scrapertools.cache_page( new_url, headers=headers )
        new_url = scrapertools.find_single_match( data, patron_new_url )
    ## -----------------------------------------------------------

    data = scrapertools.find_single_match(data,"<span id='flvplayer'></span>\n<script type='text/javascript'>(.*?)\n;</script>")
    data = unpackerjs3.unpackjs(data,0)
    url = scrapertools.get_match(data, 'file:"([^"]+)"')
    video_urls = []
    video_urls.append([scrapertools.get_filename_from_url(url)[-4:]+" [youwatch]",url])

    for video_url in video_urls:
        logger.info("[youwatch.py] %s - %s" % (video_url[0],video_url[1]))
       

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []


    patronvideos  = 'http://youwatch.org/([a-z0-9]+)'
    logger.info("youwatch find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[youwatch]"
        url = "http://youwatch.org/"+match
        if url not in encontrados and match!="embed":
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'youwatch' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)
           

    patronvideos  = 'http://youwatch.org/embed-([a-z0-9]+)'
    logger.info("youwatch find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[youwatch]"
        url = "http://youwatch.org/"+match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'youwatch' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)
           
    return devuelve

def test():
    video_urls = get_video_url("http://youwatch.org/crbt4sja1jvo")

    return len(video_urls)>0
