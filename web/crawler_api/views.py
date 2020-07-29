from django.shortcuts import render
from django.http import HttpResponse

import scrapy
from scrapy.crawler import CrawlerProcess
from ecproduct.ecproduct.spiders.vvic import VvicSpider
import os, sys

# Create your views here.
def index(request):
    return HttpResponse("Hello, world.")

def vvic(request):
    """
    start crawler named 'vvic'
    """
    crawler = 'vvic'
    process = CrawlerProcess()
    process.crawl(VvicSpider)
    process.start()
    return HttpResponse("start crawler %s successfully" % crawler)

