import lucene
import thulac
from config import *
from java.nio.file import Paths
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.analysis.cn.smart import SmartChineseAnalyzer
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.util import Version

class Retriever:
  def __init__(self, path=INDEX_DIR):
    lucene.initVM()
    self.indir = SimpleFSDirectory(Paths.get(path))
    self.analyzer = SmartChineseAnalyzer()
    self.reader = DirectoryReader.open(self.indir)
    self.searcher= IndexSearcher(self.reader)
    self.lac = thulac.thulac()
  
  def attachCurrentThread(self):
    vm_env = lucene.getVMEnv()
    vm_env.attachCurrentThread()
    return vm_env

  def search(self, query_str, restriction=2):
    self.attachCurrentThread()

    my_query = QueryParser("context", self.analyzer).parse(query_str)
    total_hits = self.searcher.search(my_query, MAX)

    result_context = []
    for hit in total_hits.scoreDocs:
      print(hit.score)
      doc = self.searcher.doc(hit.doc)
      context = doc.get("context")
      result_context.append(context)
    print(result_context)

    