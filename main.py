import argparse
import time
from flask import Flask
from config import *
from word_segmentation import SegProcessor
from indexer import Indexer

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
   parser.add_argument("-t", "--training",  action="store_true", default=False, dest="training",
                        help="This argument is to choose whether you want to process all data to train the result or not. If specified, then training of all data will be executed.")
   parser.add_argument("-l", "--limit", type=int, default=100, dest="limit", help="This argument is to set the limits of both indexing and segmenting")
   opts = parser.parse_args()

   training = False

   if opts.training:
      print()
      print("Training Mode On, All data will be segmented and indexed")
      print()
      training = True

   if opts.segmenting:
      print()
      print("==========SEGMENTATION==========")
      start = time.time()
      SegProcessor(segmentation_limit=opts.limit, training=training)
      end = time.time()
      print("Segmentation Time Cost: {}s".format(end-start))
      print("==========SEGMENTATION==========")
      print()

   if opts.indexing:
      print()
      print("==========INDEXING==========")
      start = time.time()
      Indexer(index_limit=opts.limit, training=training)
      end = time.time()
      print("Indexing Time Cost: {}s".format(end-start))
      print("==========INDEXING==========")
      print()

      # app.run()

      # test
