# -*- coding: utf-8 -*-
from xml.dom import minidom as minidom # 使用xml文件需要导入xml.dom包
from py2neo import * #操作图数据库的工具包py2neo
from setting import *

def get_xml_text_node_value(node, name):
    return node.getElementsByTagName(name)[0].childNodes[0].data

def get_all_sub_element_node(node):
    for sub_node in node.childNodes: # 遍历node节点的所有子节点
        if sub_node.nodeType == minidom.Node.TEXT_NODE: # 如果子节点的类型为minidom.Node.TEXT_NODE，跳出本次循环
            continue
        yield sub_node # 获取node节点中所有非文本的元素

def save_all_course_info():
    dom = minidom.parse("data.xml") # 使用minidom.parse()方法，解析data.xml文件
    root = dom.documentElement # 获取xml文件对象
    courses_nodes = root.getElementsByTagName('courses') # 获取xml中'courses'节点的对象集合
    courses = []
    graph = Graph(neo4j_url, password=neo4j_password) # 连接neo4j数据库
    graph.delete_all() # 删除原有的所有子图
    # 创建所有课程节点
    for course_node in get_all_sub_element_node(courses_nodes[0]):
        # 获取课程名字，课程细节，id，英文名等信息
        course = {
            'name': get_xml_text_node_value(course_node, 'name'),
            'details': get_xml_text_node_value(course_node, 'details'),
            'id': get_xml_text_node_value(course_node, 'id'),
            'english_name': get_xml_text_node_value(course_node, 'english_name'),
            'credit': get_xml_text_node_value(course_node, 'credit'),
            'credit_hour': get_xml_text_node_value(course_node, 'credit_hour'),
            'optional': get_xml_text_node_value(course_node, 'optional'),
            'semester': get_xml_text_node_value(course_node, 'semester'),
        }

        teacher_name = get_xml_text_node_value(course_node, 'teacher') # 获取教师节点的文本
        matcher = NodeMatcher(graph) # 创建一个节点查询器matcher
        teacher_node = matcher.match('Teacher', name=teacher_name).first() # 按照教师名查询所有节点，返回的节点结果放置在teacher_node中
        if not teacher_node: # 如果不存在教师节点，则在图数据库中创建教师节点
            teacher_node = Node('Teacher')
            teacher_node.update({'name': teacher_name})
            graph.create(teacher_node)
        # 创建课程节点，包含name、details、id……属性
        course_node = Node('Course')
        course_node.update(course)
        courses.append(course_node)
        graph.create(course_node)
         # 创建教师节点与课程节点之间的关系“Teach”
        relationship = Relationship(teacher_node, 'Teach', course_node)
        graph.create(relationship)
    # 创建创建课程和先修课程之间的关系“StartWith”
    adv_course_node = root.getElementsByTagName('adv-course')[0] # 获取xml中'adv-course'节点的对象集合
    for item_node in get_all_sub_element_node(adv_course_node): # 遍历'adv-course'标签的所有的<item> </item>中的内容
        adv = get_xml_text_node_value(item_node, 'adv') # 当前课程
        pre = get_xml_text_node_value(item_node, 'pre') # 先修课程
        relationship = Relationship(courses[int(adv)], "StartWith", courses[int(pre)]) # 创建课程和先修课程之间的关系“StartWith”
        graph.create(relationship)


if __name__ == '__main__':
    save_all_course_info()
