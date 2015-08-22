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

    data = scrapertools.cache_page(page_url)

    exist = scrapertools.find_single_match(data,'<div class="center">Videomega.tv - ([^<]+)</div>')
    if not exist:
        return False,"No existe o ha sido borrado de videomega"

    return True,""

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("pelisalacarta.videomega get_video_url(page_url='%s')" % page_url)

    video_urls = []

    id = scrapertools.get_match(page_url,"ref\=([A-Za-z0-9]+)")
    page_url = "http://videomega.tv/?ref="+id
    new_url = "http://videomega.tv/(?:cdn|view).php?ref="+id+"&width=(?:800|700)&height=(?:400|430)"
    print "### page_url: %s" % (page_url)
    print "### new_url: %s" % (new_url)

    # Descarga la página
    headers = [
        ['Host', 'videomega.tv'],
        ['User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0'],
        ['Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'],
        ['Accept-Language', 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3'],
        ['Accept-Encoding', 'gzip, deflate'],
        ['Referer', page_url],
        ['Connection', 'keep-alive']
    ]
    data = scrapertools.cache_page(new_url , headers = headers)

    
    try:
        ## Debug
        l = []
        patron = 'document.write\(unescape\("([^"]+)"\)\)'
        matches = re.compile(patron,re.DOTALL).findall(data)
        print "######### matches:\n%s" % (matches)
        for loc in matches:
            l.append(urllib.unquote(loc))
        print "######### l1:\n%s" % (l[0])
        print "######### l2:\n%s" % (l[1])
        print "######### l3:\n%s" % (l[2])

        ## url válida en l3
        ## l3 quote
        #<script type="text/javascript">document.write(unescape("%3c%73%63%72%69%70%74%20%74%79%70%65%3d%22%74%65%78%74%2f%6a%61%76%61%73%63%72%69%70%74%22%3e%69%66%28%59%53%4a%63%4e%46%51%52%62%62%4f%29%7b%6a%77%70%6c%61%79%65%72%28%29%2e%6f%6e%52%65%61%64%79%28%66%75%6e%63%74%69%6f%6e%28%29%7b%6a%77%70%6c%61%79%65%72%28%29%2e%6c%6f%61%64%28%5b%7b%69%6d%61%67%65%3a%22%68%74%74%70%3a%2f%2f%73%74%31%32%39%2e%75%31%2e%76%69%64%65%6f%6d%65%67%61%2e%74%76%2f%76%69%64%65%6f%73%2f%73%63%72%65%65%6e%73%68%6f%74%73%2f%34%65%38%34%61%66%33%61%64%32%62%30%37%32%30%65%30%38%37%61%33%34%39%63%64%32%34%37%35%35%61%36%2e%6a%70%67%22%20%2c%20%66%69%6c%65%3a%22%68%74%74%70%3a%2f%2f%73%74%31%32%39%2e%75%31%2e%76%69%64%65%6f%6d%65%67%61%2e%74%76%2f%76%2f%34%65%38%34%61%66%33%61%64%32%62%30%37%32%30%65%30%38%37%61%33%34%39%63%64%32%34%37%35%35%61%36%2e%6d%70%34%3f%73%74%3d%61%79%77%66%77%58%44%31%33%73%56%6a%4b%37%49%59%73%64%75%6f%35%51%26%68%61%73%68%3d%38%31%52%65%32%48%55%4e%70%74%61%78%5a%39%66%64%57%34%74%6a%70%51%22%20%20%20%20%7d%5d%29%3b%7d%29%3b%7d%3c%2f%73%63%72%69%70%74%3e"));</script>
        ## l3 unquote
        #<script type="text/javascript">if(YSJcNFQRbbO){jwplayer().onReady(function(){jwplayer().load([{image:"http://st129.u1.videomega.tv/videos/screenshots/4e84af3ad2b0720e087a349cd24755a6.jpg" , file:"http://st129.u1.videomega.tv/v/4e84af3ad2b0720e087a349cd24755a6.mp4?st=aywfwXD13sVjK7IYsduo5Q&hash=81Re2HUNptaxZ9fdW4tjpQ"    }]);});}</script>

        ## l3 quote
        location = scrapertools.get_match(data,'<script type="text/javascript">document.write\(unescape\("([^"]+)"\)\)')
        logger.info("pelisalacarta.videomega location="+location)

        location = urllib.unquote(location)
        logger.info("pelisalacarta.videomega location="+location)

        ## l3 unquote
        location = scrapertools.get_match(location,'file\:"([^"]+)"')
        logger.info("pelisalacarta.videomega location="+location)

        video_urls.append( [ scrapertools.get_filename_from_url(location)[-4:]+" [videomega]" , location ] )

    except:
        media_url = scrapertools.get_match(data,'<source src="([^"]+)" type="video/mp4"/>')
        media_url+= "|Cookie=__cfduid=d99f17efc7261084a8b2fe4dee1773a5c1395122824594"
        video_urls = [ [ "mp4 [videomega]" , media_url ] ]
    else:
        video_urls = [ ["en videomega? Va a ser que no. Videomega está vacilón", False ] ]

    for video_url in video_urls:
        logger.info("pelisalacarta.videomega %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    # http://videomega.net/auoxxtvyoy
    patronvideos  = 'videomega.tv/iframe.php\?ref\=([A-Za-z0-9]+)'
    logger.info("pelisalacarta.videomega find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[videomega]"
        #url = "http://videomega.tv/iframe.php?ref="+match
        url = "http://videomega.tv/?ref="+match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'videomega' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

    # http://videomega.net/auoxxtvyoy
    patronvideos  = 'videomega.tv/(?:cdn|view).php\?ref\=([A-Za-z0-9]+)'
    logger.info("pelisalacarta.videomega find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[videomega]"
        #url = "http://videomega.tv/iframe.php?ref="+match
        url = "http://videomega.tv/?ref="+match
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
        #url = "http://videomega.tv/iframe.php?ref="+match
        url = "http://videomega.tv/?ref="+match
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
