# IR_system

成镇宇 计76 2017080068

## 文件结构梳理

```bash
flaskapp
├── Data # 里面有原始语料库，
│   ├── CORPUS/ # 原始语料库
│   ├── INDEX/ # 建好的索引数据
│   ├── SEGMENTATION/ # thulac处理过的所有分词数据
│   └── SEGMENTATION.txt 
├── README.md
├── Report # 报告
│   ├── pics/
│   ├── report.pdf
│   └── report.md
├── THULAC_lite_c++_v1/ # thulac c++ 库
├── config.py # 一些工程的配置文件
├── indexer.py # 索引建立
├── main.py # 主运行文件
├── retriever.py # 信息检索
├── stopwords.txt # 去除stopwords用的stopwords列表
├── word_segmentation.py # python实现的thulac代码
└── templates # 前端代码
    ├── css/
    ├── home.html
    ├── js/
    └── result.html

```



## 命令行指令

**想要直接运行flaskapp，就输入`python main.py -a`即可**

```bash
python main.py --help
usage: main.py [-h] [-s] [-i] [-t] [-l LIMIT] [-a]

Parser for Backend Options

optional arguments:
  -h, --help            show this help message and exit
  -s, --segmenting      This argument is to choose whether you want to run
                        segmentation on corpus or not. If specified, the
                        segmenting will be executed.
  -i, --indexing        This argument is to choose whether you want to run the
                        indexing or not. If specified, then indexing will be
                        executed.
  -t, --training        This argument is to choose whether you want to process
                        all data to train the result or not. If specified,
                        then training of all data will be executed.
  -l LIMIT, --limit LIMIT
                        This argument is to set the limits of both indexing
                        and segmenting
  -a, --startapp        This argument is to choose whether you want to
                        activate RETREIVER and the App or not. If specified,
                        then Flask app will start along side with Retriever.
```



## 前端使用

在浏览器上前往`localhost:5000/`

### **每次搜索的时候搜索框里一定得有东西！**

1. **无位置约束：**

   1. word word 搜索：直接输入即可

      ```
      中国 强大
      ```

   2. word/phrase word/phrase搜索：`词语/词性`

      ```
      中国/n 强大/a
      ```

2. **有位置约束：**

   1. word word 搜索 + 位置约束：直接输入即可，在`restriction`输入2-5之间的数值

      ```
      中国 强大 
      2
      ```

   2. word/phrase word/phrase搜索 + 位置约束：`词语/词性`，在`restriction`输入2-5之间的数值

      ```
      中国/n 强大/a
      2
      ```

3. **前四种的混合：**

   即搜索词中，有的词可以有phrase也可以没有，位置约束也是可加可以不加。比如

   ```
   中国/n 强大
   2
   ```

