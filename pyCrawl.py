#pyCrawl by iernie

import re
import urllib2
import urlparse
import sys
import getopt
import os
import pickle

verbose = False
auto_save = False

class pyCrawl():

    def __init__(self, seed):
        self.link_regex = re.compile('<a.*href=[\'|"](.*?)[\'|"].*>')
        self.queue = set([seed])
        self.found = set([])
        self.crawled = set([])

    def save_state(self):
        save_file = open('crawl.state', 'w')
        pickle.dump(self, save_file)
        save_file.close()

    def run(self):
        while len(self.queue) > 0:
            try:
                url = self.queue.pop()
                url_parsed = urlparse.urlparse(url)
                response = urllib2.urlopen(url)
                response_content = response.read()
            except KeyError:
                print "URL queue empty"
                sys.exit()
            except urllib2.URLError:
                print "Invalid URL given:", url
                sys.exit()
            except ValueError:
                print "URL malformed"
                sys.exit()

            if verbose:
                print "Processing", url
                print len(self.queue), "links left in the queue"

            if auto_save:
                self.save_state()

            self.crawled.add(url)
            links = self.link_regex.findall(response_content)
            for link in links:

                if link == "#":
                    continue

                if link.startswith('#'):
                    link = url_parsed[0] + "://" + url_parsed[1] + "/" + link
                elif link.startswith('/'):
                    link = url_parsed[0] + "://" + url_parsed[1] + link

                if link.startswith('http'):

                    if link in self.found:
                        continue

                    if link not in self.crawled:
                        self.queue.add(link)

                    self.found.add(link)
        print "Job done"


if __name__ == '__main__':
    seed = None

    try:
        opts, args = getopt.getopt(sys.argv[1:], '', ['seed=', 'verbose', 'auto-save', 'fresh'])
    except getopt.GetoptError:
        print "Available options: --seed, --verbose, --auto-save, --fresh"
        sys.exit()

    for o, a in opts:
        if o in ('--seed'):
            seed = str(a)

        if o in ('--verbose'):
            verbose = True

        if o in ('--auto-save'):
            auto_save = True

        if o in ('--fresh'):
            print "Deleting old state..."
            os.remove("crawl.state")

    if os.path.isfile("crawl.state"):
        print "Recovering last state..."
        save_file = open('crawl.state', 'r')
        crawler = pickle.load(save_file)
        save_file.close()
    else:
        if not seed:
            print "You need to enter a seed with --seed"
            sys.exit()
        elif not seed.startswith('http'):
            print "Seed needs to start with 'http://'"
            sys.exit()
        crawler = pyCrawl(seed)

    try:
        print "Running crawler..."
        crawler.run()
    except KeyboardInterrupt:
        crawler.save_state()
        print "Crawler shut down"