"""
CLASS DEFINITION:
# all functionality fits within the ProxiedScraper class
CLASS: ProxiedScraper
    __init__ -  (self, url_list: list = [], proxy_pool: list = []) - initializes scraper
    def initialize_url_list - initializes URLs, allows user to input a list of urls or a .txt file with urls in it
        .txt should have 1 url per line with return used as delimiter
    
    def start_custom_proxy - starts the proxy : depends on __class__ProxyServer
    # internal class
    # this is the Scrapy object
    # it controls the scrape
    
    # Helper functions are used to make code easy to incorporate
    def append_proxy_list - appends a single proxy address string to ProxiedScraper.proxy_pool[]
    def set_proxy_list - takes a list[] of proxies
    def import_proxies - takes a .txt with a list of proxies (1 proxy per line)
    def clear_proxies - clears ProxiedScraper.proxy_pool[]
    def append_url_list - adds a single url string to ProxiedScraper.url_list[]
    def set_url_list - takes a list[] of URLs : depends on append_url_list()
    def import_url_list - takes a .txt of URLs (1 URL per line) : depends on set_url_list()
    def clear_urls - clears ProxiedScraper.url_list[]
    
    # these functions initiate Scrapy.
    def scrape : depends on __class__ScrapySpider (optional: start_custom_proxy)
    def scrape_list : depends on clear_urls(), add_url_list(), scrape()
    def scrape_from_file : depends on clear_urls(), import_url_list(), scrape()
    def results - returns ProxiedScraper.html_ouput Dict{URL:HTML: str}
    def clear_results - clears ProxiedScraper.html_ouput Dict{URL:HTML: str}
    def validate_proxy_list - validates proxies from input list before returning the good ones.
    def validate_proxy_pool - validates the current object's pool : depends on validate_proxy_list()
    
      CLASS: ScrapySpider
        # subclass
        __init__ - (self, url_list: list, proxy_list: list)
        def start_requests - iterates through list of urls using provided proxies
        def parse - turns output into Dict{URL:HTML: str} and puts Dict in ProxiedScraper.html_ouput
    
INSTRUCTIONS/EXAMPLE of USE:
    EXAMPLE:
    SCRAPE = ProxiedScraper(LIST[]_OF_PROXIES, LIST[]_OF_URLs)   # scrapes from provided list of URLs
    (ALTERNATE)SCRAPE = ProxiedScraper(LIST[]_OF_PROXIES, .TXT_WITH_URLs)   # scrapes from .txt file with URLs
    (OPTIONAL) SCRAPE.validate_proxy_pool() # validates provided proxies
    SCRAPE.scrape() # runs web scrape
    output = SCRAPE.results # ProxiedScraper.results will provide a Dict{URL:HTML: str} object with scrape results
initialize ProxiedScraper( POOL_OF_PROXIES, LIST_OF_URLs or .TXT_FILENAME_WITH_URLs )
DOES NOT HAVE:
currently provides an output of all successful requests.
to know if a request is not successful you have to compare list of outputs to list of input URLS.
there is functionality that would make outputting list of unsuccessful requests easy
"""


class ProxiedScraper:
    """
    @Name: ProxiedScraper
    @Description:
        class uses proxies to grab HTML body from provided websites
        can provide HTML body in a dictionary: { URL : HTML } using ProxiedScraper.results
    @Params
    url_list: list or str: initializes empty if no input. can use a list or a .txt filename with URLs
    proxy_pool: list: initializes empty of no input
    """
    # libraries for proxy server
    import socketserver
    import http.server
    import urllib.request
    import threading

    # libraries for scrapy based scraper
    import scrapy
    import random
    from scrapy.crawler import CrawlerProcess

    # libraries used for validation`
    # (currently not part of class)
    import urllib3
    from urllib3 import ProxyManager, make_headers

    def __init__(self, proxy_pool_input: list = [], url_input: list or str = []) -> None:
        """
        @Name: __init__
        @Description: initiates ProxiedScraper class
        @Params
        url_list: list or str: initializes empty if no input. can use a list or a .txt filename with URLs
        proxy_pool: list: initializes empty of no input
        """
        self.proxy_server = None
        # FIXME self_proxied_scraper.proxy = self_proxied_scraper.ProxyServer
        self.scraper = self.ScrapySpider
        self.html_output = []
        self.url_list = []
        self.initialize_url_list(url_input)
        self.proxy_pool = proxy_pool_input

    def initialize_url_list(self, url_input: list or str):
        """
        @Name: initialize_url_list
        @Description: initiates ProxiedScraper class. Allows user to provide a List[] or .txt file of urls
        dependencies: set_url_list, import_url_list
        @Params
        url_input: list or str: calls different initialization functions depending on input type
        """
        # depending on if url_input is list or str calls different initialization functions
        if type(url_input) is list:
            self.add_url_list(url_input)
        elif type(url_input) is str:
            self.import_url_list(url_input)

    def append_proxy(self, proxy_address: str) -> None:
        """
        @Name: append_proxy
        @Description:
            adds a proxy to the proxy_pool
        @Params
        proxy: str: a string containing a proxy address
        """
        self.proxy_pool.append(proxy_address)
        print(f"new proxy added: {proxy_address}")  # indicates that a URL ahs been added

    def set_proxy_list(self, proxy_list: list) -> None:
        """
        @Name: set_proxy_list
        @Description:
            sets the proxy list to the list provided
            dependencies: append_proxy
        @Params
        proxy_list: list: a list of proxy addresses
        """
        for item in proxy_list:
            self.append_proxy(item)

    def import_proxies(self, proxy_filename: str) -> None:
        """
        @Name: import_proxy_list
        @Description:
            sets provided list as the next set of URL's to be scraped.
            dependencies: set_proxy_list
        @Params
        proxy_filename: str: filename for a .txt with a list of proxy addresses (1 proxy per line)
        """
        try:
            # opens file and splits it into a list
            f = open(proxy_filename, "r")
            self.set_proxy_list(f.read().split())
            print("successful import")
        except IOError:
            print(f"Error opening {proxy_filename}")

    def clear_proxies(self):
        """
        @Name: clear_proxies
        @Description: clears all proxies from list
        @Params
        None
        """
        self.proxy_pool.clear()

    def append_url(self, url: str) -> None:
        """
        @Name: append_url
        @Description:
            adds a url to the url_list
        @Params
        url: str: a string containing a url
        """
        self.url_list.append(url)
        # print(f"new URL added: {url}")  # indicates that a URL ahs been added

    def add_url_list(self, url_list: list) -> None:
        """
        @Name: set_url_list
        @Description:
            sets provided list as the next set of URL's to be scraped
            depends on append_url()
        @Params
        url_list: list: a list of URLs
        """
        count = 0
        for item in url_list:
            count += 1
            self.append_url(item)
            print(f"url{count}: {item} < added")

    def import_url_list(self, url_filename: str) -> None:
        """
        @Name: import_url_list
        @Description:
            Opens a file and sets url_list to contents. (1 URL per line)
            depends on set_url_list to set URLs
        @Params
        url_filename: str: .txt filename for a text file holding URL's. 1 URL per line.
        """

        try:
            # opens file and splits it into a list
            f = open(url_filename, "r")
            self.add_url_list(f.read().split())
            print("successful import")
        except IOError:
            print(f"Error opening {url_filename}")

    def clear_urls(self):
        """
        @Name: clear_urls
        @Description: clears all URL's from list
        @Params
        None
        """
        self.url_list.clear()

    def scrape(self, use_custom_proxy: bool = False) -> None:
        """
        @Name: scrape
        @Description: performs the scrape. If no proxy is provided uses custom local proxy
        @Params
        use_custom_proxy: Bool = False: default is off, as custom proxy doesn't currently work.
        """
        # if no proxy was provided uses custom local proxy
        # this line provides all dependencies on custom proxy and can be removed
        # if use_custom_proxy is True:
        #     self.start_custom_proxy()

        # creates a Scrapy scraper object and crawls provided URLs
        scraper = self.ScrapySpider
        process = self.CrawlerProcess()
        process.crawl(scraper, self.url_list, self.proxy_pool)
        process.start()  # the script will be blocked here until all crawling jobs are finished

        # sets the html_output to the list value within the scraper object
        self.html_output = scraper.html_output
        process.stop()

    def scrape_list(self, url_list: list) -> None:
        """
        @Name: scrape_list
        @Description: scrapes websites in provided list
        @Params
        url_list: list: a list of urls
        """
        # immediately initiates scrape from provided list
        self.clear_urls()
        self.add_url_list(url_list)
        self.scrape()

    def scrape_url(self, url: str) -> dict:
        """
        @Name: scrape_list
        @Description: scrapes websites in provided list
        @Params
        url_list: list: a list of urls
        """
        # immediately initiates scrape from provided list
        self.clear_urls()
        self.clear_results()
        self.add_url_list([url])
        self.scrape()
        return self.results

    def scrape_from_file(self, url_filename: str) -> None:
        """
        @Name: scrape_from_file
        @Description: scrapes websites in provided .txt file
        @Params
        url_filename: str: filename for a .txt with urls in it. one url per line
        """
        # imports list from file than immediately initiates scrape
        self.clear_urls()
        self.import_url_list(url_filename)
        self.scrape()

    @property
    def results(self) -> list:
        """
        @Name: results
        @Description:
            returns a dict object containing all {URL:HTML} pairs found during scrape
            if called before scrape, html_output will be empty
        @Params
        None
        """
        # returns the html_output Dictionary object from ProxiedScraper class
        return self.html_output

    def clear_results(self):
        """
        @Name: clear_results
        @Description: clears the html_output object
        @Params
        None
        """
        self.html_output = []

    def validate_proxy_list(self, proxy_list: list, test_url: str = "http://example.com") -> list:
        """
        @Name: validate_proxy_list
        @Description:
            attempts to access the web with each proxy provided. Splits them into good and bad proxies
            returns the good proxies, prints lists of the ones that did and didn't pass
            There is probably a faster way of doing this
        @Params
        proxy_list: a list of proxies
        test_url: str: defaults to example.com
        """
        # lists for sorting proxies
        final_list = []
        bad_proxies = []
        # provides a count of proxies checked
        checked = 0

        print("Begin Validation")

        # check loop iterates through provided list
        for proxy in proxy_list:

            checked += 1

            try:
                # requests a web connection using proxy
                default_headers = self.make_headers(proxy_basic_auth='myusername:mypassword')
                http = self.ProxyManager(proxy, proxy_headers=default_headers)
                http.request('GET', test_url)
                print(f"{checked}.) {proxy} is valid")
                final_list.append(proxy)

            # if it fails test, sort proxy and notify user
            except(IOError,
                   self.urllib3.exceptions.ProxySchemeUnknown,
                   self.urllib3.exceptions.MaxRetryError,
                   self.urllib3.exceptions.NewConnectionError,
                   TimeoutError):
                print(f"{checked}.) Connection error! (Check proxy)")
                bad_proxies.append(proxy)

        # prints lists
        print(f"bad proxies: {bad_proxies}\n"
              f"good proxies: {final_list}")

        # returns only the good proxies
        return final_list

        # optional tuple would return the list of bad proxies as well
        # complicates function, so might not be proper
        # return final_list, bad_proxies

    def validate_proxy_pool(self):
        """
        @Name: validate_proxy_pool
        @Description:
            validates the current proxy pool, and removes all invalid proxies
        @Params
        None
        """
        # sets proxy_pool object = list of good proxies
        self.proxy_pool = self.validate_proxy_list(self.proxy_pool)

    class ScrapySpider(scrapy.Spider):
        """
        @Name: ScrapySpider
        @Description: Completes the scrape process
        @Params
        url_list: list[str] : a list of URLs
        proxy_list: list[str] : a list of proxy addresses
        """
        # name of the spider
        name = 'ScrapySpider'

        custom_settings = {
            # enable setting for scrapy's spider to use proxies
            'HTTPPROXY_ENABLED': True,
        }

        # list containing strs of  HTML
        html_output = []

        def __init__(self, url_list: list, proxy_list: list) -> None:
            """
            @Name: __init__
            @Description:
                initializes scraper values.
            @Params
            url_list: list: a list of URLs
            proxy_list: a list of proxies
            """
            # list of URLs where the spider will being to crawl from
            self.start_urls = url_list

            # list of proxies to use the scraper should use
            self.proxy_pool = proxy_list

            self.url_proxy_pairs = {}

            self.scrape_url = ''

        # generates a response object for each url and call parse on each response object
        def start_requests(self) -> None:
            """
            @Name: start_requests
            @Description:
                begins scrape. iterates through URL list and calls proxy
            @Params
            None
            """
            for index, url in enumerate(self.start_urls):
                self.html_output.append(f"")
                self.scrape_url = url
                # randomly choose a proxy from the pool of proxies
                proxy = ProxiedScraper.random.choice(self.proxy_pool)
                # print(f"for URL:{url} proxy is {proxy}")
                self.url_proxy_pairs.update({url: proxy})
                # make request to url through the selected proxy
                yield ProxiedScraper.scrapy.Request(url=url, callback=self.parse, meta={'proxy': proxy},
                                                    cb_kwargs=dict(url_index=index))

        def parse(self, response, url_index) -> None:
            """
            @Name: parse
            @Description:
                parses scrape into a dict object for export. {URL:HTML}
            @Params
            response: a Scrapy response
            """
            # separate website's raw html from response object
            raw_html = response.text
            # append website's raw
            self.html_output[url_index] += raw_html

            # output code for testing
            # print(f'\nTHIS IS THE RAW HTML:\n'
            #      f'{raw_html}\n'
            #      f'---end of HTML---\n\n')


if __name__ == "__main__":

    # urls to be scraped for their html
    urls = [
        "http://giowaoij.com",
        "http://heraldnet.com/article/20150218/NEWS01/150219125",
        "http://bot.whatismyipaddress.com",
    ]
    # use proxy I found online
    proxy_pool = ["http://20.81.62.32:3128"]

    # scrapes from provided list of URLs
    # SCRAPE = ProxiedScraper(proxy_pool, urls)
    # scrapes from .txt file instead
    SCRAPE = ProxiedScraper(proxy_pool, urls)
    SCRAPE.scrape()
    scrape = SCRAPE.results
    print("RESULTS")
    num = 1
    for i in scrape:
        print(f"SCRAPE {num}-------------> \n{i}")
        num += 1

# validates multiple IP addresses and scrapes multiple pages
'''
  proxy_list = ["http://23.251.138.105:8080", "43.41", "http://23.25.138.10:8080",  "http://20.76.164.205:3128", 
                "http://71.13.82.30:80", "http://3.34.13.214:8080", "http://158.177.253.24:80", 
                "http://34.138.225.120:8888", "http://20.81.62.32:3128"]
    good_proxies = validate_proxy_list(proxy_list)
    urls = ['http://bot.whatismyipaddress.com', 'https://www.scrapethissite.com/', "http://example.com",
            "https://webscraper.io/test-sites/e-commerce/allinone", "https://www.google.com/",
            "https://webscraper.io/test-sites/tables"]
    # use proxy I found online
    SCRAPE = ProxiedScraper(urls, good_proxies)
    SCRAPE.scrape()
    print(SCRAPE.html_output)
'''
