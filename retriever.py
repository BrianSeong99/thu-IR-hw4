import lucene
from config import *
from java.nio.file import Paths
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.analysis.cn.smart import SmartChineseAnalyzer
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.util import Version
from org.apache.lucene.search.highlight import Highlighter, QueryScorer, SimpleHTMLFormatter

# 为了在判断位置约束的时候用，加载stopwords
with open('stopwords.txt', 'r') as f:
  global punctuation
  punctuation = []
  for p in f:
    punctuation.append(p.strip('\n'))

class Retriever:
  def __init__(self, path=INDEX_DIR):
    # 初始化lucene，设置好analyzer、reader、searcher和分词器
    lucene.initVM()
    self.indir = SimpleFSDirectory(Paths.get(path))
    self.analyzer = SmartChineseAnalyzer()
    self.reader = DirectoryReader.open(self.indir)
    self.searcher= IndexSearcher(self.reader)
  
  # pylucene库自己本身有问题，没有办法自己控制线程，需要每次自己手动attach一个防止线程出错
  def attachCurrentThread(self):
    vm_env = lucene.getVMEnv()
    vm_env.attachCurrentThread()
    return vm_env

  # 当用户搜索的query中带有词性时
  def search_phrases(self, query_str):
    print(".....search_phrases")
    # 用来存储用户的输入的词语
    queries = []
    # 用来存储用户的输入的词性
    query_phrases = []
    # 提取用户输入的搜索词
    query_terms = query_str.split()
    for term in query_terms:

      # 假如用户输入的词中有词性
      if '/' in term:
        cutted_term = term.split('/')
        queries.append(cutted_term[0])
        query_phrases.append(cutted_term[1])

      # 假如用户输入的词中没有词性，则默认给''
      else:
        queries.append(term)
        query_phrases.append('')
    
    parsed_query = QueryParser("context", self.analyzer).parse(' '.join(queries))
    # 信息检索
    total_hits = self.searcher.search(parsed_query, MAX)
    result_contexts = []
    for hit in total_hits.scoreDocs:
      doc = self.searcher.doc(hit.doc)
      terms = (doc.get("context")).split(" ")
      phrases = (doc.get("phrase")).split(" ")
      # 用于判断搜索到的内容的query字段的词性是否与用户所期望的词性相符
      flag = True

      for index, term in enumerate(terms):
        if term in queries:
          i = queries.index(term)
          # 对比检索到的词语的词性是否和用户输入的词性一致，不一致就不添加该document到返回结果中
          if query_phrases[i] != phrases[index] and query_phrases[i] != '':
            flag = False
            break
      if flag:
        result_contexts.append([' '.join(terms), hit.score])
    
    return result_contexts

  # 当用户搜索的query中没有词性时
  def search_terms(self, parsed_query):
    print(".....search_terms")
    # 信息检索
    total_hits = self.searcher.search(parsed_query, MAX)
    result_contexts = []
    for hit in total_hits.scoreDocs:
      doc = self.searcher.doc(hit.doc)
      context = doc.get('context')
      result_contexts.append([context, hit.score])
    
    return result_contexts

  # 从flask对接过来的接口，
  def search(self, query_str, restriction=2):
    self.attachCurrentThread()

    # 对query进行解析
    result_contexts = []
    # 根据有没有‘/’判断有没有词性，
    if '/' in query_str:
      # 有词性就转到search_phrases
      result_contexts = self.search_phrases(query_str)
    else:
      # 有词性就转到search_terms
      result_contexts = self.search_terms(QueryParser("context", self.analyzer).parse(query_str))
    
    # 将搜索结果复原为文章返回
    self.recover_to_article(query_str, result_contexts, restriction)
    
    final_result = []
    #进行搜索结果中跟query相关的文段高量处理
    simpleHTMLFormatter = SimpleHTMLFormatter(u"<b><font color='red'>", u"</font></b>")
    for index, recovered_query in enumerate(self.recovered_queries):
      # 不是直接拿用户输入的query来进行高亮处理，而是通过我们自己处理好的包含了位置约束的query进行高亮处理
      recovered_query = recovered_query.replace("/", ",")
      highlighter = Highlighter(simpleHTMLFormatter, QueryScorer(QueryParser("context", self.analyzer).parse(recovered_query)))
      highLightText = highlighter.getBestFragment(self.analyzer, 'context', self.recovered_contexts[index])
      if highLightText is not None:
        final_result.append(highLightText)

    return final_result

  # 将搜索结果复原为文章返回
  def recover_to_article(self, query_str, contexts, restriction):
    self.recovered_queries = []
    self.recovered_contexts = []

    for context in contexts:
      # context中第一个元素是还未处理的文章内容，第二个元素是score
      terms = context[0].split(' ')
      score = context[1]
      length = len(terms)
      for matched_index, term in enumerate(terms):
        # 假如该词在用户输入的搜索query中
        if term in query_str:
          joined = ''.join(terms)
          # 确保没有重复的结果，跟set效果一致
          if joined not in self.recovered_contexts:
            # 位置约束处理
            tmp_matched_query = self.get_restriction_query(terms, length, matched_index, restriction)
            # 添加位置约束处理过后的query
            self.recovered_queries.append(tmp_matched_query)
            # 添加检索到的文段内容
            self.recovered_contexts.append(joined)
          # 多检索词语的情况下
          else:
            index = self.recovered_contexts.index(joined)
            # 位置约束处理
            tmp_matched_query = self.get_restriction_query(terms, length, matched_index, restriction)
            # 添加位置约束处理过后的query
            self.recovered_queries[index] += tmp_matched_query
  
  # 位置拘束
  def get_restriction_query(self, terms, term_length, matched_index, restriction):
    # 以检索到的词语为中心
    sentence = terms[matched_index]
    # 计算左边的边界
    tmp = matched_index - restriction
    left_boundary = tmp if tmp >= 0 else 0
    # 计算右边的边界
    tmp = matched_index + restriction
    right_boundary = tmp if tmp < term_length else (term_length - 1)
    # 左右两边的iterator
    l = matched_index - 1
    r = matched_index + 1
    # 添加在位置约束范围内的内容
    while left_boundary < l and r < right_boundary:
      # 假如左边不是stopwords，则添加
      if terms[l] not in punctuation:
        temp = terms[l]
        temp += sentence
        sentence = temp
        l -= 1
      # 假如右边不是stopwords，则添加
      if terms[r] not in punctuation:
        sentence += terms[r]
        r += 1
      # 假如左右都是stopwords，则退出
      if terms[l] in punctuation and terms[r] in punctuation:
        break
    return sentence

    