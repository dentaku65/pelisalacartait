# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para vidto.me
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import re

from core import scrapertools
from core import logger
from lib.jsbeautifier.unpackers import packer

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("pelisalacarta.servers.vidtome url="+page_url)

    # Lo pide una vez
    headers = [['User-Agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14']]
    data = scrapertools.cache_page( page_url , headers=headers )
    #logger.info("data="+data)
    
    logger.info("pelisalacarta.servers.vidtome opcion 2")
    op = scrapertools.get_match(data,'<input type="hidden" name="op" value="([^"]+)"')
    logger.info("pelisalacarta.servers.vidtome op="+op)
    usr_login = ""
    id = scrapertools.get_match(data,'<input type="hidden" name="id" value="([^"]+)"')
    logger.info("pelisalacarta.servers.vidtome id="+id)
    fname = scrapertools.get_match(data,'<input type="hidden" name="fname" value="([^"]+)"')
    logger.info("pelisalacarta.servers.vidtome fname="+fname)
    referer = scrapertools.get_match(data,'<input type="hidden" name="referer" value="([^"]*)"')
    logger.info("pelisalacarta.servers.vidtome referer="+referer)
    hashstring = scrapertools.get_match(data,'<input type="hidden" name="hash" value="([^"]*)"')
    logger.info("pelisalacarta.servers.vidtome hashstring="+hashstring)
    imhuman = scrapertools.get_match(data,'<input type="submit".*?name="imhuman" value="([^"]+)"').replace(" ","+")
    logger.info("pelisalacarta.servers.vidtome imhuman="+imhuman)
        
    import time
    time.sleep(10)

    # Lo pide una segunda vez, como si hubieras hecho click en el banner
    #op=download1&usr_login=&id=z3nnqbspjyne&fname=Coriolanus_DVDrip_Castellano_by_ARKONADA.avi&referer=&hash=nmnt74bh4dihf4zzkxfmw3ztykyfxb24&imhuman=Continue+to+Video
    #op=download1&usr_login=&id=h6gjvhiuqfsq&fname=GENES1S.avi&referer=&hash=taee4nbdgbuwuxfguju3t6nq2gkdzs6k&imhuman=Proceed+to+video
    post = "op="+op+"&usr_login="+usr_login+"&id="+id+"&fname="+fname+"&referer="+referer+"&hash="+hashstring+"&imhuman="+imhuman
    headers.append(["Referer",page_url])
    body = scrapertools.cache_page( page_url , post=post, headers=headers )
    logger.info("body="+body)

    data = scrapertools.find_single_match(body,"<script type='text/javascript'>(eval\(function\(p,a,c,k,e,d.*?)</script>")
    logger.info("data="+data)
    data = packer.unpack(data)
    logger.info("data="+data)

    # Extrae la URL
    #{label:"240p",file:"http://188.240.220.186/drjhpzy4lqqwws4phv3twywfxej5nwmi4nhxlriivuopt2pul3o4bkge5hxa/video.mp4"}
    video_urls = []
    media_urls = re.findall(r'\{label:"([^"]+)",file:"([^"]+)"\}', data)
    video_urls = []
    for label,media_url in media_urls:
        video_urls.append( [ scrapertools.get_filename_from_url(media_url)[-4:]+" ("+label+") [vidto.me]",media_url])

    #<a id="lnk_download" href="http://188.240.220.186/drjhpzy4lqqwws4phv3twywfxej5nwmi4nhxlriivuopt2pul3oyvkoe5hxa/INT3NS4HDTS-L4T.mkv">
    media_url = scrapertools.find_single_match(body,'<a id="lnk_download" href="([^"]+)"')
    if media_url!="":
        video_urls.append( [ scrapertools.get_filename_from_url(media_url)[-4:]+" (ORIGINAL) [vidto.me]",media_url])

    for video_url in video_urls:
        logger.info("pelisalacarta.servers.vidtome %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):

    # Añade manualmente algunos erróneos para evitarlos
    encontrados = set()
    devuelve = []

    #http://vidto.me/z3nnqbspjyne
    patronvideos  = 'vidto.me/([a-z0-9A-Z]+)'
    logger.info("pelisalacarta.servers.vidtome find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[vidto.me]"
        url = "http://vidto.me/"+match+".html"
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'vidtome' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

    #http://vidto.me/embed-z3nnqbspjyne
    patronvideos  = 'vidto.me/embed-([a-z0-9A-Z]+)'
    logger.info("pelisalacarta.servers.vidtome find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[vidto.me]"
        url = "http://vidto.me/"+match+".html"
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'vidtome' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

    return devuelve

def test():

    video_urls = get_video_url("http://vidto.me/h6gjvhiuqfsq.html")

    return len(video_urls)>0
