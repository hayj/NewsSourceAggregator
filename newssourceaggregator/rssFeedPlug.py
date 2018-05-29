import feedparser
import time
import json


class RssFeedPlug:
    waitTimer = 60
    source = None
    type = 'RSS-agent | Source : '

    def __init__(self, source, timer=60):
        if timer >= 5:
            self.waitTimer = timer
        if source:
            self.source = source
        else:
            raise RuntimeError("No source provided for RSS feed")
        self.type += source

    def getConstantFeed(self):
        while 1:
            data = feedparser.parse(self.source)
            time.sleep(self.waitTimer)
            print(data)

    @staticmethod
    def getPunctualFeed(rss):
        return feedparser.parse(rss)
