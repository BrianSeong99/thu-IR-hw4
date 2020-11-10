from flask import Flask
import argparse


app = Flask(__name__)

@app.route('/')
def hello_world():
   return ("Hello World")

if __name__ == '__main__':

   parser = argparse.ArgumentParser(description='Parser for Backend Options')
   parser.add_argument("-i", "--indexing",  action='store_true', default=False, dest= "indexing", help="This argument is to choose whether you want to run the indexing or not. If specified, then indexing will be executed.")
   opts = parser.parse_args()

   print(opts.indexing)

   # app.run()