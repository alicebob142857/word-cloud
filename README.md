# 词云生成

我统计公共管理部分顶刊近一年英文论文的标题，将标题里面的词统计频率后，制作了一个词云图。

- crawler.py 爬虫
- cloud.py 词频统计
- display.py 词云制作
- results.png 输出结果
- images 存储着词云的背景图片
- data 词频统计字典
- lib 期刊信息表格

## 1. 爬虫

crawler.py 为访问 google scholar 的爬虫程序，经过测试基本可以正常使用，首先需要在 google scholar 上精确搜索期刊名并限制时间为 2023-2024，然后复制网址到程序中，自动将相关信息存储在字典中。也可以直接修改 journal 变量

```
# source:"Public Administation Review"
journal = 'source:Public+source:Administration+source:Review'
```

但是运行一段时间后会被 google scholar 封 ip，因此程序在访问失败后后自动睡眠一段时间，并每爬取一定信息即自动保存文件。由于中文期刊的投稿量普遍较少，因此最后直接在知网上导出期刊近一年文章的 citations 后，存储到 xls 文件中，保存在 lib 文件夹里。

## 2. 词频统计

cloud.py 为根据存储得到的期刊信息，提取出标题中的词后，统计频率，最后存储在 data 文件夹中。由于没有找到合适的对英文词汇分词的 nlp 模型，我将所有文章的关键词存储在一个集合里面，在标题中检索到关键词后，即按照短语进行分词。

## 3. 词云绘制

display.py 使用 wordcloud 库进行词云的绘制。同时可以根据背景图片生成掩码，将词云绘制在背景图片灰度值大于 0 的区域。同时可以通过修改不透明度，将背景图片和词云叠加在一起。

```
image = setAlpha(image, 0)
wordcloud_image = setAlpha(wordcloud_image, 200)
```
