import jieba
import numpy as np
from jieba import posseg
from sklearn.naive_bayes import GaussianNB
#from sklearn.externals \
import joblib
from data_setting import *
from helper import *

class NBmodel:
    def __init__(self):
        jieba.load_userdict(course_dict_dir_path)  # 加载课程实体词词典
        self.stopwords = []  # 用于存储停用词
        self.vocabulary = self.load_vocabulary()  # 加载词表，存储每个特征词和对应的下标
        self.model = self.load_classifier_model()  # 模型训练之后，可直接用于预测

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
                        if term.word in train_list or term.word in self.stopwords or term.word ==' ':  # 防止数据重复
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

    # 构建并训练朴素贝叶斯模型
    def load_classifier_model(self):
        model = GaussianNB()  # 构建朴素贝叶斯模型
        train_list = []  # 定义一个空列表，用于存放训练数据
        data = np.array([])  # 存放训练数据的特征
        target = np.array([])  # 存放标签
        for file in os.listdir(detailed_questions_dir_path):  # 遍历detailed_questions/目录下的详细问题文件
            file_path = os.path.join(detailed_questions_dir_path, file)  # 详细问题文件的绝对路径
            if os.path.isdir(file_path):  # 若file_path指定的是目录，则跳出本次循环
                continue
            for line in helper.read_file(file_path):  # 读取详细问题文件，并逐行遍历
                index = file_path.split('】')[0].split('【')[1]  # 去除文件名中的'】'和'【'，提取出是第几号文件如：【0】课程介绍.txt，index值为0
                array = self.sentence_to_array(line.strip())  # 调用sentence_to_array方法，将每个问题转换成数组
                if len(data) == 0:  # 如果存放数据的数组为空
                    data = np.array(np.array([array]))  # 将问题数组转换为array格式
                    target = np.array(int(index))  # 将index作为标签，并转换成array格式
                else:
                    data = np.append(data, np.array([array]), axis=0)  # 以新的一行添加数据
                    target = np.append(target, np.array([int(index)]))  # 添加标签
        model.fit(data, target)  # 训练朴素贝叶斯模型
        path_savemodel = "model_for_NB/model.pickle"  # 模型保存的路径
        joblib.dump(model, path_savemodel)  # 保存训练好的模型
        return model

    # 计算准确率，评估模型的有效性
    def compute_accuracy(self):
        all_question_quantity = 0  # 初始化所有问题的数量
        correct_question_quantity = 0  # 初始化预测正确问题的数量
        for file in os.listdir(detailed_questions_dir_path):
            file_path = os.path.join(detailed_questions_dir_path, file)
            if os.path.isdir(file_path):
                continue
            for line in helper.read_file(file_path):
                index = file_path.split('】')[0].split('【')[1]
                array = self.sentence_to_array(line.strip())
                predict = self.model.predict([array])
                if predict[0] == int(index):
                    correct_question_quantity += 1  # 预测正确问题的数量累加
                all_question_quantity += 1  # 总问题数量累加
        return correct_question_quantity / all_question_quantity  # 计算准确率

if __name__ == '__main__':
        query_process = NBmodel()  # 实例化ModelProcess()类
        query_process.load_classifier_model()  # 训练朴素贝叶斯模型
        print("准确率为：" + str(query_process.compute_accuracy()))  # 评估模型