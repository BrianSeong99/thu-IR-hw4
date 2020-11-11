from flask import Flask
import argparse
from word_segmentation import SegProcessor
from indexer import Indexer
import time



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
      print()
      print("==========SEGMENTATION==========")
      start = time.time()
      SegProcessor()
      end = time.time()
      print("Segmentation Time Cost: {}s".format(end-start))
      print("==========SEGMENTATION==========")
      print()

   if opts.indexing:
      print()
      print("==========INDEXING==========")
      Indexer()
      print("==========INDEXING==========")
      print()

      # app.run()

      # test
