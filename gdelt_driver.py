"""
Driver
Run scraper  (GDELT_SCRAPE Dictionary Returned)
(loop through dict)
puts into (article) table
    URL
    domain_name
    publication_date
    tile
puts into gdelt
    timestamp
uses HTML
    runs summary
    - Uses SQL Insert Function on summary
    runs Hyperlinks
    - Uses SQL Insert Function on Hyperlinks
    runs Dates
    - Uses SQL Insert Function on Dates
    runs Entities
    - Uses SQL Insert Function on Entities
    runs Sentiment
    - Uses SQL Insert Function on Sentiment
"""

import DatabaseAPI
import metadata_engine
import gdelt_scraper

# for testing
import datetime


class GDELTDriver:

    def __init__(self, connection_name='change_me', db_name='change_me', config_inp={}):
        """
        @Name:
            __init__
        @Description:
            initiates gdelt_driver class
        @Params:
        @Return:
            None
        """
        # ToDo - config import
        if config_inp is None:
            config = {
                        # database management system
                        "driver_name": "mysql+pymysql",

                        # connection string for SQL instance
                        "connection_name": connection_name,

                        # name of database on SQL instance
                        "db_name": db_name,

                        # login info for database
                        "db_user": "root",
                        "db_password": "",
                    }
        else:
            config = config_inp

        config["query_string"] = dict(
            {"unix_socket": f"/cloudsql/{config['connection_name']}"})

        self.db = DatabaseAPI.DatabaseAPI(config)
        self.db.connect_to_database()

        self.scraped_output = {}

        # required for GCP cloud functions, the HTTP request that triggers the function
        # self.request_json = request.get_json()

    def new_scrape(self, date_block=None):
        """
        @Name:
            new_scrape
        @Description:
            sets gdelt scraper with most current 15 minute scrape
        @Params:
            optional data block will be able to select a specific 15-minute block.
            not complete yet
        @Return:

        """
        scraper = gdelt_scraper.GDELTSCRAPER()
        if date_block is None:
            scraper.open_file(scraper.get_recent_filename())
        else:
            scraper.open_file(date_block)
        self.scraped_output = scraper.scrape_csv()

    def run_block(self):
        """
        @Name:
            run_block
        @Description:
            scrapes a 15 minute GDELT segment and puts its metadata into Google Cloud
        @Params:
        @Return:
            None
        """

        engine = metadata_engine.MetadataEngine()

        for key, value in self.scraped_output.items():

            if len(value['contents']) == 0:
                html = None
            else:
                html = value['contents']

            if html is not None:
                # logging.warning("INSERTING ARTICLE")
                self.db.sql_insert_article(value)  # < change
                # logging.warning("INSERTING GDELT")
                self.db.sql_insert_gdelt(value)  # < change

                engine.prime_engine(html)

                if html != '':

                    self.db.sql_insert_hyperlink(engine.get_hyperlinks())
                    self.db.sql_insert_summary(engine.summarize_text())
                    self.db.sql_insert_date(engine.get_dates())
                    self.db.sql_insert_sentence_and_entity(engine.get_entities_and_sentiments())

                    # self.db.sql_insert_entity(engine.get_entities())
                    # self.db.sql_insert_sentence(engine.get_sentiment())


if __name__ == "__main__":
    driver = GDELTDriver()
    driver.new_scrape()
    driver.run_block()

    pass
