import tweepy,re
from textblob import TextBlob
import matplotlib.pyplot as plt
import json
import pymongo
from pymongo import MongoClient

class DatabaseConnection:
   
    def createConnectionDB(self):
        
        try:
            self.myclient = MongoClient("mongodb+srv://henipatel:henipatel@cluster0-9y1qg.gcp.mongodb.net/test?retryWrites=true&w=majority")

            self.myclient.server_info()
            return True   
        except pymongo.errors.ServerSelectionTimeoutError as err:
            #print("Connection failed to database")
            print(err)
        return False
               
    #def insertData(self, ):

class SentimentAnalysis:

    def __init__(self):
        self.tweets = []
        self.raw_tweets = []
        self.tweetText = []
        self.NoOfTerms = 0
        self.searchTerm = ""

    def DownloadData(self):
        # authenticating
        
        consumerKey = '10QuSgbBdTipAFQJG3lyLM6nM'
        consumerSecret = 'rRY3fGU6Zs4aiJfWgbsQJraWZNDIZ7Od4b9YOmGZlq7Uejyb4F'
        accessToken = '553787569-Juool4E8waLnAlhqmGZlzpKmBmEooso0eOsgiOSp'
        accessTokenSecret = 'gr0eMLWZua15pWuTO8KHpn0LErvVEj5ZjBjEDdrFmaABu'
        auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
        auth.set_access_token(accessToken, accessTokenSecret)
        api = tweepy.API(auth)
        
        # input for term to be searched and how many tweets to search
        self.searchTerm = input("Enter Keyword/Tag to search about: ")
        self.NoOfTerms = int(input("Enter how many tweets to search: "))

        # searching for tweets
        self.tweets = tweepy.Cursor(api.search, q=self.searchTerm, lang = "en").items(self.NoOfTerms)
        self.raw_tweets = self.tweets
        #print(str(tweets))
        print("Tweets fetched successfully")
        #print(list(self.raw_tweets))
    
        # heni - start
        file_name = str(self.NoOfTerms) + "-"+ self.searchTerm +"-"+ "tweets" +".json"
        
        #clean_tweets_dict = {"created_at": "2020-03-13 07:02:00","tweet_text": "text","user_screen_name": "name","is_retweet": "reweet", "is_quote": "quote", "quoted_text": "qtext" }
        clean_tweets_dict = {} 
        self.clean_tweets = []
        
        t_list = list(self.raw_tweets)
        if len(t_list) == 0:
            print("No tweets")
        else:
            print("not null list")
            
        for fetched_tweet in t_list:
            
            is_retweet = hasattr(fetched_tweet, "retweeted_status")
            # check if text has been truncated
            if hasattr(fetched_tweet,"extended_tweet"):
                text = fetched_tweet.extended_tweet["full_text"]
                text = self.cleanTweet(text)
            else:
                text = self.cleanTweet(fetched_tweet.text)
            text=text
            #print (text)
            #Append to temp so that we can store in csv later. I use encode UTF-8
            self.tweetText.append(text)
            # check if this is a quote tweet.
            is_quote = hasattr(fetched_tweet, "quoted_status")
            
            quoted_text = ""
            if is_quote:
                # check if quoted tweet's text has been truncated before recording it
                if hasattr(fetched_tweet.quoted_status,"extended_tweet"):
                    quoted_text = fetched_tweet.quoted_status.extended_tweet["full_text"]
                else:
                    quoted_text = fetched_tweet.quoted_status.text

            # remove characters that might cause problems with csv encoding
            #print(quoted_text)
            remove_characters = [",","\n"]
            for c in remove_characters:
                text.replace(c," ")
                quoted_text.replace(c, " ")
            
            location = fetched_tweet.user.location
            
            clean_tweets_dict = {"created_at": fetched_tweet.created_at,"tweet_text": text,"user_screen_name": fetched_tweet.user.screen_name,"is_retweet": is_retweet, "is_quote": is_quote, "quoted_text": quoted_text, "location": location}
            self.clean_tweets.append(clean_tweets_dict)
        try:
            db_data = json.dumps(self.clean_tweets, indent=4, sort_keys=True, default=str)
            with open(file_name, 'a') as tf:
                tf.write(db_data)       
        except BaseException as e:
            print("Error save_tweets %s" % str(e))
       
        print("Tweets saved to file successfully")
        print()
        
        #entering data to database
        # create connection to database and insert data to database
        dbconn = DatabaseConnection()
    
        if dbconn.createConnectionDB():
            print("connection successful")
            db = dbconn.myclient["twitter_analysis_db"]
            myCollection = db["WHO"]           
            x = myCollection.insert_many(self.clean_tweets)
            print("Data inserted successfully")
        else :
            print("connection failed")
            print("failed to insert data to database")   
        
        # Open/create a file to append data to
        #csvFile = open('result.csv', 'a')

        # Use csv writer
        #csvWriter = csv.writer(csvFile)

         # creating some variables to store info
        polarity = 0
        positive = 0
        wpositive = 0
        spositive = 0
        negative = 0
        wnegative = 0
        snegative = 0
        neutral = 0

        t1_list = list(self.clean_tweets)
        if len(t1_list) == 0:
            print("No tweets")
        else:
            print("not null list")
            # iterating through tweets fetched
            for tweet in self.tweetText:
                #print(tweet)
                
                # print (tweet.text.translate(non_bmp_map))    #print tweet's text
                analysis = TextBlob(tweet)
                # print(analysifs.sentiment)  # print tweet's polarity
                polarity += analysis.sentiment.polarity  # adding up polarities to find the average later

                if (analysis.sentiment.polarity == 0):  # adding reaction of how people are reacting to find average later
                    neutral += 1
                elif (analysis.sentiment.polarity > 0 and analysis.sentiment.polarity <= 0.3):
                    wpositive += 1
                elif (analysis.sentiment.polarity > 0.3 and analysis.sentiment.polarity <= 0.6):
                    positive += 1
                elif (analysis.sentiment.polarity > 0.6 and analysis.sentiment.polarity <= 1):
                    spositive += 1
                elif (analysis.sentiment.polarity > -0.3 and analysis.sentiment.polarity <= 0):
                    wnegative += 1
                elif (analysis.sentiment.polarity > -0.6 and analysis.sentiment.polarity <= -0.3):
                    negative += 1
                elif (analysis.sentiment.polarity > -1 and analysis.sentiment.polarity <= -0.6):
                    snegative += 1


            # Write to csv and close csv file
            #csvWriter.writerow(self.tweetText)
            #csvFile.close()

            # finding average of how people are reacting
            positive = self.percentage(positive, self.NoOfTerms)
            wpositive = self.percentage(wpositive, self.NoOfTerms)
            spositive = self.percentage(spositive, self.NoOfTerms)
            negative = self.percentage(negative, self.NoOfTerms)
            wnegative = self.percentage(wnegative, self.NoOfTerms)
            snegative = self.percentage(snegative, self.NoOfTerms)
            neutral = self.percentage(neutral, self.NoOfTerms)

            # finding average reaction
            polarity = polarity / self.NoOfTerms

            # printing out data
            print("How people are reacting on " + self.searchTerm + " by analyzing " + str(self.NoOfTerms) + " tweets.")
            print()
            print("General Report: ")

            if (polarity == 0):
                print("Neutral")
            elif (polarity > 0 and polarity <= 0.3):
                print("Weakly Positive")
            elif (polarity > 0.3 and polarity <= 0.6):
                print("Positive")
            elif (polarity > 0.6 and polarity <= 1):
                print("Strongly Positive")
            elif (polarity > -0.3 and polarity <= 0):
                print("Weakly Negative")
            elif (polarity > -0.6 and polarity <= -0.3):
                print("Negative")
            elif (polarity > -1 and polarity <= -0.6):
                print("Strongly Negative")

            print()
            print("Detailed Report: ")
            print(str(positive) + "% people thought it was positive")
            print(str(wpositive) + "% people thought it was weakly positive")
            print(str(spositive) + "% people thought it was strongly positive")
            print(str(negative) + "% people thought it was negative")
            print(str(wnegative) + "% people thought it was weakly negative")
            print(str(snegative) + "% people thought it was strongly negative")
            print(str(neutral) + "% people thought it was neutral")

            self.plotPieChart(positive, wpositive, spositive, negative, wnegative, snegative, neutral, self.searchTerm, self.NoOfTerms)


    def cleanTweet(self, tweet):
        # Remove Links, Special Characters etc from tweet
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) | (\w +:\ / \ / \S +)", " ", tweet).split())

    # function to calculate percentage
    def percentage(self, part, whole):
        temp = 100 * float(part) / float(whole)
        return format(temp, '.2f')

    def plotPieChart(self, positive, wpositive, spositive, negative, wnegative, snegative, neutral, searchTerm, noOfSearchTerms):
        labels = ['Positive [' + str(positive) + '%]', 'Weakly Positive [' + str(wpositive) + '%]','Strongly Positive [' + str(spositive) + '%]', 'Neutral [' + str(neutral) + '%]',
                  'Negative [' + str(negative) + '%]', 'Weakly Negative [' + str(wnegative) + '%]', 'Strongly Negative [' + str(snegative) + '%]']
        sizes = [positive, wpositive, spositive, neutral, negative, wnegative, snegative]
        colors = ['yellowgreen','lightgreen','darkgreen', 'gold', 'red','lightsalmon','darkred']
        patches, texts = plt.pie(sizes, colors=colors, startangle=90)
        plt.legend(patches, labels, loc="best")
        plt.title('How people are reacting on ' + searchTerm + ' by analyzing ' + str(noOfSearchTerms) + ' Tweets.')
        plt.axis('equal')
        plt.tight_layout()
        plt.show()



if __name__== "__main__":
    sa = SentimentAnalysis()
    sa.DownloadData()
    #sa.generateReport()
    #print(list(raw_t))
    #sa.saveTweetsToDB(raw_t)