from flask import Flask
import argparse
from word_segmentation import SegProcessor


app = Flask(__name__)


@app.route('/')
def hello_world():
    return ("Hello World")


if __name__ == '__main__':

   parser = argparse.ArgumentParser(description='Parser for Backend Options')
   parser.add_argument("-s", "--segmenting", action="store_true", default=False, dest="segmenting",
                        help="This argument is to choose whether you want to run segmentation on corpus or not. If specified, the segmenting will be executed.")
   parser.add_argument("-i", "--indexing",  action="store_true", default=False, dest="indexing",
                        help="This argument is to choose whether you want to run the indexing or not. If specified, then indexing will be executed.")
   opts = parser.parse_args()

   if opts.segmenting:
      SegProcessor()

   if opts.indexing:
      Indexer()

      # app.run()

      # test
