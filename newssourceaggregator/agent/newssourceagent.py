from newssourceaggregator.newssender import NewsSender
from newssourceaggregator.rssFeedPlug import RssFeedPlug
from newssourceaggregator.rssparser import RequiredDataStruct
from systemtools.basics import getDictSubElement
from newssourceaggregator.rssparser import RssParser
from time import sleep
import threading
import time
import datetime
import json

CFG_FILE_PATH="../parserconfig.json"

class NewsSourceAgent:

    def __init__(self, source, parser=None, sender=None):
        self.source = source
        self.fullData = []
        self.parser = parser
        self.sender = sender
        if sender is None:
            self.sender = NewsSender()

    def gatherUrls(self):
        cache = set()
        while 42:
            unparsedData = self.source.getPunctualFeed(self.source.source)
            klist = self.parser.getKeywordList()
            for section in unparsedData.entries:
                self.fullData.append(RequiredDataStruct())
                timeID = time.time()
                date = datetime.datetime.fromtimestamp(timeID)
                self.fullData[-1].crawling_timestamp = date
                self.fullData[-1].agent = self.source.type
                for key in klist:
                    if key in section:
                        self.fullData[-1].setItem(key, getDictSubElement(section, klist[key]))

            indexlist = []
            for struct in self.fullData:
                if struct.datadict['link'] in cache:
                    indexlist.append(self.fullData.index(struct))
            indexlist.reverse()
            for index in indexlist:
                del self.fullData[index]
            indexlist.clear()

            for struct in self.fullData:
                if struct.datadict is not None:
                    self.sender.send(json.dumps(struct.datadict))
                cache.add(struct.datadict['link'])

            sleep(self.source.waitTimer)


if __name__ == '__main__':
    print("Hello there !")
    nsa = NewsSourceAgent(source=RssFeedPlug("https://www.judgehype.com/nouvelles.xml"), parser=RssParser(CFG_FILE_PATH))
#    nsa.gatherUrls()
    nnsa = NewsSourceAgent(source=RssFeedPlug("http://www.lefigaro.fr/rss/figaro_actualites.xml", timer=90), parser=RssParser(CFG_FILE_PATH))
#    nnsa.gatherUrls()
    threading.Thread(target=nsa.gatherUrls).start()
    threading.Thread(target=nnsa.gatherUrls).start()

    while 1:
        continue
