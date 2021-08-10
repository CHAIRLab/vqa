### 代码包含两部分逻辑：1）基于问题生成word graph； 2）将word graph 与 scene graph 匹配
1） 基于问题生成word graph
###  cd src
###  python parse.py
###  解析结果见src/Data/word_graph
2) 将word graph 与 scene graph 匹配
### cd src/Query
### 执行 executor.java程序
图匹配结果见 ![img.png](img.png)

环境配置
### python:3.6.4
### pip install -r requirement.txt
### jdk:1.8.0
### eclipse