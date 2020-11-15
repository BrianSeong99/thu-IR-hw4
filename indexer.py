import os
import lucene
from config import *
from pathlib import Path

from java.nio.file import Paths
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.analysis.core import WhitespaceAnalyzer
from org.apache.lucene.util import Version
from org.apache.lucene.index import IndexWriter, IndexWriterConfig, IndexOptions
from org.apache.lucene.document import Document, Field, FieldType, StringField

'''
    索引搭建模块
'''
class Indexer:
  def __init__(self, path=INDEX_DIR, index_limit=LIMIT, training=False):
    self.index_limit = index_limit
    self.training = training
    
    p = Path(path)
    if not p.is_dir():
      os.mkdir(path)
    
    # 初始化lucene，准备好analyzer和writer
    lucene.initVM()
    indexdir = SimpleFSDirectory(Paths.get(path))
    analyzer = WhitespaceAnalyzer(Version.LATEST) # 由于thulac分词的时候已经实现了用空格来表示不同的词，所以直接用空格分析器就可以。
    iwconf = IndexWriterConfig(analyzer)
    iwconf.setOpenMode(IndexWriterConfig.OpenMode.CREATE_OR_APPEND)
    index_writer = IndexWriter(indexdir, iwconf)

    self.Indexing(index_writer)
  
  def Indexing(self, writer):
    print("Indexing Segmented File [", SEGMENTATION_FILE, "]")
    with open(SEGMENTATION_FILE, 'r') as f:
      line_count = 0
      for line in f:
        # 建立 context 的 fieldtype，需要搭建索引、存储、向量化
        fieldtype_context = FieldType()
        fieldtype_context.setIndexOptions(IndexOptions.DOCS_AND_FREQS)
        fieldtype_context.setStored(True)
        fieldtype_context.setTokenized(True)

        # 建立 phrase 的 fieldtype，只需要保存
        fieldtype_phrase = FieldType()
        fieldtype_phrase.setStored(True)

        # 对分词好的内容进行处理，把词语和词性分开来存储
        processed_context, processed_phrase = self.process_line(line)

        doc = Document()
        # context field是用于记录文章的内容
        doc.add(Field('context', processed_context, fieldtype_context))
        # phrase field适用于记录文章每个词所对应的词性
        doc.add(Field('phrase', processed_phrase, fieldtype_phrase))

        # 把document写入索引库
        writer.addDocument(doc)

        # 跟踪程序运行情况用
        print("\r", str(line_count), " lines", end="", flush=True)
        line_count = line_count + 1
        if line_count > self.index_limit and not self.training:
          break

    writer.close()
    print()

  # 对分词好的内容进行处理，把词语和词性分开来存储
  def process_line(self, line):
    processed_context = []
    processed_phrase = []
    terms = line.split(' ')
    for index, term in enumerate(terms):
      splitted = term.split('_')
      if len(splitted) > 1:
        processed_context.append(splitted[0])
        processed_phrase.append(splitted[1])

    return ' '.join(processed_context), ' '.join(processed_phrase)