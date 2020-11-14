import argparse
import time
from flask import Flask, request, render_template
from config import *
from word_segmentation import SegProcessor
from indexer import Indexer
from retriever import Retriever

app = Flask(__name__)

@app.route('/')
def hello_world():
   return ("Hello World")

@app.route('/search', methods=['POST'])
def search_query():
   query = request.args.get('query')
   restriction = 2 if request.args.get('restriction') is '' else int(request.args.get('restriction'))
   result = retriever.search(query, restriction)
   print(len(result))
   return render_template('result.html', hits=result)

if __name__ == '__main__':

   parser = argparse.ArgumentParser(description='Parser for Backend Options')
   parser.add_argument("-s", "--segmenting", action="store_true", default=False, dest="segmenting",
                        help="This argument is to choose whether you want to run segmentation on corpus or not. If specified, the segmenting will be executed.")
   parser.add_argument("-i", "--indexing",  action="store_true", default=False, dest="indexing",
                        help="This argument is to choose whether you want to run the indexing or not. If specified, then indexing will be executed.")
   parser.add_argument("-t", "--training",  action="store_true", default=False, dest="training",
                        help="This argument is to choose whether you want to process all data to train the result or not. If specified, then training of all data will be executed.")
   parser.add_argument("-l", "--limit", type=int, default=100, dest="limit", help="This argument is to set the limits of both indexing and segmenting")
   parser.add_argument("-a", "--startapp", action="store_true", default=False, dest="startapp",
                        help="This argument is to choose whether you want to activate RETREIVER and the App or not. If specified, then Flask app will start along side with Retriever.")
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

   if opts.startapp:
      print()
      print("==========STARTAPP==========")
      global retriever
      retriever = Retriever()
      # app.debug = True
      app.run()
      print()


'''
   vm_env = lucene.getVMEnv()
   vm_env.attachCurrentThread()
'''