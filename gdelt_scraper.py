from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen
from urllib.parse import urlparse
from bs4 import BeautifulSoup

import proxied_scraper

#only used for error checking
from collections import Counter
from datetime import datetime

class GDELTSCRAPER:
    '''
        @Name: __init__
        @Description:
            initiates GDELTSCRAPER
        @Params
            NONE
        @Return
            None
    '''
    def __init__(self, proxy_list_inp: list = ["http://20.81.62.32:3128"]):
        self.csv_dict = {}
        self.news_dict = {}
        self.proxy_list = proxy_list_inp
        self.gdelt_scraper = proxied_scraper.ProxiedScraper(self.proxy_list)

    '''
        @Name: open_file
        @Description: 
            Gets the file from the internet then decodes the tsv into a dictionary
        @Params
            date_time: str -> a string that is the date and time that they want the file 
            for example Febuaray 19 2015 00:00:00 would be 20150219000000
        @Return 
            None
    '''
    def open_file(self, date_time: str):
        # This is the zipped file from the GDELT database
        zipped_file = urlopen("http://data.gdeltproject.org/gdeltv2/" + date_time + ".export.CSV.zip")

        # These are all 61 of the column_headers from the csv files because the names are not in the file given
        column_headers = ["GlobalEventID", "YearMonthDate", "YearMonth", "Year", "FractionDate",
                          "Actor1Code", "Actor1Name", "Actor1CountryCode", "Actor1KnownGroupCode", "Actor1EthnicCode",
                          "Actor1Religion1Code", "Actor1Religion2Code", "Actor1Type1Code", "Actor1Type2Code",
                          "Actor1Type3Code", "Actor2Code", "Actor2Name", "Actor2CountryCode", "Actor2KnownGroupCode",
                          "Actor2EthnicCode", "Actor2Religion1Code", "Actor2Religion2Code", "Actor2Type1Code",
                          "Actor2Type2Code", "Actor2Type3Code", "IsRootEvent", "EventCode", "EventBaseCode",
                          "EventRootCode", "QuadClass", "GoldsteinScale", "NumMentions", "NumSoruces", "NumArticles",
                          "AvgTone", "Actor1Geo_Type", "Actor1Geo_Fullname", "Actor1Geo_CountryCode",
                          "Actor1Geo_ADM1Code", "Actor1Geo_ADM2Code", "Actor1Geo_Lat", "Actor1Geo_Long",
                          "Actor1Geo_FeatureID", "Actor2Geo_Type", "Actor2Geo_Fullname", "Actor2Geo_CountryCode",
                          "Actor2Geo_ADM1Code", "Actor2Geo_ADM2Code", "Actor2Geo_Lat", "Actor2Geo_Long",
                          "Actor2Geo_FeatureID", "ActionGeo_Type", "ActionGeo_Fullname", "ActionGeo_CountryCode",
                          "ActionGeo_ADM1Code", "ActionGeo_ADM2Code", "ActionGeo_Lat", "ActionGeo_Long",
                          "ActionGeo_FeatureID", "DATEADDED", "SOURCEURL"]

        # Empty dict that is filled later
        article_dict = {}

        # Code to unzip the file
        zipfile = ZipFile(BytesIO(zipped_file.read()))

        for line in zipfile.open(date_time + ".export.CSV").readlines():
            count = 0
            lines = line.decode('utf-8').split("\t")
            article_dict[lines[0]] = {}

            for col in lines:
                article_dict[lines[0]][column_headers[count]] = col
                count += 1

        self.csv_dict = article_dict

        # print(self.csv_dict)
        # print(article_dict["410424334"])
        # print(zipped_file)
        # print("\nARTICLE DICT")
        # print(article_dict)

    '''
    @Name: scrape_csv
    @Description: 
        runs the csv urls through the proxied scraper and returns HTML
        {{source:url,date:datetime,source:dw,bbc,etc., title:title of the article,contents:contents of the article}}
    @Params
        None
    @Return
        None
    '''
    def scrape_csv(self) -> dict:
    
        # a list of all urls in .csv
        key_url = {}
        urls = []
        output = {}

        for gdelt_key, source_url in self.csv_dict.items():
            key_url.update({gdelt_key: str(self.csv_dict[gdelt_key]['SOURCEURL'].replace("\n", ''))})
            urls.append(str(self.csv_dict[gdelt_key]['SOURCEURL'].replace("\n", '')))

        self.gdelt_scraper.clear_urls()
        self.gdelt_scraper.clear_results()
        self.gdelt_scraper.scrape_list(urls)

        scraper_output = self.gdelt_scraper.results
        for item in scraper_output:
            print(len(item))

        print("\n --------- scrape done. Setting up output: ")

        for index, (gdelt_key, source_url) in enumerate(key_url.items()):

            html = scraper_output[index]
            # print(f"<html>{len(html)}")

            title = ''
            if html != '':
                soup = BeautifulSoup(html, 'html.parser')
                if soup.find('title') is not None:
                    soup.find('title').get_text()
            """
            # test code (lets used know what's being put into dict)
            print(f"scrape number: {index+1}-------\n"
                  f"GDELT KEY: ->{gdelt_key}<-: \n"
                  f"'source_url': {source_url},\n"
                  f"'date': {self.csv_dict[gdelt_key]['YearMonthDate']},\n"
                  f"'source': {urlparse(source_url).netloc},\n"
                  f"'title': {title},\n"
                  f"'contents': <len(html)> = {len(html)}\n"
                  f"------------------------------------------------------------------")
            """
            output.update({gdelt_key: {'source_url': source_url,
                                       'date': self.csv_dict[gdelt_key]['YearMonthDate'],
                                       'source': urlparse(source_url).netloc,
                                       'title': title,
                                       'contents': html,
                                       }
                           }
                          )

        return output


        # scrapes all urls and returns a dict with the results
        # Scrape dict: { <url: str> : <html: str> }
        # # self.scraper.initialize_url_list(urls)
        # self.scraper.scrape_url()
        # return self.scraper.results

        # test code (prints results)
        # print("DICT{URL:HTML: str} " + f"holding scrape results: \n"
        #                                f"{self.scraper.results}\n")

    '''
    @Name: scrape_csv
    @Description: 
        uses scraped HTML to build news_dict
        {{source:url,date:datetime,source:dw,bbc,etc., title:title of the article,contents:contents of the article}}
    @Params
        None
    @Return
        None
    '''
    def build_news_dict(self):
        html_dict = self.scrape_csv()
        output_dict = {}
        domain = ''

        # TODO: complete this loop
        for key, value in html_dict.items():
            domain = urlparse(key).netloc
            date = ''
            source = key
            title = ''
            contents = value

    '''
    @Name: get_recent_filename
    @Description: 
        returns a string that provides the most recent GDELT filename at a 15 minute increment
    @Params
        None
    @Return
        string of most recent 15 minute time increment, formatted for GDELT
    '''
    def get_recent_filename(self) -> str:
        now = datetime.now()
        return now.replace(second=0, microsecond=0, minute=(now.minute // 15 * 15), hour=now.hour).strftime(
            "%Y%m%d%H%M00")

if __name__ == "__main__":

    start = datetime.now()
    gdelt = GDELTSCRAPER()

    gdelt.open_file(gdelt.get_recent_filename())
    scraped_output = gdelt.scrape_csv()

    finish = datetime.now()
    time_dif = finish - start

    count_bad = 0
    count_good = 0
    duplicate_url_counter = []

    for key, value in scraped_output.items():
        print(f"{key}\n"
              f"source_url: {value['source_url']} \n"
              f"date:{value['date']} \n"
              f"source:{value['source']} \n"
              f"title:{value['title']} \n"
              f"html: {len(value['contents'])} \n")
        duplicate_url_counter.append(value['source_url'])

        if len(value['contents']) == 0:
            count_bad += 1
        else:
            count_good += 1

    duplicates = Counter(duplicate_url_counter)

    num_dup = 0
    not_dup = 0

    for key, value in duplicates.items():
        if value != 1:
            num_dup += 1
            print(f"{value} : {key} ")
        elif value == 1:
            not_dup += 1

    print(f"Time to scrape: {time_dif.total_seconds()} seconds")
    print(f"Total Number of GDELT.CSV Items: {len(scraped_output)}")
    print(f"Total count unique URLs: {num_dup + not_dup}")

    print(f"Keys with no HTML: {count_bad}\n"
          f"Keys with HTML: {count_good}")

    print(f"COUNT OF DUPLICATES: {num_dup}")
    print((f"COUNT OF SINGLES: {not_dup}"))
