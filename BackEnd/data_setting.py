import os
root_dir_path = os.path.join(os.getcwd(), 'data')
custom_data_dir_path = os.path.join(root_dir_path, 'custom_data')
dict_dir_path = os.path.join(custom_data_dir_path, 'dictionary')
course_dict_dir_path = os.path.join(dict_dir_path, 'course_dict.txt')
question_dir_path = os.path.join(custom_data_dir_path, 'question')
question_classification_dir_path = os.path.join(question_dir_path, 'question_classification.txt')
vocabulary_dir_path = os.path.join(question_dir_path, 'vocabulary.txt') # 词表文件，后续的任务中会自动在指定目录下创建
detailed_questions_dir_path = os.path.join(question_dir_path, 'detailed_questions')
stop_words_dir_path = os.path.join(root_dir_path, 'stopwords.txt')