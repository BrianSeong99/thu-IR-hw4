from config import *
import os
import thulac

class SegProcessor:
  def __init__(self, segmentation_limit=SEGMENTATION_LIMIT):
    self.segmentation_limit = segmentation_limit
    self.file_loader()

  def file_loader(self):
    lac = thulac.thulac(seg_only=True)
    with open(SEGMENTATION_FILE, 'w') as outfile:
      for file_name in os.listdir(CORPUS_DIR):
        if file_name == ".DS_Store":
          continue
        with open(CORPUS_DIR + file_name, "r") as f:
          print("Segmenting File [", file_name, "]")
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
              if line_count > self.segmentation_limit:
                f.close()
                break
              line = f.readline()
          else:
            line = f.readline()
            line_count = 0
            while (line):
              segmented = lac.cut(line, text=True) # segmentation process
              outfile.write("{}\n".format(segmented))

              # print(segmented)
              print("\r", str(line_count), " lines", end="", flush=True)
              line_count = line_count + 1
              if line_count > self.segmentation_limit:
                f.close()
                break
              line = f.readline()
          print()