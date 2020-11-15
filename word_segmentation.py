from config import *
import os
import thulac

'''
	分词模块
'''
class SegProcessor:
  def __init__(self, segmentation_limit=LIMIT, training=False):
    self.training = training
    self.segmentation_limit = segmentation_limit
    self.file_loader()

  def file_loader(self):
    lac = thulac.thulac()
    with open(SEGMENTATION_FILE, 'w') as outfile:
      for file_name in os.listdir(CORPUS_DIR):
        if file_name == ".DS_Store":
          continue
        with open(CORPUS_DIR + file_name, "r") as f:
          print("Segmenting File [", CORPUS_DIR+file_name, "]")

          # 语料库是Sogou的情况下
          if "Sogou" in file_name:
            line_count = 0
            line = f.readline()
            while (line):
              terms = line.split(" ")
              for i in range(len(terms)):
                if terms[i] == '<N>':
                  terms[i] = '0'
              
              s = ""
              combined = s.join(terms) # merged a sentence
              segmented = lac.cut(combined, text=True) # segmentation process
              outfile.write("{}\n".format(segmented))

              # print(segmented)
              print("\r", str(line_count), " lines", end="", flush=True)
              line_count = line_count + 1
              if line_count > self.segmentation_limit and not self.training:
                f.close()
                break
              line = f.readline()
          
          # 语料库不是Sogou的情况下
          else:
            line = f.readline()
            line_count = 0
            while (line):
              segmented = lac.cut(line, text=True) # segmentation process
              outfile.write("{}\n".format(segmented))

              # print(segmented)
              print("\r", str(line_count), " lines", end="", flush=True)
              line_count = line_count + 1
              if line_count > self.segmentation_limit and not self.training:
                f.close()
                break
              line = f.readline()
          print()
