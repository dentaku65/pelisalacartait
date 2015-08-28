# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para videomega
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config

def test_video_exists( page_url ):
    logger.info("pelisalacarta.videomega test_video_exists(page_url='%s')" % page_url)
    
    return True,""

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("pelisalacarta.videomega get_video_url(page_url='%s')" % page_url)

    #data = scrapertools.cache_page(page_url)
    data = scrapertools.downloadpage(page_url,follow_redirects=False)
    video_urls = []

    location = scrapertools.find_single_match(data,'<source src="([^"]+)"')
    logger.info("pelisalacarta.videomega location="+location)

    #http://st100.u1.videomega.tv/v/bf38b3577874d7ce424c1c87d6d1b8d9.mp4?st=kuiAz1XJ7XFzOCnaleGVxA&start=0
    #http://st100.u1.videomega.tv/v/bf38b3577874d7ce424c1c87d6d1b8d9.mp4?st=kuiAz1XJ7XFzOCnaleGVxA
    video_urls.append( [ scrapertools.get_filename_from_url(location)[-4:]+" [videomega]" , location ] )

    for video_url in video_urls:
        logger.info("pelisalacarta.videomega %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    # http://videomega.net/auoxxtvyoy
    patronvideos  = 'videomega.tv/([A-Za-z0-9]+)'
    logger.info("pelisalacarta.videomega find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[videomega]"
        url = "http://videomega.tv/view.php?ref="+match+"&width=100%&height=400"
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'videomega' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

    # http://videomega.net/auoxxtvyoy
    patronvideos  = 'videomega.tv/cdn.php\?ref\=([A-Za-z0-9]+)'
    logger.info("pelisalacarta.videomega find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[videomega]"
        url = "http://videomega.tv/view.php?ref="+match+"&width=100%&height=400"
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'videomega' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)
            
    # http://videomega.tv/?ref=NcYTGcGNUY
    patronvideos  = 'videomega.tv/\?ref\=([A-Za-z0-9]+)'
    logger.info("pelisalacarta.videomega find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[videomega]"
        url = "http://videomega.tv/view.php?ref="+match+"&width=100%&height=400"
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'videomega' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)
            
    return devuelve

def test():
    video_urls = get_video_url("http://videomega.tv/iframe.php?ref=LWfaTEDONS")

    return len(video_urls)>0