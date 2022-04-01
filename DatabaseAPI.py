import sqlalchemy
import logging
import time
from random import randint


class DatabaseAPI:
    def __init__(self, config):
        # todo update this docstring to PEP8
        '''
        @Name:
            __init__
        @Description:
            initiates ProxiedScraper class
        @Params:
            config:dict: stores configuration data needed to connect to a GCP MySQL database
        @Return:
            None
        '''
        # config to GCP MySQL database
        self.config = config

        # used to fill out foreign key column in all of the junction tables
        self.last_article_id = None

    def connect_to_database(self):
        # todo update this docstring to PEP8
        '''
        @Name:
            connect_to_database
        @Description:
            Doesn't directly connect, but creates a pool of connections 
            connects to a GCP MySQL database
        @Params:
            None
        @Return:
            None
        '''

        # connect to GCP MySQL database
        self.db_connection = sqlalchemy.create_engine(
            sqlalchemy.engine.url.URL(
                drivername=self.config["driver_name"],
                database=self.config["db_name"],
                username=self.config["db_user"],
                password=self.config["db_password"],
                query=self.config["query_string"],
            ),
            pool_size=5,
            max_overflow=2,
            pool_timeout=30,
            pool_recycle=1800
        )

    def disconnect_from_database(self):
        # todo update this docstring to PEP8
        '''
        @Name:
            disconnect_from_database
        @Description:
            disconnects from the GCP MySQL database
        @Params:
            None
        @Return:
            None
        '''

        # close every connection to database
        self.db_connection.dispose()

    def sql_insert_article(self, data):
        # todo update this docstring to PEP8
        '''
        @Name:
            sql_insert_article
        @Description:
            inserts data into article table
        @Params:
            data:Dict[str, str]: data to insert in to database 
        @Return:
            None
        '''

        assert (type(data) == dict)

        # setup SQL command to insert data into article table
        command = sqlalchemy.text(
            "INSERT INTO article (url, domain_name, publication_date, title) VALUES (:url, :domain_name, :publication_date, :title)")

        # execute SQL command with a connection
        with self.db_connection.connect() as connection:
            result = connection.execute(command, data)

            # save article_id of last article for inserting other related data
            self.last_article_id = result.lastrowid

    def sql_insert_gdelt(self, data):
        # todo update this docstring to PEP8
        '''
        @Name:
            sql_insert_gdelt
        @Description:
            inserts data into gdelt table
        @Params:
            data:Dict[str, str]: data to insert in to database 
        @Return:
            None
        '''

        assert (type(data) == dict)

        # setup SQL command to insert data into gdelt table

        command = sqlalchemy.text("INSERT INTO gdelt (article_id, gdelt_id, timestamp) VALUES (:article_id, :gdelt_id, :timestamp)")
        # attach article table's as foreign key
        data['article_id'] = self.last_article_id


        # execute SQL command with a connection
        with self.db_connection.connect() as connection:
            connection.execute(command, data)

    def sql_insert_hyperlink(self, data):
        # todo update this docstring to PEP8
        '''
        @Name:
            sql_insert_hyperlink
        @Description:
            inserts data into hyperlink table
        @Params:
            data:List[Dict[str, Union[str, int]]]: data to insert in to database 
        @Return:
            None
        '''

        assert (type(data) == list)
        if len(data) > 0:
            assert (type(data[0]) == dict)
        # data is empty
        else:
            return

        # SQL command to insert data into hyperlink table
        hyperlink_command = sqlalchemy.text(
            "INSERT INTO hyperlink (hyperlink) VALUES (:hyperlink)")

        # SQL command to insert data into article_hyperlink table
        article_hyperlink_command = sqlalchemy.text("INSERT INTO article_hyperlink (article_id, hyperlink_id, frequency_in_article) VALUES (:article_id, :hyperlink_id, :frequency_in_article)")


        for hyperlink_data in data:
            # attach article table's as foreign key
            hyperlink_data['article_id'] = self.last_article_id

            with self.db_connection.connect() as connection:
                # insert into hyperlink table
                result = connection.execute(hyperlink_command, hyperlink_data)

                # save hyperlink table's id for use as foreign key
                hyperlink_data['hyperlink_id'] = result.lastrowid

                # insert into article_hyperlink table
                connection.execute(article_hyperlink_command, hyperlink_data)

    def sql_insert_summary(self, data):
        # todo update this docstring to PEP8
        '''
        @Name:
            sql_insert_summary
        @Description:
            inserts data into summary table
        @Params:
            data:Dict[str, str]: data to insert in to database 
        @Return:
            None
        '''

        assert (type(data) == dict)

        # SQL command to insert data into summary table
        command = sqlalchemy.text("INSERT INTO summary (article_id, summary) VALUES (:article_id, :summary)")


        # attach article table's as foreign key
        data['article_id'] = self.last_article_id

        # execute SQL command with a connection
        with self.db_connection.connect() as connection:
            connection.execute(command, data)

    def sql_insert_date(self, data):
        # todo update this docstring to PEP8
        '''
        @Name:
            sql_insert_date
        @Description:
            inserts data into date table
        @Params:
            data:List[Dict[str, Union[str, int]]]: data to insert in to database 
        @Return:
            None
        '''

        assert (type(data) == list)
        if len(data) > 0:
            assert (type(data[0]) == dict)
        # data is empty
        else:
            return

        # SQL command to insert data into date table
        date_command = sqlalchemy.text("INSERT INTO date (date) VALUES (:date)")
       
        # SQL command to insert data into article_date table
        article_date_command = sqlalchemy.text("INSERT INTO article_date (article_id, date_id, frequency_in_article) VALUES (:article_id, :date_id, :frequency_in_article)")


        # SQL command to insert data into article_date table
        article_date_command = sqlalchemy.text("INSERT INTO article_date (article_id, date_id, frequency_in_article) VALUES (:article_id, :date_id, :frequency_in_article)")

        # perform query
        for date_data in data:
            # attach article table's as foreign key
            date_data['article_id'] = self.last_article_id

            with self.db_connection.connect() as connection:
                # insert into date table
                result = connection.execute(date_command, date_data)

                date_data['date_id'] = result.lastrowid

                # insert into article_date table
                connection.execute(article_date_command, date_data)

    def sql_insert_sentence_and_entity(self, data):
        # todo update this docstring to PEP8
        '''
        @Name:
            sql_insert_sentence_and_entity
        @Description:
            inserts sentence and entity data into entity table
        @Params:
            data:List[Dict[str, Union[str, int, float, Dict[str, Union[str, int]]]]]: data to insert in to database 
        @Return:
            None
        '''

        assert (type(data) == list)
        if len(data) > 0:
            assert (type(data[0]) == dict)
        # data is empty
        else:
            return

        # SQL command to insert data into sentence table
        sentence_command = sqlalchemy.text("INSERT INTO sentence (article_id, sentence, sentiment_pos, sentiment_neg, sentiment_neu, sentiment_compound) VALUES (:article_id, :sentence, :sentiment_pos, :sentiment_neg, :sentiment_neu, :sentiment_compound)")

        # SQL command to insert data into entity table
        entity_command = sqlalchemy.text("INSERT INTO entity (entity, ne_type) VALUES (:entity, :ne_type)")

        # SQL command to insert data int into sentence_entity table
        sentence_entity_command = sqlalchemy.text("INSERT INTO sentence_entity (entity_id, sentence_id) VALUES (:entity_id, :sentence_id)")


        # SQL command to insert data int into article_entity table
        article_entity_command = sqlalchemy.text("INSERT INTO article_entity (article_id, entity_id, frequency_in_article) VALUES (:article_id, :entity_id, :frequency_in_article)")

        # perform commands
        for sentence_entity_data in data:
            with self.db_connection.connect() as connection:
              
                # attach article table's as foreign key
                sentence_entity_data['article_id'] = self.last_article_id
                # insert into sentence table
                result = connection.execute(sentence_command, sentence_entity_data)
                
                # save sentence table's id for use as foreign key
                sentence_id = result.lastrowid


                # insert into entity table
                for entity_data in sentence_entity_data['entities']:
                    # attach sentence table's for foreign key
                    entity_data['sentence_id'] = sentence_id
                    # attach article table's id for foreign key
                    entity_data['article_id'] = self.last_article_id

                    # insert into entity table
                    result = connection.execute(entity_command, entity_data)
                    
                    # save entity table's id for use as foreign key
                    entity_data['entity_id'] = result.lastrowid

                    # insert into sentence_entity table
                    connection.execute(sentence_entity_command, entity_data)

                    # insert into article_entity table
                    connection.execute(article_entity_command, entity_data)

    def sql_delete_old(self, time_limit=120):
        # todo update this docstring to PEP8
        # todo test this code
        '''
        @Name:
            sql_delete_old
        @Description:
            deletes old entries in tables based on time_limit
        @Params:
            time_limit: hours limit
        @Return:
            None
        '''
        curr_time = int(time.time()) - (time_limit * 60 * 60)

        command = sqlalchemy.text(
            f'SELECT gdelt.article_id FROM gdelt WHERE gdelt.gdelt_id < {curr_time}'
        )

        article_ids = []
        with self.db_connection.connect() as connection:
            # insert into sentence table
            article_ids = connection.execute(command).fetchall()

        tables = ['article', 'gdelt', 'summary', 'entity', 'hyperlink', 'date', 'sentence',
                  'sentence_entity', 'article_entity', 'article_date', 'article_hyperlink']

        for article_id in article_ids:
            for table in tables:
                delete_cmd = sqlalchemy.text(
                    f'DELETE FROM {table} WHERE {table}.article_id = {article_id}')

                with self.db_connection.connect() as connection:
                    connection.execute(delete_cmd)


def main(request):
    # required for GCP cloud functions, the HTTP request that triggers the function
    request_json = request.get_json()

    config = {
        # database management system
        "driver_name": "mysql+pymysql",

        # connection string for SQL instance
        "connection_name":CHANGE ME, 

        # name of database on SQL instance
        "db_name":CHANGE ME,


        # login info for database
        "db_user": "root",
        "db_password": "",
    }
    config["query_string"] = dict(
        {"unix_socket": f"/cloudsql/{config['connection_name']}"})

    db = DatabaseAPI(config)
    db.connect_to_database()

    # dummy data that would be parsed from an article
    dummy_data = {
        'article': {
            'url': "TEST URL",
            "domain_name": "TEST DOMAIN NAME",
            "publication_date": time.strftime('%Y-%m-%d %H:%M:%S'),
            "title": "TEST TITLE"
        },
        'gdelt': {
            'gdelt_id': int(time.time()),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        },
        'hyperlink': [
            {
                'hyperlink': f"HYPERLINK {time.strftime('%Y-%m-%d %H:%M:%S')} 0",
                'frequency_in_article': 1
            },
            {
                'hyperlink': f"HYPERLINK {time.strftime('%Y-%m-%d %H:%M:%S')} 1",
                'frequency_in_article': 2
            },
        ],
        'summary': {
            'summary':'SUMMARY'
        },
        'date': [
            {
                'date': f"DATE {time.strftime('%Y-%m-%d %H:%M:%S')} 0",
                'frequency_in_article': 1
            },
            {
                'date': f"DATE {time.strftime('%Y-%m-%d %H:%M:%S')} 1",
                'frequency_in_article': 2
            },
        ],
        'sentence_entity': [
            {

                'sentence':f"SENTENCE {time.strftime('%Y-%m-%d %H:%M:%S')} 0",
                'sentiment_pos':0.234,
                'sentiment_neg':0.66,
                'sentiment_neu':0.106,
                'sentiment_compound':-0.4404,
                'entities': [
                    {
                        'entity': f"ENTITY NAME {time.strftime('%Y-%m-%d  %H:%M:%S')} 0",
                        'ne_type': f"NNP",
                        'frequency_in_article': 1
                    },
                    {
                        'entity': f"ENTITY NAME {time.strftime('%Y-%m-%d  %H:%M:%S')} 1",
                        'ne_type': f"VBD",
                        'frequency_in_article': 2
                    }
                ]
            },
            {
                'sentence':f"SENTENCE {time.strftime('%Y-%m-%d %H:%M:%S')} 1",
                'sentiment_pos':0.234,
                'sentiment_neg':0.66,
                'sentiment_neu':0.106,
                'sentiment_compound':-0.4404,
                'entities': [
                    {
                        'entity': f"ENTITY NAME {time.strftime('%Y-%m-%d  %H:%M:%S')} 0",
                        'ne_type': f"NNP",
                        'frequency_in_article': 1
                    },
                    {
                        'entity': f"ENTITY NAME {time.strftime('%Y-%m-%d  %H:%M:%S')} 1",
                        'ne_type': f"VBD",
                        'frequency_in_article': 2
                    }
                ]
            },
        ],
    }

    logging.warning("INSERTING ARTICLE")
    db.sql_insert_article(dummy_data['article'])

    logging.warning("INSERTING GDELT")
    db.sql_insert_gdelt(dummy_data['gdelt'])

    logging.warning("INSERTING HYPERLINK")
    db.sql_insert_hyperlink(dummy_data['hyperlink'])

    db.sql_insert_summary(dummy_data['summary'])

    logging.warning("INSERTING DATE")
    db.sql_insert_date(dummy_data['date'])

    logging.warning("INSERTING SENTENCE and entity")
    db.sql_insert_sentence_and_entity(dummy_data['sentence_entity'])

    db.disconnect_from_database()

    return 'ok'
