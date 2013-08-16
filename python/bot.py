import HTMLParser
import json
from tempfile import NamedTemporaryFile

from tweepy.streaming import StreamListener
from tweepy import API, OAuthHandler, Stream

from interpreter import run

from settings import (CONSUMER_TOKEN, CONSUMER_SECRET,
                      ACCESS_TOKEN, ACCESS_SECRET)


hp = HTMLParser.HTMLParser()


class Listener(StreamListener):

    def __init__(self, auth):
        self.auth = auth

    def on_data(self, data):
        data = json.loads(data)
        d, user = data["text"], data["user"]["screen_name"]
        d = d.replace("#gbc", "")
        d = hp.unescape(d)
        print d

        try:
            context = run(d)
            with NamedTemporaryFile(suffix=".png") as tf:
                context.canvas.save(tf.name)
                API(self.auth).update_status_with_media(
                        tf.name, status="@%s Here ya go!" % user)
        except Exception as e:
            print e

        return True

    def on_error(self, status):
        print status


if __name__ == "__main__":

    auth = OAuthHandler(CONSUMER_TOKEN, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

    stream = Stream(auth, Listener(auth))
    stream.filter(track=["#gbc"])

