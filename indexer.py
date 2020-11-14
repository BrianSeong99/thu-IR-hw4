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


class Indexer:
  def __init__(self, path=INDEX_DIR, index_limit=LIMIT, training=False):
    self.index_limit = index_limit
    self.training = training
    
    p = Path(path)
    if not p.is_dir():
      os.mkdir(path)
    
    lucene.initVM()
    indexdir = SimpleFSDirectory(Paths.get(path))
    analyzer = WhitespaceAnalyzer(Version.LATEST)
    iwconf = IndexWriterConfig(analyzer)
    iwconf.setOpenMode(IndexWriterConfig.OpenMode.CREATE_OR_APPEND)
    index_writer = IndexWriter(indexdir, iwconf)

    self.Indexing(index_writer)
  
  def Indexing(self, writer):
    print("Indexing Segmented File [", SEGMENTATION_FILE, "]")
    with open(SEGMENTATION_FILE, 'r') as f:
      line_count = 0
      for line in f:
        fieldtype_context = FieldType()
        fieldtype_context.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)
        fieldtype_context.setStored(True)
        fieldtype_context.setTokenized(True)

        fieldtype_phrase = FieldType()
        fieldtype_phrase.setStored(True)

        processed_context, processed_phrase = self.process_line(line)

        doc = Document()
        doc.add(Field('context', processed_context, fieldtype_context))
        doc.add(Field('phrase', processed_phrase, fieldtype_phrase))

        writer.addDocument(doc)

        print("\r", str(line_count), " lines", end="", flush=True)
        line_count = line_count + 1
        if line_count > self.index_limit and not self.training:
          break

    writer.close()
    print()

  def process_line(self, line):
    processed_context = []
    processed_phrase = []
    terms = line.split(' ')
    for index, term in enumerate(terms):
      splitted = term.split('_')
      if len(splitted) > 1:
        processed_context.append(term)
        processed_phrase.append(splitted[1])
    
    return ' '.join(processed_context), ' '.join(processed_phrase)