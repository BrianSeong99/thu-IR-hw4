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
from org.apache.lucene.search.highlight import Highlighter, QueryScorer, SimpleHTMLFormatter

with open('stopwords.txt', 'r') as f:
  global punctuation
  punctuation = []
  for p in f:
    punctuation.append(p.strip('\n'))

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

  def search_phrases(self, query_str):
    print(".....search_phrases")
    queries = []
    query_phrases = []
    query_terms = query_str.split()
    for term in query_terms:
      if '/' in term:
        cutted_term = term.split('/')
        queries.append(cutted_term[0])
        query_phrases.append(cutted_term[1])
      else:
        queries.append(term)
        query_phrases.append('')
    
    parsed_query = QueryParser("context", self.analyzer).parse(' '.join(queries))
    total_hits = self.searcher.search(parsed_query, MAX)
    result_contexts = []
    for hit in total_hits.scoreDocs:
      doc = self.searcher.doc(hit.doc)
      terms = (doc.get("context")).split(" ")
      phrases = (doc.get("phrase")).split(" ")
      flag = True

      for index, term in enumerate(terms):
        if term in queries:
          i = queries.index(term)
          if query_phrases[i] != phrases[index]:
            flag = False
            break
      if flag:
        result_contexts.append([' '.join(terms), hit.score])
    
    return result_contexts, parsed_query

  def search_terms(self, parsed_query):
    print(".....search_terms")
    total_hits = self.searcher.search(parsed_query, MAX)
    result_contexts = []
    for hit in total_hits.scoreDocs:
      doc = self.searcher.doc(hit.doc)
      context = doc.get('context')
      result_contexts.append([context, hit.score])
    
    return result_contexts

  def search(self, query_str, restriction=2):
    self.attachCurrentThread()

    parsed_query = QueryParser("context", self.analyzer).parse(query_str)
    result_contexts = []
    if '/' in query_str:
      result_contexts, parsed_query = self.search_phrases(query_str)
    else:
      result_contexts = self.search_terms(parsed_query)
    
    self.recover_to_article(query_str, result_contexts, restriction)
    
    final_result = []
    simpleHTMLFormatter = SimpleHTMLFormatter(u"<b><font color='red'>", u"</font></b>")
    for index, recovered_query in enumerate(self.recovered_queries):
      highlighter = Highlighter(simpleHTMLFormatter, QueryScorer(QueryParser("context", self.analyzer).parse(recovered_query)))
      highLightText = highlighter.getBestFragment(self.analyzer, 'context', self.recovered_contexts[index])
      if highLightText is not None:
        final_result.append(highLightText)
    
    return final_result

  def recover_to_article(self, query_str, contexts, restriction):
    self.recovered_queries = []
    self.recovered_contexts = []

    for context in contexts:
      terms = context[0].split(' ')
      score = context[1]
      length = len(terms)
      for matched_index, term in enumerate(terms):
        if term in query_str:
          joined = ''.join(terms)
          if joined not in self.recovered_contexts:
            tmp_matched_query = self.get_restriction_query(terms, length, matched_index, restriction)
            self.recovered_queries.append(tmp_matched_query)
            self.recovered_contexts.append(joined)
      
  def get_restriction_query(self, terms, term_length, matched_index, restriction):
    sentence = terms[matched_index]
    tmp = matched_index - restriction
    left_boundary = tmp if tmp >= 0 else 0
    tmp = matched_index + restriction
    right_boundary = tmp if tmp < term_length else (term_length - 1)
    l = matched_index - 1
    r = matched_index + 1
    while left_boundary < l and r < right_boundary:
      if terms[l] not in punctuation:
        temp = terms[l]
        temp += sentence
        sentence = temp
        l -= 1
      if terms[r] not in punctuation:
        sentence += terms[r]
        r += 1
      if terms[l] in punctuation and terms[r] in punctuation:
        break
    return sentence

    