# -*- coding:utf-8 -*-
from py2neo import Graph
from setting import *


class Neo4j:
    def __init__(self):
        self.graph = Graph(neo4j_url, password=neo4j_password)  # 初始化图数据库的配置，包括neo4j的启动端口，neo4j的密码

    # 获取课程名为course_name的课程节点
    def get_course_node(self, course_name):
        query_sentence = 'match (c:Course) where c.name="%s" return c' % course_name  # Cypher语句，查询课程
        data1 = self.graph.run(query_sentence).data()  # 执行Cypher语句
        if len(data1) == 0:  # 若查询结果为空，返回None
            return None
        return data1[0]['c']  # 返回所有的查询到的课程名称

    # 查询课程的先修课程
    def get_course_adv(self, course_name):  # 如果根据课程名称没有查询到课程，则返回None
        if not self.get_course_node(course_name):
            return None
        # 获取课程的先修课程
        query_sentence = 'match(cc:Course)-[relationship:StartWith *1..]->(advCourse:Course) ' \
                         'where cc.name="%s" return relationship' % course_name  # Cypher语句，查询与当前课程有“StartWith”关系的节点，返回关系开始节点和结束节点课程的信息
        query_result = self.graph.run(query_sentence).data()  # 执行查询

        courses = [course_name]  # 用于保存当前课程及其先修课程的名称
        index_relationships = []  # 用于保存“StartWith”关系开始和结束课程的索引
        for item in query_result:  # 遍历查询结果
            # 提取key'relationship'对应的value值
            relationships = item['relationship']  # 提取key'relationship'对应的value值
            for sub_relationship in relationships:  # 遍历关系信息
                start_node_name = sub_relationship.start_node['name']  # 关系开始节点，表示后修课程
                if start_node_name not in courses:  # 如果课程名称不在courses列表中
                    courses.append(start_node_name)  # 添加课程名称
                end_node_name = sub_relationship.end_node['name']  # 关系结束节点，表示先修课程
                if end_node_name not in courses:  # 如果先修课程名称不在courses列表中
                    courses.append(end_node_name)  # 添加先修课程名称
                index_relationship = (
                    courses.index(start_node_name),  # 后修课程在courses中的位置/索引
                    courses.index(end_node_name))  # 先修课程在courses中的位置/索引
                if index_relationship not in index_relationships:  # 如果该关系不在列表中
                    index_relationships.append(
                        index_relationship)  # 添加关系，eg.[(0, 1), (0, 2),……]，其中，0表示某课程在courses列表中的位置；1和2表示该课程的先修课程在courses列表中的位置
        # 返回eg.{'courses': ['算法分析与设计', '离散数学', '算法与数据结构', '软件工程专业导论', 'C语言程序设计'], 'index_relationships': [(0, 1), (0, 2), (2, 3), (2, 1), (2, 4), (4, 3), (0, 4)]}
        return {"courses": courses, "index_relationships": index_relationships}

    # 获取授课教师的姓名
    def get_course_teacher(self, course_name):
        if not self.get_course_node(course_name):  # 如果根据课程名称没有查询到课程，则返回None
            return None
        query_sentence = 'match(t:Teacher)-[r:Teach]->(c:Course) where c.name="%s" return t' % course_name  # Cypher语句，查询授课教师
        data1 = self.graph.run(query_sentence).data()  # 执行查询
        if not data1:  # 如果没有查询到，返回None
            return None
        return data1[0]['t']  # 返回授课教师的姓名
def main():
    neo4j = Neo4j()
    course_name = "算法分析与设计"
    print(neo4j.get_course_adv(course_name)) # 查询"算法分析与设计"的先修课程
    print(str(neo4j.get_course_teacher(course_name)).encode('utf-8').decode('unicode_escape')) # 查询"算法分析与设计"的授课老师

if __name__ == '__main__':
    main()

