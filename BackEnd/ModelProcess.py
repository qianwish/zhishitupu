import jieba
import numpy as np
from jieba import posseg
from sklearn.naive_bayes import GaussianNB
#from sklearn.externals
import joblib
from data_setting import *
from helper import *


class ModelProcess:
    def __init__(self):
        jieba.load_userdict(course_dict_dir_path)  # 加载课程实体词词典
        self.abstract_map = {}  # 存储抽象词与原始词的对应关系，如课程‘并行计算’的抽象词是‘cn’
        self.stopwords = []  # 用于存储停用词
        self.questions_pattern = self.load_questions_pattern()  # 从文件中读取定义的问题类型，存入字典中
        self.vocabulary = self.load_vocabulary()  # 加载词表
        self.model = self.load_classifier_model()  # 模型训练之后，可直接用于预测

    def load_questions_pattern(self):
        questions_pattern = {}  # 初始化一个字典
        for line in helper.read_file(question_classification_dir_path):  # 按行读取question_classification.txt文件中定义的问题类别
            # 如："1:cn 先修课程" 切分成为列表中的两个元素，index存储"1",pattern存储"cn 先修课程"
            tokens = line.split(':')
            index, pattern = tokens[0], tokens[1]
            questions_pattern[int(index)] = pattern  # 存储到字典中，如:{1:'cn 先修课程'}
        return questions_pattern

    # 加载停用词
    def load_stop_words(self):
        for word in helper.read_file(stop_words_dir_path):  # 停用词文件：data/stopwords.txt
            self.stopwords.append(word)

            # 将各个详细问题进行分词,并将分词结果写入vocabulary.txt文件

    def save_vocabulary_to_file(self):
        self.load_stop_words()  # 加载停用词
        train_list = []
        # 创建vocabulary.txt文件，并将详细问题分词后的结果写入
        with open(vocabulary_dir_path, 'a', encoding='utf-8') as f:
            for file in os.listdir(detailed_questions_dir_path):  # 遍历data/question/detailed_questions/目录下的所有文件
                file_path = os.path.join(detailed_questions_dir_path, file)  # 组合路径，每个问题文件的绝对路径
                if os.path.isdir(file_path):  # 如果file_path为目录，则跳出本次循环
                    continue
                for line in helper.read_file(file_path):  # 读取每个问题文件，并按行遍历
                    terms = posseg.cut(line)  # 采用结巴工具包进行分词，返回分词和词性
                    for term in terms:  # 遍历分词结果
                        if term.word in train_list or term.word in self.stopwords or term.word == ' ':  # 防止数据重复
                            continue
                        train_list.append(term.word)
                        f.write(term.word + '\n')  # 将词写入文件

    # 如果vocabulary.txt文件是否为空，则调用save_vocabulary_to_file()方法创建此表文件；并加载词表，转换成字典格式
    def load_vocabulary(self):
        vocabulary = {}
        if not os.path.exists(vocabulary_dir_path):  # 如果vocabulary.txt文件是否为空
            self.save_vocabulary_to_file()  # 则将各个详细问题进行分词,并将分词结果写入vocabulary.txt文件
        index = 0
        for line in helper.read_file(vocabulary_dir_path):  # 加载词表，并以字典的形式存放，index作为key值，line作为value
            # 以字典形式存放入vocabulary字典  index作为key值，line作为value
            vocabulary[line] = index
            index += 1
        return vocabulary

    # 创建和词表中词的数量相等的全0列表，将句子进行jieba分词，如果词在词表中，值更改为1，不在词表中，值保持为0。
    def sentence_to_array(self, line):
        vector = [0] * len(self.vocabulary)  # 创建和词表中词的数量相等的全0数组
        terms = posseg.cut(line)  # 采用结巴工具包进行分词，返回分词和词性
        for term in terms:  # 遍历分词结果
            word = term.word
            if word in self.vocabulary:  # 如果词在词表中
                index = self.vocabulary[word]  # 找到word在词表中的位置
                vector[index] = 1  # vector中相同的位置值更改为1
        return vector

    # 加载朴素贝叶斯模型
    def load_classifier_model(self):
        model = joblib.load('model_for_NB/model.pickle')
        return model

    # 将句子抽象化，eg.算法分析与设计的学分 --> cn 的 学分
    def query_abstract(self, question):
        terms = posseg.cut(question)  # jieba分词
        abstract_query = ""  # 用来存储问题抽象之后的结果
        for term in terms:  # 遍历分词结果
            word = term.word
            print(term.word, term.flag)
            term_str = str(term)  # 将分词结果转换为字符串
            if term.flag == 'cn':  # 词性为cn的词，即用cn表示课程名称
                abstract_query += "cn "
                self.abstract_map['cn'] = word  # 保存cn和某门课程名称之间的映射关系
            else:
                abstract_query += word + " "  # 添加不是课程名称的词
        return abstract_query

    # 找到抽象后的问题对应的问题模板中的问句
    def query_classify(self, ab_str):
        test_array = self.sentence_to_array(ab_str)  # 调用sentence_to_array()方法，将抽象后的句子转化为数组
        index = self.model.predict([test_array])  # 使用朴素贝叶斯模型对数据进行预测
        model_index = int(index)  # 问题的类别编号
        print("问题的类别编号是:", model_index)
        return model_index, self.questions_pattern[model_index]  # 返回问题类别及预先定义的问题模板

    # 将抽象词替换回原始名词，如将‘cn’替换为对应的课程名称
    def query_extension(self, str_pattern):
        for key in self.abstract_map:
            # key为模板中的代词，如'cn'
            if key in str_pattern:
                value = self.abstract_map[key]  # 找到代词对应的原始的名词
                str_pattern = str_pattern.replace(key, value)  # 将问题模板中的问题替换成原始的名词
        self.abstract_map.clear()  # 将abstract_map清空，以避免影响下次执行
        return str_pattern

    # 原始问题->抽象表示->对应的问题模板->将问题模板中的抽象词替换回原有名词
    def analysis_query(self, question):
        print("原始句子:", question)
        question = question.replace('-', '', -1).replace('/', '', -1)  # 去掉问句中的“-”符号和“/”符号
        ab_str = self.query_abstract(question)  # 调用query_abstract()方法，将句子进行抽象表示
        print("替换关键词之后:", ab_str)
        index, str_pattern = self.query_classify(ab_str)  # 调用query_classify()方法，找到对应的问题模板中的问句
        print("句子套用对应的问题模板后:", str_pattern)
        final_pattern = self.query_extension(str_pattern)  # 调用query_extension()方法，将问题模板中的抽象词替换回原有名词
        print("原始句子替换成系统可识别的结果:", final_pattern)
        final_pattern_array = final_pattern.split(' ')
        return index, final_pattern_array
def main():
    query_process = ModelProcess() # 实例化ModelProcess类
    query_process.analysis_query("C语言程序设计的学分") # 模拟用户问题测试

if __name__ == '__main__':
    main()
