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
      # else:
      #   cutted = self.lac.cut(term, text=False)
      #   for cutted_term in cutted:
      #     phrase.append(cutted_term)
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
        result_contexts.append(''.join(terms))
    
    return result_contexts, parsed_query

  def search_terms(self, parsed_query):
    print(".....search_terms")
    total_hits = self.searcher.search(parsed_query, MAX)
    result_contexts = []
    for hit in total_hits.scoreDocs:
      doc = self.searcher.doc(hit.doc)
      context = doc.get('context')
      result_contexts.append(context)
    
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
    for hit in self.recovered_hits:
      highlighter = Highlighter(simpleHTMLFormatter, QueryScorer(parsed_query))
      highLightText = highlighter.getBestFragment(self.analyzer, 'context', hit)
      if highLightText is not None:
        final_result.append(highLightText)
    
    return final_result

  def recover_to_article(self, query_str, contexts, restriction):
    self.recovered_query = []
    self.recovered_context = []

    self.recovered_hits = []

    for context in contexts:
      terms = context.split(' ')
      length = len(terms)
      self.recovered_hits.append(''.join(terms))
      # for matched_index, term in enumerate(terms):
      #   if term == query_str:
      #     tmp_matched_query = self.get_restriction_query(terms, length, matched_index, restriction)
      #     self.recovered_query.append(tmp_matched_query)
      #     self.recovered_context.append(''.join(terms))

      
      #     tmp_matched_hit = ''
      #     if matched_index == 0:
      #       tmp_matched_hit += \
      #         (terms[0]) \
      #         + (terms[1] if terms[1] not in punctuation else '') \
      #         + ' '
      #     elif matched_index == 1:
      #       tmp_matched_hit += \
      #         (terms[0] + terms[1]) \
      #         + (terms[2] if terms[2] not in punctuation else '') \
      #         + ' '
      #     elif matched_index == length-2:
      #       tmp_matched_hit += \
      #         (terms[length-3] + terms[length-2] \
      #         if terms[length-3] not in punctuation else terms[length-2]) \
      #         + ' '
      #     elif matched_index == length-3:
      #       tmp_matched_hit = \
      #         (terms[length-4] + terms[length-3] + terms[length-2] \
      #         if terms[length-4] not in punctuation else terms[length-3] + terms[length-2]) \
      #         + ' '
      #     elif matched_index >= 2 and matched_index <= length-4:
      
    self.recovered_hits = list(set(self.recovered_hits))
    if '' in self.recovered_hits:
      self.recovered_hits.remove('')
      
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

    