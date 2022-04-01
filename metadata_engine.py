import numpy
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.tag import pos_tag
import spacy
from spacy import displacy
from collections import Counter
from spacy.lang.en.examples import sentences
import en_core_web_sm
from transformers import pipeline
from nltk.tokenize import WhitespaceTokenizer
from nltk.tokenize import TreebankWordTokenizer as twt
import string

# !pip install vaderSentiment
# pip install torch

nltk.download('punkt')
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


class MetadataEngine:
    """
    @Name: metadata_engine
    @Description: This class extracts metada from an HTML object
        to use: First run the prime_engine function, than
    @Params:
    None
    """

    def __init__(self, html=None):
        self.sentiment = None
        nltk.download("popular")
        nltk.download('vader_lexicon')
        self.html = ''
        self.text = ''
        if html:
            self.prime_engine(html)
        self.date_list = []

    def prime_engine(self, html):
        """
        @Name: prime_engine
        @Description: This function sets the self.htms and self.text objects
        HTML: HTML from a website
        """
        self.html = html
        self.text = self.get_text()  # get_text not currently implemented

    def get_text(self):
        """
        @Name: get_text
        @Description:
        """
        # currently empty, please replace

        soup = BeautifulSoup(self.html, features="html.parser")

        # kill all script and style elements
        for script in soup(["script", "style"]):
            script.extract()  # rip it out

        # get text
        self.text = soup.get_text()
        return self.text

    def check_ent_day(self, entity):
        """
        @Name: checkEntDAY
        @Description: This function will state whether the text of a named entity includes the name of a weekday
        @Params
        entity: a string from the text that was recognized as a named entity by SpaCy
            # helper function to detect if any days are in an entity text
        """
        words = entity.split()
        for word in words:
            if word == 'Mon' or word == 'Mon.' or word == 'Monday':
                return True
            if (
                    word == "Tu" or word == "Tu." or word == "Tue" or word == "Tue." or word == 'Tues' or word == 'Tues.' or word == 'Tuesday'):
                return True
            if word == 'Wed' or word == 'Wed.' or word == 'Wednesday':
                return True
            if (
                    word == 'Th' or word == 'Th.' or word == 'Thu' or word == 'Thu.' or word == 'Thur' or word == 'Thur.' or word == 'Thurs' or word == 'Thurs' or word == 'Thursday'):
                return True
            if word == 'Fri' or word == 'Fri.' or word == 'Friday':
                return True
            if word == 'Sat' or word == 'Sat.' or word == 'Saturday':
                return True
            if word == 'Sun' or word == 'Sun.' or word == 'Sunday':
                return True
        return False

    def check_ent_num(self, string_number) -> bool:
        """
        @Name: checkEntNUM
        @Description: This function will state whether a named entity is a date
        @Params
        stringnumber: a string from the text that was recognized as a named entity by SpaCy
                # helper function: takes in a string, returns a bool
        """
        # this function checks if a number is a date
        # get shape of the string, and check if formatting is consistent with common formats of dates
        length = len(string_number)
        for i in range(length):
            if string_number[i].isdigit():
                character = string_number[i]
                string_number = string_number.replace(character, 'x')
        if string_number == 'xx-xx-xxxx':
            return True
        if string_number == 'x-x-xxxx':
            return True
        if string_number == 'xx-x-xxxx':
            return True
        if string_number == 'x-xx-xxxx':
            return True
        if string_number == 'xx-xxxx':
            return True
        if string_number == 'x-xxxx':
            return True
        if string_number == 'x-xx':
            return True
        if string_number == 'xx-xx-xx':
            return True
        if string_number == 'x-xx-xx':
            return True
        if string_number == 'xx-x-xx':
            return True
        if string_number == 'x-x-xx':
            return True
        return False

    def check_token_num(self, token):
        """
        @Name: checkTokenNUM
        @Description: This function states whether a token is a date
        @Params
        token: a string from the text
            # helper function: takes in a string, returns a bool
        """
        # check if shape of token is consistent with the common formats of dates
        if token.shape_ == 'dd/dd/dddd':
            return True
        if token.shape_ == 'd/d/dddd':
            return True
        if token.shape_ == 'dd/d/dddd':
            return True
        if token.shape_ == 'd/dd/dddd':
            return True
        if token.shape_ == 'd/d/dd':
            return True
        if token.shape_ == 'dd/dd/dd':
            return True
        if token.shape_ == 'd/dd/dd':
            return True
        if token.shape_ == 'dd/d/dd':
            return True
        if token.shape_ == 'd/dddd':
            return True
        if token.shape_ == 'dd/dddd':
            return True
        if token.shape_ == 'd/dd':
            return True
        if token.shape_ == 'dd/dd':
            return True
        if token.shape_ == 'd/d':
            return True
        # add more if reading non-American articles
        return False

    def get_dates(self):
        """
        @Name: getDates
        @Description: 
        This function will return set the "date_list" member variable to a list of dates that are inside the text
        @Params
        text:String: body of text you want to process
        """

        # the publishing date of the article 
        
        # this line can be taken outside the function to save time
        nlp = en_core_web_sm.load()  
        # processes the text
        doc = nlp(self.text)  
        
        # creates list that will hold items of class Date, which holds the date text AND the 
        # position of that text in the string 
        date_pos_list = []  

        for ent in doc.ents:
            if (
                    # if the entity is a DATE and is not just a time-related word like "months" or "days", add to list
                    ent.label_ == 'DATE'):  
                if ent.text[0].isdigit() or ent.text[0].isupper():
                    date_pos_list.append(ent.text)
            # if entity is any sort of number, then
            elif ent.label_ == 'NUM' or ent.label_ == 'CARDINAL':
                # use helper function to check if number is a date
                if self.check_ent_num(ent.text):  
                    date_pos_list.append(ent.text)
        for token in doc:
            # if (token.pos_ == 'NUM' or token.pos_ == 'X'): 
            # --TAKEN OUT AS SPACY DOES NOT ALWAYS CLASSIFY TOKENS WITH SHAPE XX/XX/XXXX THE SAME WAY, 
            # CAN PUT BACK IN IF NEEDED

            # uses helper function to check if number is a date
            if self.check_token_num(token):  
                date_pos_list.append(token)
                
        # create a list of the texts of the dates (no position element)
        date_list = []  
        for item in date_pos_list:
            date_list.append(item)
        self.date_list = date_list
        return self.date_list

    def summarize_text(self, percentage=.2, article_text=''):
        """
        @Name: summarizeText
        @Description: This will make a summary of the inputted text based around the length (amount of words you want)
        @Params
        text:String: Inputted text
        percentage:int:Not required, range[0,1], default is 20% decimal of desired number of words of original article
        @Return
        A summary of the inputted text and percentage
        """
        # task specific SummarizationPipeLine
        # model is default model

        if article_text == '':
            article_text = self.text

        summarizer = pipeline(
            'summarization', model="sshleifer/distilbart-cnn-12-6")

        summary = ''

        # number of possible words in text (may count malformed characters)
        num_orig_words = len(article_text.split())

        # number of words in summary
        num_new_words = round(num_orig_words * percentage)
        # print(num_new_words)

        if num_new_words < 20:
            num_new_words = 20
        elif num_new_words > 80:
            num_new_words = 80

        # "returns a summary of the inputted text that is a percentage of the text"
        # 5 appears to work fairly well for producing range
        add_on = round(num_new_words / 5)

        if num_orig_words > 300:
            text_array = article_text.split()
            length = 300

            text_array = [' '.join(text_array[i:i + length]) for i in range(0, len(text_array), length)]

            print(f"TEXT ARRAY: ---- {text_array}")
            for item in text_array:
                print(f"item: ---------\n {item}")
                num_orig_words = len(item.split())
                num_new_words = round(num_orig_words * percentage)

                if num_new_words < 20:
                    num_new_words = 20
                elif num_new_words > 80:
                    num_new_words = 80

                add_on = round(num_new_words / 5)

                if num_new_words + add_on < len(item.split()):
                    print("in loop ------------")
                    small_summary = summarizer(item, max_length=(
                            num_new_words + add_on), min_length=(num_new_words - add_on), do_sample=False)
                    ss_text = small_summary[0]['summary_text']
                    print(f"ss_text: {ss_text}")
                    summary = summary + "\n" + ss_text + "..."

            if len(summary.split()) > 300:
                summary = self.summarize_text(.2, summary)

            return summary

        else:

            # takes inputted text and summarize it with the inputted length
            summary = summarizer(article_text, max_length=(
                    num_new_words + add_on), min_length=(num_new_words - add_on), do_sample=False)
            return summary[0]['summary_text']

    def get_hyperlinks(self):
        """
        @Name: get_hyperlinks
        @Description: This gets all of the hyperlinks from a given article
        @Params
        HTML: The html from beatiful soup of the given url
        @Return
        A list of every hyperlink in the html
        """
        hyperlink = {}  # hyperlinks will be output as a list
        soup = BeautifulSoup(html)
        links = soup.find_all('a')

        for tag in links:  # finds all <a> tags within html source
            url = tag.get('href', ' ')
            if "/" in url:
                hyperlink[tag.text.strip()] = url
        return hyperlink


    def get_entities_and_sentiments(self):
        entity_and_sentiment_data = []
        
        # create sentiment analyzer object
        sid_obj = SentimentIntensityAnalyzer()

        # tokenize text into sentences
        for sentence in nltk.sent_tokenize(self.text):
            sentence_data = {}
            
            sentence_data['sentence'] = sentence

            # compute sentiment scores for each sentence
            sentiment_dict = sid_obj.polarity_scores(sentence)
            for score in sentiment_dict:
                sentence_data[f'sentiment_{score}'] = sentiment_dict[score]

            # get entities for each sentence
            sentence_data['entities'] = self.get_entities(sentence)

            entity_and_sentiment_data.append(sentence_data)

        return entity_and_sentiment_data

    def get_entities(self, text):
        """
        @Name: get_entities
        @Description: Function will take in a string input and output a dictionary of key of tokens
                    and value of an dictionary: name entity type | frequency | character location(s) as array
                    ne_entity, frequency, pos_list are the keys respective to the above values
        @Params
        text:String: String input for dictionary output
        @Return
        A Dictionary of every entity in the text that contains its type, frequency, and position
        """
        # tokenizes input and assigns entity type for each token
        # result of w_list is an array of tuples [string, entity type]
        w_list = nltk.word_tokenize(text)
        w_list = nltk.pos_tag(w_list)

        # tokenizes based on span and stores start/end positions of original input
        # posList size may be different than w_list because word_tokenize() 
        # can consider punctuation to be tokens while span_tokenize() does not
        posList = list(twt().span_tokenize(text))

        # pos:int: current item to be considered in PosList
        pos = 0

        # entries:dictionary: to be returned with key of tokens and value of an dictionary: 
        # name entity type | frequency | character location(s) as dictionary
        
        # value of dictionary represented as dictionary with valid keys: "ne_type", "frequency", "pos_list"
        entries = {}

        for w in w_list:
            # checks if current token(w) is a punctuation. Skips if punctuation.
            if len(w[0]) > 1 and w[0] not in string.punctuation:
                # if current string is not in entries, a new key/value pair is created with proper starting values
                if w[0] not in entries:
                    # name entity type | frequency | character location(s) as dictionary
                    entries[w[0]] = {"ne_type": w[1],
                                     "frequency": 1,
                                     "pos_list": [posList[pos][0]]}

                # if current string is in entries, frequency is incremented by 1 and 
                # character position list appends current position
                else:
                    entries[w[0]]["frequency"] += 1
                    entries[w[0]]["pos_list"].append(posList[pos][0])
                pos += 1
        return entries

    def get_sentiment(self):
        """
        @Name: sentiment
        @Description: Function will take in a string input and output the sentiment of each sentence
        @Params
        text:String: String input for dictionary output
        @Return
        A Dictionary of sentence in the text that contains its sentiment
        """
        sid_obj = SentimentIntensityAnalyzer()

        res = {}

        # tokenize the paragraph into sentences with nltk
        for sentence in nltk.sent_tokenize(self.text):
            # establish the polarity scores dictonary
            sentiment_dict = sid_obj.polarity_scores(sentence)

            # add sentiment to an overall return dictonary
            res[sentence] = sentiment_dict

        # return the overall dictonary
        self.sentiment = res
        return res

    # sentiment('This is a test. I love dogs. I hate cats.')


if __name__ == "__main__":
    from urllib.request import urlopen
    from bs4 import BeautifulSoup
    import json

    # url = "https://www.cnn.com/europe/live-news/ukraine-russia-putin-news-03-29-22/index.html"

    # html = urlopen(url).read()
    # soup = BeautifulSoup(html, features="html.parser")

    engine = MetadataEngine()
    paragraph = "It was one of the worst movies I've seen, despite good reviews. Unbelievably bad acting!! Poor direction. VERY poor production. The movie was bad. Very bad movie. VERY BAD movie!"
    engine.prime_engine(paragraph)
    print(json.dumps(engine.get_entities_and_sentiments(), indent=4))
    # engine.prime_engine(html)

    # print(f"ARTICLE TEXT: --------------\n{engine.text}")

    # print(f"SENTIMENT: \n "
    #       f"{engine.get_sentiment()}\n"
    #       f"---------------------------\n")
    # print(f"ENTITIES:  \n"
    #       f"{engine.get_entities()} \n"
    #       f"---------------------------\n")
    # print(f"Hyperlinks:   \n"
    #       f"{engine.get_hyperlinks()}  \n"
    #       f"---------------------------\n"
    #       f"")

    # new_text = []
    # for item in engine.text.split():
    #     if item != ' ' and item != '\n':
    #         new_text.append(item)

    # print(f"{engine.text}")
    # print(f"---------------------\n"
    #       f"{new_text}")

    # print(f"Length {len(engine.text.split())}")

    # print(f"SUMMARY:   \n"
    #       f"{engine.summarize_text()}  \n"
    #       f"---------------------------\n"
    #       f"")

    # print(f"DATES:   \n"
    #       f"{engine.get_dates()}  \n"
    #       f"---------------------------\n"
    #       f"")
