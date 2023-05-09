import re
import pdb
import sys
from collections import Counter
import copy
# token分类
TOKEN_STYLE = [
    'KEY_WORD', 'IDENTIFIER', 'DIGIT_CONSTANT',
    'OPERATOR', 'SEPARATOR', 'STRING_CONSTANT',
    'BOOL_CONSTANT'
]

# 具体化关键字、运算符、分隔符
DETAIL_TOKEN_STYLE = {
    'int': 'INT',
    'float': 'FLOAT',
    'string': 'STRING',
    'bool': 'BOOL',
    'func': 'FUNC',
    'for': 'FOR',
    'while': 'WHILE',
    'if': 'IF',
    'elif': 'ELIF',
    'else': 'ELSE',
    'return': 'RETURN',
    'break': 'BREAK',
    'continue': 'CONTINUE',
    '=': 'ASSIGN',
    '&': 'AND',
    '|': 'OR',
    '!': 'NOT',
    '^': 'XOR',
    '<': 'LT',
    '>': 'GT',
    '+': 'PLUS',
    '-': 'MINUS',
    '*': 'MUL',
    '/': 'DIV',
    '%': 'MOD',
    '~': 'SQUARE',
    '>=': 'GET',
    '<=': 'LET',
    '==': 'EQUAL',
    '++': 'SELF_PLUS',
    '--': 'SELF_MINUS',
    '!=': 'NEQUAL',
    '(': 'LL_BRACKET',
    ')': 'RL_BRACKET',
    '{': 'LB_BRACKET',
    '}': 'RB_BRACKET',
    ',': 'COMMA',
    '"': 'DOUBLE_QUOTE',
    ';': 'SEMICOLON',
}

# 关键字
keywords = [
    ['int', 'float', 'string', 'bool', 'func'],
    ['if', 'for', 'while', 'else','elif'],
    ['return'],
    ['break','continue']
]

# 运算符
operators = [
    '=', '&', '|', '!','^', '<', '>', '>=', '<=', '==', '!=', '+', '-', '*', '/', '%', '~', '++', '--',
]

child_operators = [['!', '++', '--'], ['+', '-', '*', '/',
                                   '%', '>', '<', '>=', '<=', '~', '!=', '==', '&', '|', '=','^']]
# 赋值 与或非 六种比较运算 加减乘除 取模 乘方(~)

# 内置函数
inside_function = ["printf", "readInt", "readFloat", "readString"]

# 分隔符
delimiters = ['(', ')', '{', '}', '[', ']', ',', '\"', ';']

# 程序文件名字
file_name = None

# 文件内容
content = None


# 程序异常
class ProgramError(Exception):
    def __init__(self,ErrorInfo):
        super().__init__(self) #初始化父类
        self.errorinfo=ErrorInfo
    def __str__(self):
        return self.errorinfo

class Token:
    def __init__(self, token_type, token_value, line_num):
        self.type = token_type
        self.value = token_value
        self.line = line_num

    def __str__(self):
        return f"Type: {self.type}, Value: {self.value}, Line: {self.line}"

# 定义一个词法分析器类
class Lexer:
    def __init__(self, file_name):
        global content
        with open(file_name, 'r') as f:
            content = f.read()
        self.tokens = []

    # 获取下一个字符
    def get_next_char(self):
        if len(content) > 0:
            return content[0]
        else:
            return None

    # 移动指针
    def move_pointer(self, step):
        global content
        content = content[step:]

    # 输出
    def print_log(self, token):
        if isinstance(token, list):
            for tk in token:
                print("行:"+str(tk.line)+" 类型:" +
                      str(tk.type)+" 值:"+str(tk.value))
        else:
            print("行:"+str(token.line)+" 类型:" +
                  str(token.type)+" 值:"+str(token.value))

    # 判断是否为关键字
    def is_keyword(self, word):
        for i in range(len(keywords)):
            if word in keywords[i]:
                return True
        return False
    # 判断是否为运算符
    def is_operator(self, char):
        return char in operators

    # 判断是否为分隔符
    def is_delimiter(self, char):
        return char in delimiters

    # 判断是否为空白字符
    def is_blank(self,char):
        global line_num
        if char == '\n':
            line_num += 1
            return True
        return (char == ' ' or
                char == '\t' or
                char == '\r')
    # 跳过空白字符
    def skip_blank(self):
        while content and self.is_blank(content[0]):
            self.move_pointer(1)
            
    # 获取下一个token
    def get_next_token(self):
        global content
        global line_num
        token_value = ''

        # 判断是否为关键字或标识符
        if content[0].isalpha() or content[0] == '_':
            while content[0].isalnum() or content[0] == '_':
                token_value += content[0]
                self.move_pointer(1)
            # 判断是否为关键字词组
            if self.is_keyword(token_value):
                token_type = DETAIL_TOKEN_STYLE[token_value]
            else:
                token_type = TOKEN_STYLE[1]
            # 布尔值设置为布尔类型
            if token_value == "True" or token_value == "False":
                token_type = TOKEN_STYLE[6]

        # 判断是否为数字常量
        elif content[0].isdigit():
            while content[0].isdigit() or content[0] == '.':
                token_value += content[0]
                self.move_pointer(1)
            token_type = TOKEN_STYLE[2]

        # 判断是否为运算符
        elif self.is_operator(content[0]):
            token_value += content[0]
            self.move_pointer(1)
            
            # 如果是++或--或==
            if (token_value == '+' or token_value == '-' or token_value == '=') and (token_value == content[0]):
                token_value += content[0]
                token_type = DETAIL_TOKEN_STYLE[token_value]
                self.move_pointer(1)
            # 如果是>=或<=
            elif (token_value == '>' or token_value == '<') and content[0] == '=':
                token_value += content[0]
                token_type = DETAIL_TOKEN_STYLE[token_value]
                self.move_pointer(1)
            # 如果是!=
            elif token_value == '!' and content[0] == '=':
                token_value += content[0]
                token_type = DETAIL_TOKEN_STYLE[token_value]
                self.move_pointer(1)
            else:
                token_type = DETAIL_TOKEN_STYLE[token_value]

        # 判断是否为分隔符
        elif self.is_delimiter(content[0]):
            token_value = ""
            if content[0] == '\"':
                token_value += content[0]
                self.move_pointer(1)
                try:
                    while content[0] != '\"':
                        token_value += content[0]
                        self.move_pointer(1)
                except:
                    print("无法找到右引号，请检查字符串定义是否正确 in line {}!".format(line_num))
                    raise ProgramError("无法找到右引号，请检查字符串定义是否正确 in line {}!".format(line_num))
                    
                token_value += content[0]
                self.move_pointer(1)
                token_type = TOKEN_STYLE[5]
                if '\"' in token_value[1:-1]:
                    print("字符串中暂不支持引号!")
                    raise ProgramError("字符串中暂不支持引号 in line {}!".format(line_num))
                    
            else:
                token_value += content[0]
                token_type = DETAIL_TOKEN_STYLE[token_value]
                self.move_pointer(1)

        # 无法识别的字符
        else:
            token_value += content[0]
            self.move_pointer(1)
            token_type = 'UNKNOWN'

        # 生成token
        token = Token(token_type, token_value, line_num)
        self.tokens.append(token)
        
        # 跳过空白字符等
        self.skip_blank()
        
        return token

    # 调用get_next_token函数获得整个文件的token
    def run(self,print_log_flag = False):
        global line_num
        line_num = 1
        Token_list = []
        self.skip_blank()
        while len(content) > 0:
            token = self.get_next_token()
            if print_log_flag:
                self.print_log(token)
            if isinstance(token, list):
                for tk in token:
                    Token_list.append(tk)
            else:
                Token_list.append(token)
        return Token_list

# 语法树节点
class SyntaxTreeNode(object):
    def __init__(self, value=None, _type=None, extra_info=None):
        self.value = value # 节点值
        self.type = _type  # token类型
        self.extra_info = extra_info  # token的额外信息：类型、关键字等
        self.father = None  # 父节点
        self.left = None  # 左树
        self.right = None  # 右树
        self.first_son = None  # 父节点的第一个子树
        self.line = None # 节点所在行数
        
    # 设置value
    def set_value(self, value):
        self.value = value

    # 设置type
    def set_type(self, _type):
        self.type = _type

    # 设置extra_info
    def set_extra_info(self, extra_info):
        self.extra_info = extra_info

    # 获取value
    def get_value(self):
        return self.value

    # 获取type
    def get_type(self):
        return self.type

    # 获取extra_info
    def get_extra_info(self):
        return self.extra_info

# 语法树
class SyntaxTree(object):
    def __init__(self):
        # 语法树的根节点
        self.root = None
        # 当前所遍历到的节点
        self.current = None

    # 设置根节点
    def set_root(self, root):
        self.root = root

    # 获取根节点
    def get_root(self):
        return self.root

    # 为父节点添加子节点的函数
    def add_child_node(self, new_node, father=None):
        # 如果没有指定父节点，则默认为当前节点
        if father is None:
            father = self.current
        new_node.father = father
        # 如果父节点没有子节点，则将新节点作为第一个子节点
        if father.first_son is None:
            father.first_son = new_node
        # 如果父节点已经有子节点，则将新节点添加到最后一个子节点的右边
        else:
            temp = father.first_son
            while temp.right is not None:
                temp = temp.right
            temp.right = new_node
            new_node.left = temp
            new_node.father = father
        # 将当前节点设置为新节点
        self.current = new_node

    # 交换相邻的两棵兄弟子树
    def switch(self, left, right):
        left_left = left.left
        right_right = right.right
        left.left = right
        left.right = right_right
        right.left = left_left
        right.right = left
        if left_left:
            left_left.right = right
        if right_right:
            right_right.left = left


class Parser(object):
    '''语法分析器'''
    def __init__(self, tokens):
        self.tokens = tokens
        if not tokens:
            print("build successfully!")
            
        # tokens下标
        self.index = 0
        # 最终生成的语法树
        self.tree = SyntaxTree()

    # 处理大括号里的部分
    def process_bracket(self, father_tree):
        self.index += 1
        sentence_tree = SyntaxTree()
        sentence_tree.current = sentence_tree.root = SyntaxTreeNode('Sentence')
        father_tree.add_child_node(sentence_tree.root, father_tree.root)
        while True:
            # 句型
            sentence_pattern = self.get_sentence_pattern()
            # 声明语句
            if sentence_pattern == 'STATEMENT':
                self.statement(sentence_tree.root)
            # 赋值语句
            elif sentence_pattern == 'ASSIGNMENT':
                self.assignment_statement(sentence_tree.root)
            # 初始化语句
            elif sentence_pattern == 'VARIABLE_INITIALIZATION':
                self.variable_initiazation(sentence_tree.root)
            # 函数调用
            elif sentence_pattern == 'FUNCTION_CALL':
                self.function_call_statement(sentence_tree.root)
            # 控制流语句
            elif sentence_pattern == 'CONTROL':
                self.control_statement(sentence_tree.root)
            # break语句
            elif sentence_pattern == 'BREAK':
                self.break_statement(sentence_tree.root)
            # continue语句 
            elif sentence_pattern == 'CONTINUE':
                self.continue_statement(sentence_tree.root)
            # return语句
            elif sentence_pattern == 'RETURN':
                self.return_statement(sentence_tree.root)
            # 自增或自减
            elif sentence_pattern == 'SELFPLUS' or sentence_pattern == 'SELFMINUS':
                self._self_process(sentence_pattern,sentence_tree.root)
            # 右大括号，函数结束
            elif sentence_pattern == 'RB_BRACKET':
                break
            else:
                print('遇到了错误的句型 in line {}!'.format(self.tokens[self.index].line))
                raise ProgramError('遇到了错误的句型 in line {}!').format(self.tokens[self.index].line)
                

    # 函数声明
    def function_statment(self, father=None):
        if not father:
            father = self.tree.root
        func_statement_tree = SyntaxTree()
        func_statement_tree.current = func_statement_tree.root = SyntaxTreeNode(
            'FunctionStatement')
        self.tree.add_child_node(func_statement_tree.root, father)
        # 函数声明循环判断
        flag = True
        while flag and self.index < len(self.tokens):
            # 如果是函数定义关键字
            if self.tokens[self.index].value in keywords[0]:
                if self.tokens[self.index].value != 'func':
                    print("函数关键字仅支持func!")
                    raise ProgramError('函数关键字仅支持func in line {}').format(self.tokens[self.index].line)
                    
                return_type = SyntaxTreeNode('Type')
                func_statement_tree.add_child_node(return_type)
                func_statement_tree.add_child_node(
                    SyntaxTreeNode(self.tokens[self.index].value, 'FIELD_TYPE', {'type': self.tokens[self.index].value}))
                self.index += 1
            # 如果是函数名
            elif self.tokens[self.index].type == 'IDENTIFIER':
                func_name = SyntaxTreeNode('FunctionName')
                func_statement_tree.add_child_node(
                    func_name, func_statement_tree.root)
                # extra_info
                func_statement_tree.add_child_node(
                    SyntaxTreeNode(self.tokens[self.index].value, 'IDENTIFIER', {'type': 'FUNCTION_NAME'}))
                self.index += 1
            # 如果是参数序列
            elif self.tokens[self.index].type == 'LL_BRACKET':
                params_list = SyntaxTreeNode('StateParameterList')
                func_statement_tree.add_child_node(
                    params_list, func_statement_tree.root)
                self.index += 1
                while self.tokens[self.index].type != 'RL_BRACKET':
                    if self.tokens[self.index].value in keywords[0]:
                        param = SyntaxTreeNode('Parameter')
                        func_statement_tree.add_child_node(param, params_list)
                        # extra_info
                        func_statement_tree.add_child_node(
                            SyntaxTreeNode(self.tokens[self.index].value, 'FIELD_TYPE', {'type': self.tokens[self.index].value}), param)
                        if self.tokens[self.index + 1].type == 'IDENTIFIER':
                            # if self.tokens[self.index+2].type == 'ASSIGN' and self.tokens[self.index+]
                            # extra_info
                            func_statement_tree.add_child_node(SyntaxTreeNode(self.tokens[self.index + 1].value, 'IDENTIFIER', {
                                                               'type': 'VARIABLE', 'variable_type': self.tokens[self.index].value}), param)
                            # 判断参数
                            double_next_token_type = self.tokens[self.index+2].type

                            # 参数定义结束
                            if double_next_token_type == 'RL_BRACKET':
                                self.index += 2
                                break
                            # 多参数定义
                            elif double_next_token_type == 'COMMA':
                                self.index += 2
                                continue
                            # 参数自带初始值
                            elif double_next_token_type == 'ASSIGN':
                                if self.tokens[self.index].value == 'string':
                                    func_statement_tree.add_child_node(
                                        SyntaxTreeNode(self.tokens[self.index+3].value, 'STRING_CONSTANT'), param)
                                elif self.tokens[self.index].value == 'int' or self.tokens[self.index].value == 'float':
                                    func_statement_tree.add_child_node(
                                        SyntaxTreeNode(self.tokens[self.index+3].value, '_Constant'), param)
                                elif self.tokens[self.index].value == 'bool':
                                    func_statement_tree.add_child_node(
                                        SyntaxTreeNode(self.tokens[self.index+3].value, 'BOOL_CONSTANT'), param)
                                self.index += 2
                                continue
                            else:
                                print("函数定义参数错误！参数之间须以分割符逗号进行分割！")
                                raise ProgramError("函数定义参数错误！参数之间须以分割符逗号进行分割 in line {}!".format(self.tokens[self.index].line))
                                
                        else:
                            print('函数定义参数错误!')
                            raise ProgramError("函数定义参数错误 in line {}!".format(self.tokens[self.index].line))
                            
                        self.index += 1
                    self.index += 1
                self.index += 1
            # 如果是遇见了左大括号
            elif self.tokens[self.index].type == 'LB_BRACKET':
                self.process_bracket(func_statement_tree)
                # 处理完函数体后，直接break
                break
            else:
                print("function statement error!")
                raise ProgramError('函数声明错误!')
                

    # 变量初始化语句：变量初始化只支持单个变量初始化，不支持混杂声明和初始化同时进行
    def variable_initiazation(self, father=None):
        if not father:
            father = self.tree.root
        variable_initialization_tree = SyntaxTree()
        variable_initialization_tree.current = variable_initialization_tree.root = SyntaxTreeNode(
            'VARIABLE_INITIALIZATION')
        self.tree.add_child_node(variable_initialization_tree.root, father)
        # 声明部分
        stat_father = variable_initialization_tree.root
        statement_tree = SyntaxTree()
        statement_tree.current = statement_tree.root = SyntaxTreeNode(
            'Statement')
        variable_initialization_tree.add_child_node(
            statement_tree.root, stat_father)
        while self.tokens[self.index].type != 'ASSIGN':  # 遇到赋值号则结束
            # 变量类型
            if self.tokens[self.index].value in keywords[0]:
                tmp_variable_type = self.tokens[self.index].value
                variable_type = SyntaxTreeNode('Type')
                statement_tree.add_child_node(variable_type)
                # extra_info
                statement_tree.add_child_node(
                    SyntaxTreeNode(self.tokens[self.index].value, 'FIELD_TYPE', {'type': self.tokens[self.index].value}))
            # 变量名
            elif self.tokens[self.index].type == 'IDENTIFIER':
                # extra_info
                statement_tree.add_child_node(SyntaxTreeNode(self.tokens[self.index].value, 'IDENTIFIER', {
                                              'type': 'VARIABLE', 'variable_type': tmp_variable_type}), statement_tree.root)
            self.index += 1
        # 赋值部分
        assign_father = variable_initialization_tree.root
        assign_tree = SyntaxTree()
        assign_tree.current = assign_tree.root = SyntaxTreeNode('Assignment')
        variable_initialization_tree.add_child_node(
            assign_tree.root, assign_father)
        self.index -= 1  # 声明部分进行完之后，当前index从赋值号开始，因此减去1回到变量名部分。
        while self.tokens[self.index].type != 'SEMICOLON':
            # 被赋值的变量
            if self.tokens[self.index].type == 'IDENTIFIER':
                assign_tree.add_child_node(
                    SyntaxTreeNode(self.tokens[self.index].value, 'IDENTIFIER'))
                self.index += 1
            elif self.tokens[self.index].type == 'ASSIGN':
                self.index += 1
                # 如果不是调用函数
                if self.tokens[self.index+1].type != 'LL_BRACKET':
                    self.expression_statement(assign_tree.root)
                else:
                    break
        self.index += 1

        # 函数调用部分
        if self.tokens[self.index].type == 'LL_BRACKET':
            func_call_father = assign_tree.root
            func_call_tree = SyntaxTree()
            func_call_tree.current = func_call_tree.root = SyntaxTreeNode(
                'FunctionCall')
            assign_tree.add_child_node(func_call_tree.root, func_call_father)
            self.index -= 1  # 当前index从函数名开始
            while self.tokens[self.index].type != 'SEMICOLON':
                # 函数名
                if self.tokens[self.index].type == 'IDENTIFIER':
                    func_call_tree.add_child_node(
                        SyntaxTreeNode(self.tokens[self.index].value, 'FUNCTION_NAME'))
                    func_name = self.tokens[self.index].value
                    line = self.tokens[self.index].line
                # 左小括号
                elif self.tokens[self.index].type == 'LL_BRACKET':
                    self.index += 1
                    params_list = SyntaxTreeNode('CallParameterList')
                    func_call_tree.add_child_node(
                        params_list, func_call_tree.root)
                    try:
                        while self.tokens[self.index].type != 'RL_BRACKET':
                            if self.tokens[self.index].type == 'IDENTIFIER' or self.tokens[self.index].type == 'DIGIT_CONSTANT' or self.tokens[self.index].type == 'STRING_CONSTANT':
                                func_call_tree.add_child_node(
                                    SyntaxTreeNode(self.tokens[self.index].value, self.tokens[self.index].type), params_list)
                            elif self.tokens[self.index].type == 'AND':
                                func_call_tree.add_child_node(
                                    SyntaxTreeNode(self.tokens[self.index].value, 'AND'), params_list)
                            self.index += 1
                    except:
                        print("函数调用缺少')'!")
                        raise ProgramError('函数{}调用缺少右括号 in line {}!').format(func_name,line)
                        
                else:
                    print('function call error!')
                    raise ProgramError('函数{}调用错误 in line {}!').format(func_name,line)
                    
                self.index += 1
            self.index += 1

    # 声明语句
    def statement(self, father=None):
        if not father:
            father = self.tree.root
        statement_tree = SyntaxTree()
        statement_tree.current = statement_tree.root = SyntaxTreeNode(
            'Statement')
        self.tree.add_child_node(statement_tree.root, father)
        # 暂时用来保存当前声明语句的类型，以便于识别多个变量的声明
        tmp_variable_type = None
        while self.tokens[self.index].type != 'SEMICOLON':
            # 变量类型
            if self.tokens[self.index].value in keywords[0]:
                tmp_variable_type = self.tokens[self.index].value
                variable_type = SyntaxTreeNode('Type')
                statement_tree.add_child_node(variable_type)
                # extra_info
                statement_tree.add_child_node(
                    SyntaxTreeNode(self.tokens[self.index].value, 'FIELD_TYPE', {'type': self.tokens[self.index].value}))
            # 变量名
            elif self.tokens[self.index].type == 'IDENTIFIER':
                # extra_info
                statement_tree.add_child_node(SyntaxTreeNode(self.tokens[self.index].value, 'IDENTIFIER', {
                                              'type': 'VARIABLE', 'variable_type': tmp_variable_type}), statement_tree.root)
            # 多个变量声明
            elif self.tokens[self.index].type == 'COMMA':
                while self.tokens[self.index].type != 'SEMICOLON':
                    if self.tokens[self.index].type == 'IDENTIFIER':
                        tree = SyntaxTree()
                        tree.current = tree.root = SyntaxTreeNode('Statement')
                        self.tree.add_child_node(tree.root, father)
                        # 类型
                        variable_type = SyntaxTreeNode('Type')
                        tree.add_child_node(variable_type)
                        # extra_info
                        # 类型
                        tree.add_child_node(
                            SyntaxTreeNode(tmp_variable_type, 'FIELD_TYPE', {'type': tmp_variable_type}))
                        # 变量名
                        tree.add_child_node(SyntaxTreeNode(self.tokens[self.index].value, 'IDENTIFIER', {
                                            'type': 'VARIABLE', 'variable_type': tmp_variable_type}), tree.root)
                    self.index += 1
                break
            self.index += 1
        self.index += 1

    # 赋值语句
    def assignment_statement(self, father=None):
        if not father:
            father = self.tree.root
        assign_tree = SyntaxTree()
        assign_tree.current = assign_tree.root = SyntaxTreeNode('Assignment')
        self.tree.add_child_node(assign_tree.root, father)
        # 常变量表达式部分
        while self.tokens[self.index].type != 'SEMICOLON':
            # 被赋值的变量
            if self.tokens[self.index].type == 'IDENTIFIER':
                assign_tree.add_child_node(
                    SyntaxTreeNode(self.tokens[self.index].value, 'IDENTIFIER'))
                self.index += 1
            elif self.tokens[self.index].type == 'ASSIGN':
                self.index += 1
                # 如果不是调用函数
                if self.tokens[self.index+1].type != 'LL_BRACKET':
                    self.expression_statement(assign_tree.root)
                else:
                    break
        self.index += 1

        # 函数调用部分
        if self.tokens[self.index].type == 'LL_BRACKET':
            func_call_father = assign_tree.root
            func_call_tree = SyntaxTree()
            func_call_tree.current = func_call_tree.root = SyntaxTreeNode(
                'FunctionCall')
            assign_tree.add_child_node(func_call_tree.root, func_call_father)
            self.index -= 1  # 当前index从函数名开始
            while self.tokens[self.index].type != 'SEMICOLON':
                # 函数名
                if self.tokens[self.index].type == 'IDENTIFIER':
                    func_call_tree.add_child_node(
                        SyntaxTreeNode(self.tokens[self.index].value, 'FUNCTION_NAME'))
                # 左小括号
                elif self.tokens[self.index].type == 'LL_BRACKET':
                    self.index += 1
                    params_list = SyntaxTreeNode('CallParameterList')
                    func_call_tree.add_child_node(
                        params_list, func_call_tree.root)
                    try:
                        while self.tokens[self.index].type != 'RL_BRACKET':
                            if self.tokens[self.index].type == 'IDENTIFIER' or self.tokens[self.index].type == 'DIGIT_CONSTANT' or self.tokens[self.index].type == 'STRING_CONSTANT':
                                func_call_tree.add_child_node(
                                    SyntaxTreeNode(self.tokens[self.index].value, self.tokens[self.index].type), params_list)
                                func_name = self.tokens[self.index].value
                                line = self.tokens[self.index].line
                            elif self.tokens[self.index].type == 'AND':
                                func_call_tree.add_child_node(
                                    SyntaxTreeNode(self.tokens[self.index].value, 'AND'), params_list)
                            self.index += 1
                    except:
                        print("函数调用缺少')'!")
                        raise ProgramError('函数{}调用缺少右括号 in line {}').format(func_name,line)
                        
                else:
                    print('function call error!')
                    raise ProgramError('函数{}调用错误 in line {}').format(func_name,line)
                    
                self.index += 1
            self.index += 1

    # while语句
    def while_statement(self, father=None):
        while_tree = SyntaxTree()
        while_tree.current = while_tree.root = SyntaxTreeNode(
            'Control', 'WhileControl')
        self.tree.add_child_node(while_tree.root, father)
        self.index += 1
        # 左小括号
        if self.tokens[self.index].type == 'LL_BRACKET':
            self.index += 1
            tmp_index = self.index
            while self.tokens[tmp_index].type != 'RL_BRACKET':
                tmp_index += 1
            self.expression_statement(while_tree.root, tmp_index)
            self.index += 1
        else:
            print('error: lack of left bracket!')
            raise ProgramError('while循环缺少左括号 in line {}').format(self.tokens[self.index].line)
            
        # 左大括号
        if self.tokens[self.index].type == 'LB_BRACKET':
            self.process_bracket(while_tree)

    # for语句
    def for_statement(self, father=None):
        for_tree = SyntaxTree()
        for_tree.current = for_tree.root = SyntaxTreeNode(
            'Control', 'ForControl')
        self.tree.add_child_node(for_tree.root, father)
        # 标记for语句是否结束
        while True:
            token_type = self.tokens[self.index].type
            # for标记
            if token_type == 'FOR':
                self.index += 1
            # 左小括号
            elif token_type == 'LL_BRACKET':
                self.index += 1
                # 首先找到右小括号的位置
                tmp_index = self.index
                while self.tokens[tmp_index].type != 'RL_BRACKET':
                    tmp_index += 1
                # for语句中的第一个分号前的部分
                # 如果是变量初始化
                if self.tokens[self.index].value in keywords[0]:
                    if self.tokens[self.index].value != 'func':
                        sentence_pattern = self.get_sentence_pattern()
                        if sentence_pattern != 'VARIABLE_INITIALIZATION':
                            print("错误的变量初始化方式：in line {}".format(
                                self.tokens[self.index].line))
                            raise ProgramError("错误的变量初始化方式：in line {}".format(
                                self.tokens[self.index].line))
                            
                        self.variable_initiazation(for_tree.root)
                    else:
                        print("错误的变量初始化类型：func in line {}".format(
                            self.tokens[self.index].line))
                        raise ProgramError("错误的变量初始化类型：func in line {}".format(
                            self.tokens[self.index].line))
                        
                        
                # 要么就是赋值
                else:
                    self.assignment_statement(for_tree.root)
                # 两个分号中间的部分
                self.expression_statement(for_tree.root)
                self.index += 1
                # 第二个分号后的部分
                self.expression_statement(for_tree.root, tmp_index)
                self.index += 1
            # 如果为左大括号
            elif token_type == 'LB_BRACKET':
                self.process_bracket(for_tree)
                break
        # 交换for语句下第三个子节点和第四个子节点
        current_node = for_tree.root.first_son.right.right
        next_node = current_node.right
        for_tree.switch(current_node, next_node)
    
    # break语句
    def break_statement(self,father=None):
        grand = father.father
        if not grand or grand.type !='ForControl' and grand.type !='WhileControl' and grand.father.type !='IfElseControl':
            print("错误的break语句使用地点，break语句仅支持在For和While循环体中使用!")
            raise ProgramError("错误的break语句使用地点，break语句仅支持在For和While循环体中使用 in line {}!".format(self.tokens[self.index].line))
        
        if grand.father.type =='IfElseControl':
            current_node = grand.father
            while current_node:
                if current_node.type != 'ForControl' and current_node.type != 'WhileControl':
                    current_node = current_node.father
                elif current_node.value == 'FunctionStatement':
                    current_node = None
                else:
                    break 
            if not current_node:
                raise ProgramError("错误的break语句使用地点，break语句仅支持在For和While循环体中使用 in line {}!".format(self.tokens[self.index].line))
        
        self.tree.add_child_node(SyntaxTreeNode('BREAK'),father)
        self.index += 1
        if self.tokens[self.index].type != 'SEMICOLON':
            print("缺少分号 in line {}".format(self.tokens[self.index-1].line))
            raise ProgramError("缺少分号 in line {}".format(self.tokens[self.index-1].line))
            
        self.index += 1
          
    # continue语句
    def continue_statement(self,father=None):
        grand = father.father
        if not grand or grand.type !='ForControl' and grand.type !='WhileControl' and grand.father.type !='IfElseControl':
            print("错误的break语句使用地点，break语句仅支持在For和While循环体中使用!")
            raise ProgramError("错误的break语句使用地点，break语句仅支持在For和While循环体中使用 in line {}!".format(self.tokens[self.index].line))
        
        if grand.father.type =='IfElseControl':
            current_node = grand.father
            while current_node:
                if current_node.type != 'ForControl' and current_node.type != 'WhileControl':
                    current_node = current_node.father
                elif current_node.value == 'FunctionStatement':
                    current_node = None
                else:
                    break 
            if not current_node:
                raise ProgramError("错误的break语句使用地点，break语句仅支持在For和While循环体中使用 in line {}!".format(self.tokens[self.index].line))
            
        self.tree.add_child_node(SyntaxTreeNode('CONTINUE'),father)
        self.index+=1
        if self.tokens[self.index].type != 'SEMICOLON':
            print("缺少分号 in line {}".format(self.tokens[self.index-1].line))
            raise ProgramError("缺少分号 in line {}".format(self.tokens[self.index-1].line))
            
        self.index += 1
        
    # if语句
    def ifelse_statement(self, father=None):
        if_else_tree = SyntaxTree()
        if_else_tree.current = if_else_tree.root = SyntaxTreeNode(
            'Control', 'IfElseControl')
        self.tree.add_child_node(if_else_tree.root, father)

        if_tree = SyntaxTree()
        if_tree.current = if_tree.root = SyntaxTreeNode('IfControl')
        if_else_tree.add_child_node(if_tree.root)
        
        # if标志
        if self.tokens[self.index].type == 'IF':
            self.index += 1
            # 左小括号
            if self.tokens[self.index].type == 'LL_BRACKET':
                self.index += 1
                # 右小括号位置
                tmp_index = self.index
                while not (self.tokens[tmp_index].type == 'RL_BRACKET' and self.tokens[tmp_index+1].type == 'LB_BRACKET'):
                    tmp_index += 1
                self.expression_statement(if_tree.root, tmp_index)
                self.index += 1
            else:
                print('error: lack of left bracket!')
                raise ProgramError("if语句缺少左括号 in line {}".format(self.tokens[self.index].line))
                

            # 左大括号
            if self.tokens[self.index].type == 'LB_BRACKET':
                self.process_bracket(if_tree)
        
        # 如果是elif关键字
        if self.tokens[self.index].type == 'ELIF':
            self.index += 1
            elif_tree = SyntaxTree()
            elif_tree.current = elif_tree.root = SyntaxTreeNode('ElifControl')
            if_else_tree.add_child_node(elif_tree.root,if_else_tree.root)
            
            if self.tokens[self.index].type == 'LL_BRACKET':
                self.index += 1
                # 右小括号位置
                tmp_index = self.index
                while not (self.tokens[tmp_index].type == 'RL_BRACKET' and self.tokens[tmp_index+1].type == 'LB_BRACKET'):
                    tmp_index += 1
                self.expression_statement(elif_tree.root, tmp_index)
                self.index += 1
            else:
                print('error: lack of left bracket!')
                raise ProgramError("elif语句缺少左括号 in line {}".format(self.tokens[self.index].line))
                

            # 左大括号
            if self.tokens[self.index].type == 'LB_BRACKET':
                self.process_bracket(elif_tree)
            
        # 如果是else关键字
        if self.tokens[self.index].type == 'ELSE':
            self.index += 1
            else_tree = SyntaxTree()
            else_tree.current = else_tree.root = SyntaxTreeNode('ElseControl')
            if_else_tree.add_child_node(else_tree.root, if_else_tree.root)
            # 左大括号
            if self.tokens[self.index].type == 'LB_BRACKET':
                self.process_bracket(else_tree)

    def control_statement(self, father=None):
        token_type = self.tokens[self.index].type
        if token_type == 'WHILE':
            self.while_statement(father)
        elif token_type == 'IF':
            self.ifelse_statement(father)
        elif token_type == 'FOR':
            self.for_statement(father)
        else:
            print('error: control style not supported!')
            raise ProgramError("控制语句类型不支持 in line {}!".format(self.tokens[self.index].line))
            
    
    # 自增或自减操作
    def _self_process(self,process_type,father=None):
        selftree = SyntaxTree()
        selftree.current = selftree.root = SyntaxTreeNode(
            'SELF',process_type)
        self.tree.add_child_node(selftree.root,father)
        self.expression_statement(selftree.root)
        self.index+=1
        
    # 表达式
    def expression_statement(self, father=None, index=None):
        if not father:
            father = self.tree.root
        # 运算符优先级 乘方最高
        operator_priority = {
            '+': 1,
            '-': 1,
            '*': 2,
            '/': 2,
            '%': 2,
            '~': 3,
            '>': 0,
            '>=': 0,
            '<': 0,
            '<=': 0,
            '==': 0,
            '!=': 0,
            '=':-3,
            '&': -1,
            '|': -2,
            '!': 3,
        }
        # 运算符栈
        operator_stack = []
        # 转换成的逆波兰表达式结果
        reverse_polishexpression_statement = []
        # 中缀表达式转为后缀表达式，即逆波兰表达式
        while self.tokens[self.index].type != 'SEMICOLON':
            if index and self.index >= index:
                break
            # 如果是常量
            if self.tokens[self.index].type == 'DIGIT_CONSTANT':
                tree = SyntaxTree()
                tree.current = tree.root = SyntaxTreeNode(
                    'Expression', 'Constant')
                tree.add_child_node(
                    SyntaxTreeNode(self.tokens[self.index].value, '_Constant'))
                reverse_polishexpression_statement.append(tree)
            elif self.tokens[self.index].type == 'BOOL_CONSTANT':
                tree = SyntaxTree()
                tree.current = tree.root = SyntaxTreeNode(
                    'Expression', 'Constant')
                tree.add_child_node(
                    SyntaxTreeNode(self.tokens[self.index].value, 'BOOL_CONSTANT'))
                reverse_polishexpression_statement.append(tree)
            # 如果是字符串常量
            if self.tokens[self.index].type == 'STRING_CONSTANT':
                tree = SyntaxTree()
                tree.current = tree.root = SyntaxTreeNode(
                    'Expression', 'Constant')
                tree.add_child_node(
                    SyntaxTreeNode(self.tokens[self.index].value, self.tokens[self.index].type))
                reverse_polishexpression_statement.append(tree)
            # 如果是变量
            elif self.tokens[self.index].type == 'IDENTIFIER':
                # 变量
                tree = SyntaxTree()
                tree.current = tree.root = SyntaxTreeNode(
                    'Expression', 'Variable')
                tree.add_child_node(
                    SyntaxTreeNode(self.tokens[self.index].value, '_Variable'))
                reverse_polishexpression_statement.append(tree)
            # 如果是运算符
            elif self.tokens[self.index].value in operators or self.tokens[self.index].type == 'LL_BRACKET' or self.tokens[self.index].type == 'RL_BRACKET':
                tree = SyntaxTree()
                tree.current = tree.root = SyntaxTreeNode(
                    'Operator', 'Operator')
                tree.add_child_node(
                    SyntaxTreeNode(self.tokens[self.index].value, '_Operator'))

                # 如果是左括号，直接压栈
                if self.tokens[self.index].type == 'LL_BRACKET':
                    operator_stack.append(tree)
                # 如果是右括号，弹栈直到遇到左括号为止
                elif self.tokens[self.index].type == 'RL_BRACKET':
                    while operator_stack and operator_stack[-1].current.value != '(':
                        reverse_polishexpression_statement.append(
                            operator_stack.pop())
                    # 将左括号弹出来
                    if operator_stack:
                        operator_stack.pop()
                # 其他只能是运算符
                else:
                    
                    while operator_stack and operator_stack[-1].current.value != '(' and operator_priority[tree.current.value] < operator_priority[operator_stack[-1].current.value]:
                        reverse_polishexpression_statement.append(
                            operator_stack.pop())
                    operator_stack.append(tree)
            self.index += 1
        
        # 最后将符号栈清空，最终得到逆波兰表达式reverse_polishexpression_statement
        while operator_stack:
            reverse_polishexpression_statement.append(operator_stack.pop())
    
        # 操作数栈
        operand_stack = []
        
        for item in reverse_polishexpression_statement:
            if item.root.type != 'Operator':
                operand_stack.append(item)
            else:
                # 处理运算符
                # 单目运算符
                if item.current.value in child_operators[0]:
                    a = operand_stack.pop()
                    new_tree = SyntaxTree()
                    
                    new_tree.current = new_tree.root = SyntaxTreeNode(
                        'Expression', 'SingleOperand',reverse_polishexpression_statement)
                    # 添加操作符
                    new_tree.add_child_node(item.root)
                    # 添加操作数
                    new_tree.add_child_node(a.root, new_tree.root)
                    operand_stack.append(new_tree)
                # 双目运算符
                elif item.current.value in child_operators[1]:
                    try:
                        b = operand_stack.pop()
                        a = operand_stack.pop()
                    except:
                        print("ERROR:请检查运算符{}是否具有两个操作数!".format(item.current.value))
                        raise ProgramError("请检查运算符{}是否具有两个操作数 in line {}!".format(item.current.value,self.tokens[self.index].line))
                        
                    new_tree = SyntaxTree()
                    new_tree.current = new_tree.root = SyntaxTreeNode(
                        'Expression', 'DoubleOperand',reverse_polishexpression_statement)
                    # 第一个操作数
                    new_tree.add_child_node(a.root)
                    # 操作符
                    new_tree.add_child_node(item.root, new_tree.root)
                    # 第二个操作数
                    new_tree.add_child_node(b.root, new_tree.root)
                    operand_stack.append(new_tree)
                else:
                    print('operator %s not supported!' % item.current.value)
                    raise ProgramError("运算符{}不支持 in line {}!".format(item.current.value,self.tokens[self.index].line))
                    
        self.tree.add_child_node(operand_stack[0].root, father)
    # 函数调用
    def function_call_statement(self, father=None):
        if not father:
            father = self.tree.root
        func_call_tree = SyntaxTree()
        func_call_tree.current = func_call_tree.root = SyntaxTreeNode(
            'FunctionCall')
        self.tree.add_child_node(func_call_tree.root, father)

        while self.tokens[self.index].type != 'SEMICOLON':
            # 函数名
            if self.tokens[self.index].type == 'IDENTIFIER':
                func_call_tree.add_child_node(
                    SyntaxTreeNode(self.tokens[self.index].value, 'FUNCTION_NAME'))
            # 左小括号
            elif self.tokens[self.index].type == 'LL_BRACKET':
                self.index += 1
                params_list = SyntaxTreeNode('CallParameterList')
                func_call_tree.add_child_node(params_list, func_call_tree.root)
                try:
                    while self.tokens[self.index].type != 'RL_BRACKET':
                        if self.tokens[self.index].type == 'IDENTIFIER' or self.tokens[self.index].type == 'DIGIT_CONSTANT' or self.tokens[self.index].type == 'STRING_CONSTANT':
                            func_call_tree.add_child_node(
                                SyntaxTreeNode(self.tokens[self.index].value, self.tokens[self.index].type), params_list)
                        elif self.tokens[self.index].type == 'AND':
                            func_call_tree.add_child_node(
                                SyntaxTreeNode(self.tokens[self.index].value, 'AND'), params_list)
                        self.index += 1
                except:
                    print("函数调用缺少')'!")
                    raise ProgramError("函数调用缺少右括号 in line {}!".format(self.tokens[self.index].line))
                    
            else:
                print('function call error!')
                raise ProgramError("函数调用错误 in line {}!".format(self.tokens[self.index].line))
                
            self.index += 1
        self.index += 1

    # return语句
    def return_statement(self, father=None):
        if not father:
            father = self.tree.root
        return_tree = SyntaxTree()
        return_tree.current = return_tree.root = SyntaxTreeNode('Return')
        self.tree.add_child_node(return_tree.root, father)
        while self.tokens[self.index].type != 'SEMICOLON':
            # 被赋值的变量
            if self.tokens[self.index].type == 'RETURN':
                return_tree.add_child_node(
                    SyntaxTreeNode(self.tokens[self.index].value))
                self.index += 1
            else:
                self.expression_statement(return_tree.root)
        self.index += 1

    # 根据一个句型的句首判断句型
    def get_sentence_pattern(self):
        token_value = self.tokens[self.index].value
        token_type = self.tokens[self.index].type
        # 控制句型
        if token_value in keywords[1]:
            return 'CONTROL'
        # 有可能是声明语句或者函数声明语句或者初始化语句

        elif token_value in keywords[0] and self.tokens[self.index + 1].type == 'IDENTIFIER':
            double_next_token_type = self.tokens[self.index + 2].type
            third_next_token_type = self.tokens[self.index + 3].type
            try:
                fourth_next_token_type = self.tokens[self.index + 4].type
            except: 
                fourth_next_token_type = None
            if double_next_token_type == 'LL_BRACKET':  # 左小括号，为函数声明
                return 'FUNCTION_STATEMENT'
            elif double_next_token_type == 'SEMICOLON' or double_next_token_type == 'COMMA':  # 分号或逗号，为变量声明
                return 'STATEMENT'
            elif double_next_token_type == "ASSIGN":  # 等号，为变量初始化
                # 不可用==进行变量初始化中的赋值
                if third_next_token_type == 'ASSIGN':
                    print("错误的初始化方式:==")
                    raise ProgramError("错误的初始化方式'==' in line {}!".format(self.tokens[self.index].line))
                    
                return 'VARIABLE_INITIALIZATION'
            else:
                return 'ERROR'
            
        # 可能为函数调用或者赋值语句或者表达式
        # TODO:完成表达式的识别，懒得做了
        elif token_type == 'IDENTIFIER' or token_type == 'OPERATOR': 
            next_token_type = self.tokens[self.index + 1].type
            if token_type == 'IDENTIFIER':
                if next_token_type == 'LL_BRACKET':
                    return 'FUNCTION_CALL'
                elif next_token_type == 'ASSIGN':
                    return 'ASSIGNMENT'
                else:
                    return 'ERROR'
        
        # break语句
        elif token_type == 'BREAK':
            return 'BREAK'
        # continue语句
        elif token_type == 'CONTINUE':
            return 'CONTINUE'
        # return语句
        elif token_type == 'RETURN':
            return 'RETURN'
        # 右大括号，表明函数的结束
        elif token_type == 'RB_BRACKET':
            self.index += 1
            return 'RB_BRACKET'
        else:
            return 'ERROR'

    # 主程序
    def main(self):
        # 根节点
        self.tree.current = self.tree.root = SyntaxTreeNode('Sentence')
        while self.index < len(self.tokens):
            # 句型
            sentence_pattern = self.get_sentence_pattern()
            # 函数声明语句
            if sentence_pattern == 'FUNCTION_STATEMENT':
                self.function_statment()
                continue
            # 声明语句
            elif sentence_pattern == 'STATEMENT':
                self.statement()
            # 函数调用
            elif sentence_pattern == 'FUNCTION_CALL':
                self.function_call_statement()
            else:
                print('main error!')
                raise ProgramError("主函数错误 in line {}!".format(self.tokens[self.index].line))
                

    # DFS遍历并可视化树结构
    def display(self, node, depth=0):
        if not node:
            return
        print('|   ' * depth, end='')
        print('|-- ', end='')
        print('( self: %s %s, father: %s, left: %s, right: %s )' % (node.value, node.type, node.father.value if node.father else None,
              node.left.value if node.left else None, node.right.value if node.right else None))
        child = node.first_son
        while child:
            self.display(child, depth+1)
            child = child.right

class Semantic(object):
    ''' 语义分析器 '''
    def __init__(self, ast):
        # 生成的语法树
        self.root = ast
        # 语法类型
        self.sentence_type = ['Sentence', 'FunctionStatement', 'VARIABLE_INITIALIZATION',
                              'Statement', 'FunctionCall', 'Assignment', 'Control', 'Expression', 'Return','BREAK','CONTINUE']
        # 表达式中的符号栈
        self.operator_stack = []
        # 表达式中的操作符栈
        self.operand_stack = []
        # 表达式栈，用于遍历表达式
        self.expres_stack = []
        # 最大递归深度
        self.max_recursion_depth = 1000
        # 递归栈
        self.recursion_stack = {}
        # 运算符优先级规则全局变量
        self.operator_priority = {
            '+': 1,
            '-': 1,
            '*': 2,
            '/': 2,
            '%': 2,
            '~': 3,
            '>': 0,
            '>=': 0,
            '<': 0,
            '<=': 0,
            '==': 0,
            '!=': 0,
            '&': -1,
            '|': -2,
            '!': 3
        }
        # 语法树节点栈
        self.ast_node_stack = []
        # 函数声明的语法树节点的字典
        self.function_statement_node_dict = {}
        # 记录函数声明初始化状态的字典
        self.function_init_status_dict = {} 
        # 函数返回值字典
        self.function_return_value_dict = {"main":None}
        # 函数调用标志字典
        self.function_call_flag = {}
        # 内置函数返回值变量
        self.inside_function_return_value_dict = {}
        # 符号字典：存储多个函数块作用域内的变量，初始默认含有main函数的变量字典
        self.symbol_dict = {'main': {}}
        # 符号表
        self.symbol_table = {}
        # 当前函数
        self.current_function = None
        # 主函数节点
        self.main_node = None
        # 语法树转列表-->暂时没用
        self.ast_node_stack.append(self.root)
        self.ast_to_stack(self.root)
        # 循环跳转标志(break,continue)
        self.loop_finish_flag = False
        # 预遍历所有函数
        self._pre_traverse(self.root)
        # 预编译后，当前函数设为main
        self.current_function = 'main'
        
    def ast_to_stack(self, node):
        if not node:
            return
        child = node.first_son
        while child:
            self.ast_node_stack.append(child)
            self.ast_to_stack(child)
            child = child.right
    
    # 函数定义句型
    def _function_statement(self, node=None):
        # 第一个儿子
        current_node = node.first_son
        # 暂存当前参数的类型、名字和值，以便识别多个参数
        tmp_parameter_type = None
        tmp_parameter_name = None
        tmp_parameter_value = None
        flag = 0  # 是否初始化，0为否，1为是，默认为否。
        while current_node:
            if current_node.value == 'FunctionName':
                if current_node.first_son.value != 'main':
                    if current_node.first_son.value in inside_function:
                        print("错误的函数命名：{}是内置函数!".format(current_node.first_son.value))
                        raise ProgramError("错误的函数命名：{}是内置函数!".format(current_node.first_son.value))
                        
                    func_name = current_node.first_son.value
                    self.current_function = func_name
                    self.symbol_table = {}  # 清空符号表
                    # 创建self.current_function函数名的符号表
                    self.symbol_dict[func_name] = {}
                    self.function_init_status_dict[func_name] = {}
                    # 临时节点1
                    tmp_node_1 = current_node.right  # StateParameterList
                    while tmp_node_1.value != 'Sentence':
                        if tmp_node_1.value == 'StateParameterList':
                            # 临时节点2
                            tmp_node_2 = tmp_node_1.first_son  # Parameter
                            # 遍历参数表中的所有参数
                            while tmp_node_2:
                                flag = 0
                                tmp_parameter_type = tmp_node_2.first_son.value
                                tmp_parameter_name = tmp_node_2.first_son.right.value
                                tmp_parameter_value = None
                                # 如果有值
                                try:
                                    tmp_parameter_value = tmp_node_2.first_son.right.right.value
                                    flag = 1
                                except:
                                    pass
                                self.symbol_table[tmp_parameter_name] = {
                                    'type': 'PARAMETER', 'field_type': tmp_parameter_type, 'value': tmp_parameter_value, 'init': flag}
                                tmp_node_2 = tmp_node_2.right

                            self.symbol_dict[func_name] = self.symbol_table
                        tmp_node_1 = tmp_node_1.right

                else:  # 如果是main函数
                    self.current_function = "main"
                    self.symbol_table = {}
                    self.symbol_dict['main'] = self.symbol_table
            elif current_node.value == 'Sentence':
                if self.current_function != "main":  # 调用函数直接从Sentence开始进入，不再进行参数定义
                    self.function_statement_node_dict[self.current_function] = {
                        'in_node': current_node.first_son, 'out_node': None}
                else:
                    self.main_node = current_node
                if current_node.first_son:
                    self._pre_traverse(current_node.first_son)
            current_node = current_node.right
    
    # 预扫描，将所有的函数声明加入符号表
    def _pre_traverse(self,node=None):
        self._pre_handler(node)
        next_node = node.right
        while next_node:
            self._pre_handler(next_node)
            next_node = next_node.right
    
    def _pre_handler(self,node=None):
        if not node:
            return
        if node.value in self.sentence_type:
            # 句型
            if node.value == 'Sentence':
                self._pre_traverse(node.first_son)
            # 函数声明
            if node.value == 'FunctionStatement':
                self._function_statement(node)
                
    # 简单的sizeof
    def _sizeof(self, _type):
        size = -1
        if _type == 'int' or _type == 'float' or _type == 'long':
            size = 4
        elif _type == 'char':
            size = 1
        elif _type == 'double':
            size = 8
        return str(size)
    
    # 字典统计归类，用于函数参数
    def classify_parameter_dict(self, original_dict):
        sorted_dict = {}
        for k, v in original_dict.items():
            # 如果值已经在结果字典中，则将当前键添加到值对应的列表中
            if v in sorted_dict:
                sorted_dict[v].append(k)
            # 如果值不在结果字典中，则创建一个新的键值对
            else:
                sorted_dict[v] = [k]
        return sorted_dict
    
    def is_constant(self,value):
        if isinstance(value,int) or isinstance(value, float):
            return True
        elif isinstance(value,str):
            return value[0] == '\"'
    
    def judge_type(self,value):
        if isinstance(value,bool):
            return "bool"
        if isinstance(value,int):
            return "int"
        elif isinstance(value,float):
            return "float"
        elif isinstance(value,str):
            if value[0]!='\"':
                return "IDENTIFIER"
            else:
                return "string"
        else:
            return "ERROR"
        
    def judge_constant_type(self, constant):
        if constant == 'string':
            return 'STRING_CONSTANT'
        elif constant == 'int' or constant == 'float':
            return 'DIGIT_CONSTANT'
        elif constant == 'bool':
            return 'BOOL_CONSTANT'
        else:
            return 'ERROR'
    
    def judge_constant_value_type(self,value):
        if isinstance(value,bool):
            return "BOOL_CONSTANT"
        elif isinstance(value,int) or isinstance(value,float):
            return "DIGIT_CONSTANT"
        elif isinstance(value,str):
            if value[0] =='\"':
                return "STRING_CONSTANT"
            else:
                return "NOT_CONSTANT"
        
    def extract_string(self,string):
        if string[0]!='\"':
            return string
        else:
            return string[1:-1]
            
    # 函数调用
    def _function_call(self, node=None):
        current_node = node.first_son
        func_name = None
        parameter_dict = {}
        # 存储变量名、类型和值的列表
        parameter_name_list = []
        parameter_type_list = []
        is_inside_flag = 0  # 是否为内建函数，0为否，1为是，默认为0
        
        # 拷贝符号表，用于最后复原函数内所有变量的状态
        copy_symbol_table = None
        # 首先是传参
        while current_node:
            # 函数名字
            if current_node.type == 'FUNCTION_NAME':
                func_name = current_node.value
                if func_name == 'main':
                    raise ProgramError("main函数不支持调用!")
                # 如果是内置函数
                if func_name in inside_function:
                    is_inside_flag = 1
                                         
                # 如果是自定义函数
                elif not copy_symbol_table and not is_inside_flag:
                    if func_name == self.current_function:
                        raise ProgramError("暂不支持递归调用!")

                    self.function_call_flag[func_name] = True
                    try:
                        copy_symbol_table = copy.deepcopy(self.symbol_dict[func_name])
                    except RecursionError:
                        raise ProgramError("递归层数已达到最大值:{},终止运行!".format(self.max_recursion_depth))

            # 函数参数
            elif current_node.value == 'CallParameterList':
                tmp_node = current_node.first_son
                while tmp_node:
                    # 是常数
                    if tmp_node.type == 'DIGIT_CONSTANT' or tmp_node.type == 'STRING_CONSTANT':
                        if tmp_node.type == 'STRING_CONSTANT':
                            parameter_name_list.append("{}".format(tmp_node.value))
                            parameter_type_list.append("string")
                        else: # DIGIT_CONSTANT
                            if "." in tmp_node.value:
                                parameter_name_list.append(float(tmp_node.value))
                                parameter_type_list.append("float")
                            else:
                                parameter_name_list.append(int(tmp_node.value))
                                parameter_type_list.append("int")
                        # parameter_list.append(label)
                    # 是某个变量
                    elif tmp_node.type == 'IDENTIFIER':
                        if tmp_node.value not in self.symbol_dict[self.current_function]:
                            raise ProgramError("变量{}尚未声明!".format(tmp_node.value))
                            
                        else:
                            if not self.symbol_dict[self.current_function][tmp_node.value]['init']:
                                print("变量{}尚未初始化!".format(tmp_node.value))
                                raise ProgramError("变量{}尚未初始化!".format(tmp_node.value))
                                
                        parameter_name_list.append(tmp_node.value)
                        parameter_type_list.append(self.symbol_dict[self.current_function][tmp_node.value]['field_type'])
                    else:
                        print(tmp_node.value)
                        print(tmp_node.type)
                        print('parameter type is not supported yet!')
                        raise ProgramError('parameter type is not supported yet!')

                    tmp_node = tmp_node.right
            current_node = current_node.right
        
        # 自定义函数
        if not is_inside_flag:
            # 检查参数数量和类型是否正确
            required_parameter_dict = {key: {'field_type': value.get('field_type'), 'init': value.get(
                'init')} for key, value in self.symbol_dict[func_name].items() if value.get('type') == 'PARAMETER'}
            num_params = len(required_parameter_dict)  # 定义参数数量
            num_args = len(parameter_name_list)  # 传入参数数量
            
            # 传入参数数小于定义参数数，就要考虑初始化的值了
            if num_args < num_params:
                # 如果所有参数都没有初始化，则说明少传参数了，直接退出程序
                if all(value.get('init') == 0 for value in required_parameter_dict.values()):
                    print("参数数量不一致：required {},but {} was given.".format(
                        num_params, num_args))
                    raise ProgramError("参数数量不一致：required {},but {} was given.".format(
                        num_params, num_args))
                    
                not_inited_parameter_dict = {
                    k: v['field_type'] for k, v in required_parameter_dict.items() if v['init'] == 0}
                num_not_inited_parameter = len(not_inited_parameter_dict)
                # 给定参数数量大于等于未初始化参数，但是又比函数的总参数量小，需要进一步考虑并按参数顺序赋值。
                if num_args >= num_not_inited_parameter:
                    if num_args == num_not_inited_parameter:
                        not_inited_parameter_type_list = list(not_inited_parameter_dict.values())
                        # 判断传入的参数和函数未初始化的参数的类型和顺序是否完全一致
                        if not_inited_parameter_type_list != parameter_type_list:
                            print("错误的函数参数，请检查类型和顺序是否一致!")
                            raise ProgramError("错误的函数参数，请检查类型和顺序是否一致!")

                        
                        not_inited_list = [k for k in not_inited_parameter_dict.keys()]
                        for param, var in zip(not_inited_list, parameter_name_list):
                            if self.is_constant(var):
                                self.symbol_dict[func_name][param]['value'] = var
                            else:
                                self.symbol_dict[func_name][param]['value'] = self.symbol_dict[self.current_function][var]['value']
                            self.symbol_dict[func_name][param]['init'] = 1
                    else:  # num_args > num_not_inited_parameter
                        cnt = 0  # 记录字典中的第cnt个值
                        # 临时符号表，等确认全部参数都被初始化后再赋给self.symbol_dict[func_name]
                        tmp_symbol_table = self.symbol_dict[func_name]
                        for k, p in required_parameter_dict.items():
                            current_var_name = parameter_name_list[cnt]
                            current_var_type = parameter_type_list[cnt]
                            if p['field_type'] == current_var_type:
                                required_parameter_dict[k]['init'] = 1
                                tmp_symbol_table[k]['init'] = 1
                                tmp_symbol_table[k]['value'] = self.symbol_dict[self.current_function][current_var_name]['value']
                                cnt += 1
                                continue
                            else:
                                if required_parameter_dict[k]['init'] != 1:
                                    print("错误的函数定义参数，请检查类型和顺序是否一致!")
                                    raise ProgramError("错误的函数定义参数，请检查类型和顺序是否一致!")

                                continue
                        # 有可能有问题：可能需要加个判断条件len(list(parameter_dict.keys())) == cnt
                        if not all(value.get('init') == 1 for value in required_parameter_dict.values()):
                            print("错误的函数定义参数，请检查类型和顺序是否一致!")
                            raise ProgramError("错误的函数定义参数，请检查类型和顺序是否一致!")
                        
                        self.symbol_dict[func_name] = tmp_symbol_table
                else:
                    print("参数数量不一致：required {},but {} was given.".format(
                        num_not_inited_parameter, num_args))
    
            # 传入参数数和定义参数数相等
            elif num_args == num_params:
                processed_required_parameter_dict = {
                    k: v['field_type'] for k, v in required_parameter_dict.items()}
                required_parameter_type_list = list(processed_required_parameter_dict.values())
                
                if required_parameter_type_list != parameter_type_list:
                    print("错误的函数参数，请检查类型和顺序是否一致!")
                    raise ProgramError("错误的函数参数，请检查类型和顺序是否一致!")

                required_list = [k for k in processed_required_parameter_dict.keys()]  
                for param, var in zip(required_list, parameter_name_list):
                    if self.is_constant(var):
                        self.symbol_dict[func_name][param]['value'] = var
                    else:
                        self.symbol_dict[func_name][param]['value'] = self.symbol_dict[self.current_function][var]['value']
                    self.symbol_dict[func_name][param]['init'] = 1
    
            # 传入参数数大于定义参数数
            else:  # num_args > num_params
                print("参数数量不一致：required {},but {} was given.".format(
                    num_params, num_args))
                raise ProgramError("参数数量不一致：required {},but {} was given.".format(
                    num_params, num_args))
                
            tmp_function = self.current_function
            self.current_function = func_name
            in_node = self.function_statement_node_dict[self.current_function]['in_node']
            out_node = self.function_statement_node_dict[self.current_function]['out_node']
            if in_node:  # 表示如果函数体内有代码
                self.traverse(in_node)
            # 调用完后，复原所有变量的值
            self.symbol_dict[self.current_function] = copy_symbol_table
            self.function_call_flag[self.current_function] = False
            self.current_function = tmp_function
            
        # 内置函数
        else:
            parameter_cnt = len(parameter_name_list)
            if parameter_cnt == 0:
                arg = None
            elif parameter_cnt > 1:
                print("参数数量不一致：required 1,but {} was given.".format(parameter_cnt))
                raise ProgramError("参数数量不一致：required 1,but {} was given.".format(parameter_cnt))
                
            else:
                arg = parameter_name_list[0]
            if self.inside_function_return_value_dict:
                self.inside_function_return_value_dict = {}
            if func_name == "printf":
                self.printf_function(arg)
            elif func_name == "readInt":
                self.inside_function_return_value_dict[self.readInt_function(arg)] = 'int'
            elif func_name == "readFloat":
                self.inside_function_return_value_dict[self.readFloat_function(arg)] = 'float'
            elif func_name == "readString":
                self.inside_function_return_value_dict[self.readString_function(arg)] = 'string'
            
    def printf_function(self,arg=None):
        if not arg:
            return
        arg_type = self.judge_type(arg)
        if arg_type == 'IDENTIFIER':
            if not self.symbol_dict[self.current_function][arg]['init']:
                print("变量{}尚未初始化!".format(arg))
                raise ProgramError("变量{}尚未初始化!".format(arg))
                
            arg_type = field_type = self.symbol_dict[self.current_function][arg]['field_type']
            arg = arg_value = self.symbol_dict[self.current_function][arg]['value']
            
        if arg_type == 'int' or arg_type == 'float':
            print(arg,end='')
        elif arg_type == 'string':
            extract_string = self.extract_string(arg)
            if '\\n' in extract_string:
                for string in extract_string.split('\\n')[:-1]:
                    print(string,end='')
                    print('\n',end='')
            else:
                print(extract_string,end='')
        elif arg_type == 'bool':
            print(arg,end='')
        else: # ERROR
            print("不受支持的参数类型 in function 'printf'")
            raise ProgramError("不受支持的参数类型 in function 'printf'")

    
    def readInt_function(self,arg=None):
        if arg == None:
            return_value = input("请输入一个整型数值：")
        else:
            arg_type = self.judge_type(arg)
            if arg_type == "IDENTIFIER":
                if not self.symbol_dict[self.current_function][arg]['init']:
                    print("变量{}尚未初始化!".format(arg))
                    raise ProgramError("变量{}尚未初始化!".format(arg))
                    
                arg_type = field_type = self.symbol_dict[self.current_function][arg]['field_type']
                arg = self.symbol_dict[self.current_function][arg]['value']
                
            if arg_type == "int" or arg_type == "float":
                print("错误的参数类型：required string but given {}.".format(arg_type))
                raise ProgramError("错误的参数类型：required string but given {}.".format(arg_type))
                
            elif arg_type == "string":
                extract_string = self.extract_string(arg)
                if '\\n' in extract_string:
                    for string in extract_string.split('\\n')[:-1]:
                        print(string,end='')
                        print('\n',end='')
                    return_value = input()
                else:
                    return_value = input(extract_string)
            else: # ERROR
                print("不受支持的参数类型 in function 'readInt'!")
                raise ProgramError("不受支持的参数类型 in function 'readInt'!")

        try:
            return int(return_value)
        except:
            print("错误的输入类型!请确保输入的是一个整型!")
            raise ProgramError("不受支持的参数类型 in function 'readInt'!")

    
    def readFloat_function(self,arg=None):
        if arg == None:
            return_value = input("请输入一个浮点型数值：")
        else:
            arg_type = self.judge_type(arg)
            if arg_type == "IDENTIFIER":
                if not self.symbol_dict[self.current_function][arg]['init']:
                    print("变量{}尚未初始化!".format(arg))
                    raise ProgramError("变量{}尚未初始化!".format(arg))
                    
                arg_type = field_type = self.symbol_dict[self.current_function][arg]['field_type']
                arg = self.symbol_dict[self.current_function][arg]['value']
                
            if arg_type == "int" or arg_type == "float":
                print("错误的参数类型：required string but given {}.".format(arg_type))
                raise ProgramError("错误的参数类型：required string but given {}.".format(arg_type))
                
            elif arg_type == "string":
                extract_string = self.extract_string(arg)
                if '\\n' in extract_string:
                    for string in extract_string.split('\\n')[:-1]:
                        print(string,end='')
                        print('\n',end='')
                    return_value = input()
                else:
                    return_value = input(extract_string)
            else: # ERROR
                print("不受支持的参数类型 in function 'readFloat'!")
                raise ProgramError("不受支持的参数类型 in function 'readFloat'!")

        try:
            return float(return_value)
        except:
            print("错误的输入类型!请确保输入的是一个浮点型!")
            raise ProgramError("错误的输入类型!请确保输入的是一个浮点型!")

    
    def readString_function(self,arg=None):
        if arg == None:
            return_value = input("请输入一个字符串型数值：")
        else:
            arg_type = self.judge_type(arg)
            if arg_type == "IDENTIFIER":
                if not self.symbol_dict[self.current_function][arg]['init']:
                    print("变量{}尚未初始化!".format(arg))
                    raise ProgramError("变量{}尚未初始化!".format(arg))
                    
                arg_type = field_type = self.symbol_dict[self.current_function][arg]['field_type']
                arg = self.symbol_dict[self.current_function][arg]['value']
                
            if arg_type == "int" or arg_type == "float":
                print("错误的参数类型：required string but given {}.".format(arg_type))
                raise ProgramError("错误的参数类型：required string but given {}.".format(arg_type))
                
            elif arg_type == "string":
                extract_string = self.extract_string(arg)
                if '\\n' in extract_string:
                    for string in extract_string.split('\\n')[:-1]:
                        print(string,end='')
                        print('\n',end='')
                    return_value = input()
                else:
                    return_value = input(extract_string)
            else: # ERROR
                print("不受支持的参数类型 in function 'readString'!")
                raise ProgramError("不受支持的参数类型 in function 'readString'!")
                
        try:
            return str(return_value)
        except:
            print("错误的输入类型!请确保输入的是一个字符串型!")
            raise ProgramError( "错误的输入类型!请确保输入的是一个字符串型!")
            
    
    # 声明语句
    def _statement(self, node=None):
        if self.current_function!='main':
            if self.current_function not in self.function_call_flag or not self.function_call_flag[self.current_function]:
                return
        # 1:初始化的，0:没有初始化
        flag = 0
        # 变量数据类型
        variable_field_type = None
        # 变量类型，是数组还是单个变量
        variable_type = None
        # 变量名
        variable_name = None
        current_node = node.first_son
        while current_node:
            # 类型
            if current_node.value == 'Type':
                variable_field_type = current_node.first_son.value
            # 变量名
            elif current_node.type == 'IDENTIFIER':
                variable_name = current_node.value
                variable_type = current_node.extra_info['type']
            # 数组元素
            elif current_node.value == 'ConstantList':
                tmp_node = current_node.first_son
                # 保存该数组
                array = []
                while tmp_node:
                    array.append(tmp_node.value)
                    tmp_node = tmp_node.right
            current_node = current_node.right
        # 将该变量存入符号表
        self.symbol_table[variable_name] = {
            'type': variable_type, 'field_type': variable_field_type, 'init': flag, 'value': None}
        self.symbol_dict[self.current_function] = self.symbol_table
    
    # 赋值语句
    def _assignment(self, node=None):
        if self.current_function!='main':
            if self.current_function not in self.function_call_flag or not self.function_call_flag[self.current_function]:
                return
        current_node = node.first_son
        if current_node.type != 'IDENTIFIER':
            print("赋值表达式右侧必须是一个标志符!")
            raise ProgramError("赋值表达式右侧必须是一个标志符!")

        if current_node.right.value != 'Expression' and current_node.right.value != 'FunctionCall':
            print("不支持的赋值类型:{}".format(current_node.right.value))
            raise ProgramError("不支持的赋值类型:{}".format(current_node.right.value))
            

        # 首先判断该变量是否已进行过声明
        if current_node.value not in self.symbol_table:
            print("变量{}尚未声明!".format(current_node.value))
            raise ProgramError("变量{}尚未声明!".format(current_node.value))
            

        # 如果右子树是常量表达式
        if current_node.right.value == 'Expression':
            expres = self._expression(current_node.right)
            # 首先判断该变量是否已进行过声明
            if current_node.value not in self.symbol_table:
                print("变量{}未声明!".format(current_node.value))
                raise ProgramError("变量{}未声明!".format(current_node.value))
                
            # 该变量的类型
            field_type = self.symbol_table[current_node.value]['field_type']
            # 继续判断：赋值号左右两边类型是否一致？
            field_constant_type = self.judge_constant_type(field_type)
            if expres['type'] == 'DIGIT_CONSTANT' or expres['type'] == 'STRING_CONSTANT' or expres['type'] == 'BOOL_CONSTANT':
                if field_constant_type != expres['type']:
                    raise ProgramError("错误的赋值类型:{}!".format(expres['type']))
                    
                # 判断完成后，进行解释执行操作：
                if field_type == 'int':
                    # 通过四舍五入规则将右边强制转换为int并赋值
                    self.symbol_table[current_node.value]['value'] = round(float(expres['value']))
                elif field_type == 'float':
                    # 直接转浮点即可
                    self.symbol_table[current_node.value]['value'] = float(expres['value'])
                elif field_type == 'string':
                    self.symbol_table[current_node.value]['value'] = expres['value']
                elif field_type == 'bool':
                    if expres['value'] == 'True':
                        self.symbol_table[current_node.value]['value'] = True
                    elif expres['value'] == 'False':
                        self.symbol_table[current_node.value]['value'] = False
                        
                flag = 1
                self.symbol_table[current_node.value]['init'] = flag
            # 如果是变量赋值
            elif expres['type'] == 'VARIABLE':
                var = expres['value']
                var_field_type = self.symbol_table[var]['field_type']
                var_constant_type = self.judge_constant_type(var_field_type)
                # 如果是函数体定义的变量
                if self.symbol_table[var]['type'] == 'VARIABLE':
                    if self.symbol_table[var]['init'] == 0:
                        raise ProgramError("变量{}未初始化，无法赋值!".format(var))
                        
                    else:
                        # 如果变量值的常数类型不一致
                        if field_constant_type != var_constant_type:
                            print("变量{}和{}值类型不一致，无法赋值！".format(
                                current_node.value, var))
                            raise ProgramError("变量{}和{}值类型不一致，无法赋值！".format(
                                current_node.value, var))
                            
                        # 同理
                        if field_type == 'int':
                            self.symbol_table[current_node.value]['value'] = round(float(self.symbol_table[expres['value']]['value']))
                        elif field_type == 'float':
                            self.symbol_table[current_node.value]['value'] = float(self.symbol_table[expres['value']]['value'])
                        elif field_type == 'string':
                            self.symbol_table[current_node.value]['value'] = self.symbol_table[expres['value']]['value']
                        elif field_type == 'bool':
                            if expres['value'] == 'True':
                                self.symbol_table[current_node.value]['value'] = True
                            elif expres['value'] == 'False':
                                self.symbol_table[current_node.value]['value'] = False
                                
                        flag = 1
                        self.symbol_table[current_node.value]['init'] = flag
                # 如果是函数头定义的参数
                elif self.symbol_table[var]['type'] == 'PARAMETER':
                    if field_constant_type != var_constant_type:
                        print("变量{}和{}值类型不一致，无法赋值！".format(
                            current_node.value, var))
                        raise ProgramError("变量{}和{}值类型不一致，无法赋值！".format(
                            current_node.value, var))
                        
                    # 如果有未初始化的参数，说明函数尚未被调用，赋值操作直接略过
                    if self.symbol_table[var]['init'] == 0:
                        pass
                    else:
                        if field_type == 'int':
                            self.symbol_table[current_node.value]['value'] = round(float(self.symbol_table[expres['value']]['value']))
                        elif field_type == 'float':
                            self.symbol_table[current_node.value]['value'] = float(self.symbol_table[expres['value']]['value'])
                        elif field_type == 'string':
                            self.symbol_table[current_node.value]['value'] = self.symbol_table[expres['value']]['value']
                        elif field_type == 'bool':
                            if expres['value'] == 'True':
                                self.symbol_table[current_node.value]['value'] = True
                            elif expres['value'] == 'False':
                                self.symbol_table[current_node.value]['value'] = False
                        flag = 1
                        self.symbol_table[current_node.value]['init'] = flag
                self.symbol_dict[self.current_function] = self.symbol_table
                
            else:
                print("不支持的赋值类型:{}".format(expres['type']))
                raise ProgramError("不支持的赋值类型:{}".format(expres['type']))
                
            
        # 如果右子树是函数调用
        else:
            tmp_symbol_table = self.symbol_table
            self._function_call(current_node.right)
            self.symbol_table = tmp_symbol_table
            func_name = current_node.right.first_son.value
            if func_name not in inside_function:
                # 如果有返回值
                return_value = self.function_return_value_dict[func_name]
                var_field_type = current_node.father.left.first_son.first_son.value # field_type
                if return_value != None:
                    return_value_type = self.judge_constant_value_type(return_value)
                    var_value_type = self.judge_constant_type(var_field_type)
                    if return_value_type != var_value_type:
                        print("变量 {} 的常数类型: {} 和函数 {} 的返回值常数类型 {} 不一致!".format(current_node.value,var_value_type,func_name,return_value_type))
                        raise ProgramError("变量 {} 的常数类型: {} 和函数 {} 的返回值常数类型 {} 不一致!".format(current_node.value,var_value_type,func_name,return_value_type))
                        
                    if var_field_type == 'int':
                        self.symbol_table[current_node.value]['value'] = round(float(return_value))
                    elif var_field_type == 'float':
                        self.symbol_table[current_node.value]['value'] = float(return_value)
                    elif var_field_type == 'string':
                        self.symbol_table[current_node.value]['value'] = return_value
                    elif var_field_type == 'bool':
                        if return_value == 'True':
                            self.symbol_table[current_node.value]['value'] = True
                        elif return_value == 'False':
                            self.symbol_table[current_node.value]['value'] = False
                    
                    flag = 1
    
                    self.symbol_table[current_node.value]['init'] = flag
                    self.symbol_dict[self.current_function] = self.symbol_table
    
                else:
                    print("无返回值的函数无法用于变量初始化!函数名:{}".format(self.current_function))
                    raise ProgramError("无返回值的函数无法用于变量初始化!函数名:{}".format(self.current_function))
                    
            else:
                return_value = list(self.inside_function_return_value_dict.keys())[0]
                return_type = self.judge_constant_type(self.inside_function_return_value_dict[return_value])
                var_field_type = self.symbol_dict[self.current_function][current_node.value]['field_type']
                var_type = self.judge_constant_type(var_field_type)
                
                if return_type != var_type:
                    print("变量 {} 的常数类型: {} 和函数 {} 的返回值常数类型 {} 不一致!".format(current_node.value,var_type,func_name,return_type))
                    raise ProgramError("变量 {} 的常数类型: {} 和函数 {} 的返回值常数类型 {} 不一致!".format(current_node.value,var_type,func_name,return_type))
                    
                    
                if var_field_type == 'int':
                    self.symbol_table[current_node.value]['value'] = round(float(return_value))
                elif var_field_type == 'float':
                    self.symbol_table[current_node.value]['value'] = float(return_value)
                elif var_field_type == 'string':
                    self.symbol_table[current_node.value]['value'] = return_value
                elif var_field_type == 'bool':
                    if return_value == 'True':
                        self.symbol_table[current_node.value]['value'] = True
                    elif return_value == 'bool':
                        self.symbol_table[current_node.value]['value'] = False
                        
                flag = 1
                self.symbol_table[current_node.value]['init'] = flag
                self.symbol_dict[self.current_function] = self.symbol_table

    # 变量初始化语句（声明+赋值）
    def _variable_initialization(self, node=None):
        if self.current_function!='main':
            if self.current_function not in self.function_call_flag or not self.function_call_flag[self.current_function]:
                return
        # 变量声明部分      
        # 初始化标志，默认为0
        flag = 0
        # 变量数据类型
        variable_field_type = None
        # 变量类型，是数组还是单个变量
        variable_type = None
        # 变量名
        variable_name = None
        current_node = node.first_son
        while current_node:
            # 类型
            if current_node.value == 'Type':
                variable_field_type = current_node.first_son.value
                current_node = current_node.right
                continue
            # 变量名
            elif current_node.type == 'IDENTIFIER':
                variable_name = current_node.value
                variable_type = current_node.extra_info['type']
                if variable_name in [param for param,value in self.symbol_dict[self.current_function].items() if value.get('type') == 'PARAMETER']:
                    print("暂不支持在函数内声明与函数参数同名的变量：{} {}".format(variable_field_type,variable_name))
                    raise ProgramError("暂不支持在函数内声明与函数参数同名的变量：{} {}".format(variable_field_type,variable_name))
                    
            # 数组元素
            elif current_node.value == 'ConstantList':
                tmp_node = current_node.first_son
                # 保存该数组
                array = []
                while tmp_node:
                    array.append(tmp_node.value)
                    tmp_node = tmp_node.right
            current_node = current_node.first_son
        
        self.symbol_table = self.symbol_dict[self.current_function]
        # 将该变量存入符号表
        self.symbol_table[variable_name] = {
            'type': variable_type, 'field_type': variable_field_type, 'init': flag, 'value': None}

        # 变量赋值部分
        current_node = node.first_son.right.first_son
        if current_node.right.value != 'Expression' and current_node.right.value != 'FunctionCall':
            print("assignment wrong in variable initialzation.")
            raise ProgramError("变量初始化中的赋值错误!")

        # 如果右子树是常量表达式
        if current_node.right.value == 'Expression':
            expres = self._expression(current_node.right)
            # 首先判断该变量是否已进行过声明
            if current_node.value not in self.symbol_table:
                print("变量{}未声明!".format(current_node.value))
                raise ProgramError("变量{}未声明!".format(current_node.value))
                
            # 该变量的类型
            field_type = self.symbol_table[current_node.value]['field_type']
            # 继续判断：赋值号左右两边类型是否一致？
            field_constant_type = self.judge_constant_type(field_type)
            if expres['type'] == 'DIGIT_CONSTANT' or expres['type'] == 'STRING_CONSTANT' or expres['type'] == 'BOOL_CONSTANT':
                if field_constant_type != expres['type']:
                    raise ProgramError("错误的赋值类型:{}!".format(expres['type']))
                    
                # 判断完成后，进行解释执行操作：
                if field_type == 'int':
                    # 通过四舍五入规则将右边强制转换为int并赋值
                    self.symbol_table[current_node.value]['value'] = round(float(expres['value']))
                elif field_type == 'float':
                    # 直接转浮点即可
                    self.symbol_table[current_node.value]['value'] = float(expres['value'])
                elif field_type == 'string':
                    self.symbol_table[current_node.value]['value'] = expres['value']
                elif field_type == 'bool':
                    self.symbol_table[current_node.value]['value'] = expres['value']
                        
                flag = 1
                self.symbol_table[current_node.value]['init'] = flag
            # 如果是变量赋值
            elif expres['type'] == 'VARIABLE':
                var = expres['value']
                var_field_type = self.symbol_table[var]['field_type']
                var_constant_type = self.judge_constant_type(var_field_type)
                # 如果是函数体定义的变量
                if self.symbol_table[var]['type'] == 'VARIABLE':
                    if self.symbol_table[var]['init'] == 0:
                        raise ProgramError("变量{}未初始化，无法赋值!".format(var))
                        
                    else:
                        # 如果变量值的常数类型不一致
                        if field_constant_type != var_constant_type:
                            print("变量{}和{}值类型不一致，无法赋值！".format(
                                current_node.value, var))
                            raise ProgramError("变量{}和{}值类型不一致，无法赋值！".format(
                                current_node.value, var))
                            
                        # 同理
                        if field_type == 'int':
                            self.symbol_table[current_node.value]['value'] = round(float(self.symbol_table[expres['value']]['value']))
                        elif field_type == 'float':
                            self.symbol_table[current_node.value]['value'] = float(self.symbol_table[expres['value']]['value'])
                        elif field_type == 'string':
                            self.symbol_table[current_node.value]['value'] = self.symbol_table[expres['value']]['value']
                        elif field_type == 'bool':
                            self.symbol_table[current_node.value]['value'] = expres['value']
                                
                        flag = 1
                        self.symbol_table[current_node.value]['init'] = flag
                # 如果是函数头定义的参数
                elif self.symbol_table[var]['type'] == 'PARAMETER':
                    if field_constant_type != var_constant_type:
                        print("变量{}和{}值类型不一致，无法赋值！".format(
                            current_node.value, var))
                        raise ProgramError("变量{}和{}值类型不一致，无法赋值！".format(
                            current_node.value, var))
                        
                    # 如果有未初始化的参数，说明函数尚未被调用，赋值操作直接略过
                    if self.symbol_table[var]['init'] == 0:
                        pass
                    else:
                        if field_type == 'int':
                            self.symbol_table[current_node.value]['value'] = round(float(self.symbol_table[expres['value']]['value']))
                        elif field_type == 'float':
                            self.symbol_table[current_node.value]['value'] = float(self.symbol_table[expres['value']]['value'])
                        elif field_type == 'string':
                            self.symbol_table[current_node.value]['value'] = self.symbol_table[expres['value']]['value']
                        elif field_type == 'bool':
                            self.symbol_table[current_node.value]['value'] = expres['value']
                        flag = 1
                        self.symbol_table[current_node.value]['init'] = flag
                self.symbol_dict[self.current_function] = self.symbol_table
                
            else:
                print("不支持的赋值类型:{}".format(expres['type']))
                raise ProgramError("不支持的赋值类型:{}".format(expres['type']))
                
            
        # 如果右子树是函数调用
        else:
            tmp_symbol_table = self.symbol_table
            self._function_call(current_node.right)
            self.symbol_table = tmp_symbol_table
            func_name = current_node.right.first_son.value
            if func_name not in inside_function:
                # 如果有返回值
                return_value = self.function_return_value_dict[func_name]
                var_field_type = current_node.father.left.first_son.first_son.value # field_type
                if return_value != None:
                    return_value_type = self.judge_constant_value_type(return_value)
                    var_value_type = self.judge_constant_type(var_field_type)
                    
                    if return_value_type != var_value_type:
                        print("变量 {} 的常数类型: {} 和函数 {} 的返回值常数类型 {} 不一致!".format(current_node.value,var_value_type,func_name,return_value_type))
                        raise ProgramError("变量 {} 的常数类型: {} 和函数 {} 的返回值常数类型 {} 不一致!".format(current_node.value,var_value_type,func_name,return_value_type))
                        
                    if var_field_type == 'int':
                        self.symbol_table[current_node.value]['value'] = round(float(return_value))
                    elif var_field_type == 'float':
                        self.symbol_table[current_node.value]['value'] = float(return_value)
                    elif var_field_type == 'string':
                        self.symbol_table[current_node.value]['value'] = return_value
                    elif var_field_type == 'bool':
                        self.symbol_table[current_node.value]['value'] = return_value
                    
                    flag = 1
    
                    self.symbol_table[current_node.value]['init'] = flag
                    self.symbol_dict[self.current_function] = self.symbol_table
    
                else:
                    print("无返回值的函数无法用于变量初始化!函数名:{}".format(self.current_function))
                    raise ProgramError("无返回值的函数无法用于变量初始化!函数名:{}".format(self.current_function))
                    
            else:
                return_value = list(self.inside_function_return_value_dict.keys())[0]
                return_type = self.judge_constant_type(self.inside_function_return_value_dict[return_value])
                var_field_type = self.symbol_dict[self.current_function][current_node.value]['field_type']
                var_type = self.judge_constant_type(var_field_type)
                
                if return_type != var_type:
                    print("变量 {} 的常数类型: {} 和函数 {} 的返回值常数类型 {} 不一致!".format(current_node.value,var_type,func_name,return_type))
                    raise ProgramError("变量 {} 的常数类型: {} 和函数 {} 的返回值常数类型 {} 不一致!".format(current_node.value,var_type,func_name,return_type))
                    
                    
                if var_field_type == 'int':
                    self.symbol_table[current_node.value]['value'] = round(float(return_value))
                elif var_field_type == 'float':
                    self.symbol_table[current_node.value]['value'] = float(return_value)
                elif var_field_type == 'string':
                    self.symbol_table[current_node.value]['value'] = return_value
                elif var_field_type == 'bool':
                    self.symbol_table[current_node.value]['value'] = return_value

                flag = 1
                self.symbol_table[current_node.value]['init'] = flag
                self.symbol_dict[self.current_function] = self.symbol_table
            
    # for语句
    def _control_for(self, node=None):
        if self.current_function!='main':
            if self.current_function not in self.function_call_flag or not self.function_call_flag[self.current_function]:
                return
        current_node = node.first_son
        # 遍历的是for循环中的那个部分
        cnt = 2
        loop_node = None
        while current_node:
            # for第一部分
            if current_node.value == 'Assignment':
                self._assignment(current_node)
            elif current_node.value == 'VARIABLE_INITIALIZATION':
                self._variable_initialization(current_node)
            # for第二、三部分
            elif current_node.value == 'Expression':
                # 第二部分
                if (cnt == 2):    
                    cnt += 1
                    # 表达式结果为False则跳出循环
                    result = self._calculate_expression(current_node)
                    if not result:
                        break
                # 第三部分
                else:
                    cnt = 2
                    self._expression(current_node.right.right)
                    continue
            # for语句部分
            elif current_node.value == 'Sentence':
                if not loop_node:
                    loop_node = current_node.left
                self.traverse(current_node.first_son)
                # 若已break
                if current_node.extra_info == 'break':
                    break
                current_node = loop_node
                continue
            current_node = current_node.right

    # if else语句
    def _control_if(self, node=None):
        if self.current_function!='main':
            if self.current_function not in self.function_call_flag or not self.function_call_flag[self.current_function]:
                return
        current_node = node.first_son
        executed_flag = False
        while current_node:
            if current_node.value == 'IfControl':
                if current_node.first_son.value != 'Expression' and current_node.first_son.right.value != 'Sentence':
                    print("if语句错误!")
                    raise ProgramError("if语句错误!")
   
                result = self._calculate_expression(current_node.first_son)
                if result:
                    executed_flag = True
                    self.traverse(current_node.first_son.right.first_son)
            
            elif current_node.value == 'ElifControl':
                if current_node.first_son.value != 'Expression' and current_node.first_son.right.value != 'Sentence':
                    print("elif语句错误!")
                    raise ProgramError("elif语句错误!")
   
                result = self._calculate_expression(current_node.first_son)
                if result:
                    executed_flag = True
                    self.traverse(current_node.first_son.right.first_son)
                    
            elif current_node.value == 'ElseControl':
                if not executed_flag:
                    self.traverse(current_node.first_son)
            current_node = current_node.right

    # while语句
    def _control_while(self, node=None):
        if self.current_function!='main':
            if self.current_function not in self.function_call_flag or not self.function_call_flag[self.current_function]:
                return
        current_node = node.first_son
        loop_node = None
        while current_node:
            if current_node.value == 'Expression':
                result = self._calculate_expression(current_node)
                if not result:
                    break
            elif current_node.value == 'Sentence':
                if not loop_node:
                    loop_node = current_node.left
                self.traverse(current_node.first_son)
                if current_node.extra_info == 'break':
                    self.loop_finish_flag = False
                    break
                elif current_node.extra_info == 'continue':
                    self.loop_finish_flag = False
                    
                current_node = loop_node
                continue
            current_node = current_node.right

    # return语句
    def _return(self, node=None):
        if self.current_function!='main':
            if self.current_function not in self.function_call_flag or not self.function_call_flag[self.current_function]:
                return
        current_node = node.first_son
        if not current_node or not current_node.right:
            print('return error!')
            raise ProgramError("return语句错误!")

        if current_node.value != 'return' or current_node.right.value != 'Expression':
            print('return error!')
            raise ProgramError("return语句错误!")
 
        else:
            current_node = current_node.right
            expres = self._expression(current_node)
            if expres['type'] == 'VARIABLE':
                if expres['type'] in self.symbol_dict and self.symbol_dict[self.current_function][expres['value']]['init'] == 1:
                    self.function_return_value_dict[self.current_function] = self.symbol_dict[self.current_function][expres['value']]['value']
                else:
                    raise ProgramError("返回变量{}不存在，或尚未初始化!".format(expres['value']))
            elif expres['type'] == 'DIGIT_CONSTANT' or expres['type'] == 'STRING_CONSTANT':
                self.function_return_value_dict[self.current_function] = str(expres['value'])
            elif expres['type'] == 'BOOL_CONSTANT':
                self.function_return_value_dict[self.current_function] = expres['value']
            else:
                print('return type not supported!')
                raise ProgramError("return类型不支持!")

    # break语句
    def _break(self,node=None):
        sentence_node = node.father
        
        # 说明这是在ifelse语句里的break
        if sentence_node.father.type != 'ForControl' and sentence_node.father.type != 'WhileControl':
            current_node = sentence_node.father
            # 找到break所属的循环体节点
            while current_node:
                if current_node.type != 'ForControl' and current_node.type != 'WhileControl':
                    current_node = current_node.father
                else:
                    break
            sentence_node = current_node.first_son
            while sentence_node.value != 'Sentence':
                sentence_node = sentence_node.right
        
        sentence_node.extra_info = "break"
        self.loop_finish_flag = True
                
    # continue语句
    def _continue(self,node=None):
        sentence_node = node.father
        # 说明这是在ifelse语句里的continue
        if sentence_node.father.type != 'ForControl' and sentence_node.father.type != 'WhileControl':
            current_node = sentence_node.father
            # 找到break所属的循环体节点
            while current_node:
                if current_node.type != 'ForControl' and current_node.type != 'WhileControl':
                    current_node = current_node.father
                else:
                    break
            sentence_node = current_node.first_son
            while sentence_node.value != 'Sentence':
                sentence_node = sentence_node.right
                
        
        sentence_node.extra_info = "continue"
        self.loop_finish_flag = True
        
    # TODO:增加识别操作符和操作数层级以还原逆波兰表达式的功能
    def _traverse_expression(self, node=None,depth = 0):
        if not node:
            return
        if node.type == '_Variable':
            self.expres_stack.append(
                {'type': 'VARIABLE', 'operand': node.value,'depth':depth})
        elif node.type == '_Constant':
            self.expres_stack.append(
                {'type': 'DIGIT_CONSTANT', 'operand': node.value,'depth':depth})
        elif node.type == '_Operator':
            self.expres_stack.append(
                {'type': 'Operator', 'operator':node.value,'depth':depth})
        elif node.type == '_ArrayName':
            self.expres_stack.append(
                {'type': 'ARRAY_ITEM', 'operand': [node.value, node.right.value],'depth':depth})
            return
        
        current_node = node.first_son
        while current_node:
            self._traverse_expression(current_node,depth+1)
            current_node = current_node.right

    # 表达式类型返回-->用于赋值和初始化语句
    def _expression(self, node=None):
        if node.type == 'Constant':
            # 如果是数值常量
            if node.first_son.type == '_Constant':
                return {'type': 'DIGIT_CONSTANT', 'value': node.first_son.value}
            # 如果是字符串常量
            elif node.first_son.type == 'STRING_CONSTANT':
                return {'type': 'STRING_CONSTANT', 'value': node.first_son.value}
            elif node.first_son.type == 'BOOL_CONSTANT':
                if node.first_son.value == 'True':
                    return {'type': 'BOOL_CONSTANT','value':True}
                else:
                    return {'type': 'BOOL_CONSTANT','value':False}
            
        elif node.type == 'Variable':
            return {'type':'VARIABLE','value':node.first_son.value}
        
        # 先清空
        self.operand_stack = []
        
        # 判断self是在赋值函数中调用的还是在for语句中调用的，二者语法树结构不同
        if node.left.father:
            reverse_polishexpression_statement = [tree.current for tree in node.extra_info]
            # 如果是赋值语句，则symbol_dict的更新交给赋值函数
            if node.left.father.value == 'Assignment':
                result = self._traverse_statement_calculate(reverse_polishexpression_statement)
                field_type = self.judge_type(result)
                constant_type = self.judge_constant_type(field_type)
                return_value = {'type': constant_type, 'value': result}
                return return_value
            elif node.left.father.type == 'ForControl':
                # 如果是for语句，则symbol_dict的更新需要在这里完成
                self._traverse_statement_update(reverse_polishexpression_statement)  
                
    # 遍历逆波兰表达式并完成计算(更新)
    def _traverse_statement_update(self,statement):
        stack = []
        name_stack = []
        type_stack = []
        for item in statement:
            item_type = item.type
            item_value = item.value
            if item_type == '_Variable':
                if item_value not in self.symbol_dict[self.current_function]:
                    print("变量{}未声明!".format(item_value))
                    raise ProgramError("变量{}未声明!".format(item_value))
                    
                if self.symbol_dict[self.current_function][item_value]['init'] == 0:
                    print("变量{}未初始化!".format(item_value))
                    raise ProgramError("变量{}未初始化!".format(item_value))
                    
                stack.append(self.symbol_dict[self.current_function][item_value]['value'])
                name_stack.append(item_value)
                type_stack.append('Var')
            elif item_type == '_Constant':
                if '.' in item_value:
                    stack.append(float(item_value))
                else:
                    stack.append(int(item_value))
                type_stack.append('Cons')
                name_stack.append(None)
            
            elif item_type == 'BOOL_CONSTANT':
                if item_value == 'True':
                    stack.append(True)
                else:
                    stack.append(False)
                type_stack.append('BOOL')
                name_stack.append(None)
                
            elif item_type == '_Operator':
                # 单目运算符
                if item_value in child_operators[0]:
                    right_operand = stack.pop()
                    right_type = type_stack.pop()
                    right_name = name_stack.pop()
                    if item_value == '!':
                        result = not right_operand
                    elif item_value == '++':
                        result = right_operand + 1
                        if right_type == 'Var':
                            self.symbol_dict[self.current_function][right_name]['value'] = result
                    elif item_value == '--':
                        result = right_operand - 1
                        if right_type == 'Var':
                            self.symbol_dict[self.current_function][right_name]['value'] = result
                    stack.append(result)
                    type_stack.append('Cons')
                    name_stack.append(None)
                # 双目运算符
                elif item_value in child_operators[1]:
                    right_operand = stack.pop()
                    left_operand = stack.pop()
                    right_type = type_stack.pop()
                    left_type = type_stack.pop()
                    right_name = name_stack.pop()
                    left_name = name_stack.pop()
                    if item_value == '+':
                        result = left_operand + right_operand
                    elif item_value == '-':
                        result = left_operand - right_operand
                    elif item_value == '*':
                        result = left_operand * right_operand
                    elif item_value == '/':
                        result = left_operand / right_operand
                    elif item_value == '%':
                        result = left_operand % right_operand
                    elif item_value == '~':
                        result = left_operand ** right_operand
                    elif item_value == '>':
                        result = left_operand > right_operand
                    elif item_value == '<':
                        result = left_operand < right_operand
                    elif item_value == '>=':
                        result = left_operand >= right_operand
                    elif item_value == '<=':
                        result = left_operand <= right_operand
                    elif item_value == '==':
                        result = left_operand == right_operand
                    elif item_value == '!=':
                        result = left_operand != right_operand
                    elif item_value == '&':
                        result = left_operand and right_operand
                    elif item_value == '|':
                        result = left_operand or right_operand
                    elif item_value == '^':
                        result = left_operand ^ right_operand
                    elif item_value == '=':
                        result = right_operand
                        if left_type == 'Var':
                            self.symbol_dict[self.current_function][left_name]['value'] = result
                        else:
                            print("赋值左值必须为变量!")
                            raise ProgramError("赋值左值必须为变量!")

                    stack.append(result)
                    type_stack.append('Cons')
                    name_stack.append(None)
                else:
                    print("operator {} not supported!".format(item_value))
                    raise ProgramError("operator {} not supported!".format(item_value))
                    
        return result
    
    # 表达式值返回-->用于Contorl语句
    def _calculate_expression(self,node=None):
        # 先清空
        self.operand_stack = []
        
        # 逆波兰表达式
        # 不优雅的实现方式：把Parser类中已经生成好的逆波兰表达式通过extra_info属性传到了Semantic类。
        # TODO:直接通过语法树还原逆波兰表达式
        reverse_polishexpression_statement = [tree.current for tree in node.extra_info]
        result = self._traverse_statement_update(reverse_polishexpression_statement) # 赋值并更新
        if not isinstance(result,bool):
            if result == 0:
                result = False
            else:
                result = True
        return result
    
    # 遍历逆波兰表达式并完成计算(不更新)
    def _traverse_statement_calculate(self,statement):
        stack = []
        for item in statement:
            item_type = item.type
            item_value = item.value
            if item_type == '_Variable':
                if item_value not in self.symbol_dict[self.current_function]:
                    print("变量{}未声明!".format(item_value))
                    raise ProgramError("变量{}未声明!".format(item_value))
                    
                if self.symbol_dict[self.current_function][item_value]['init'] == 0:
                    print("变量{}未初始化!".format(item_value))
                    raise ProgramError("变量{}未初始化!".format(item_value))
                    
                stack.append(self.symbol_dict[self.current_function][item_value]['value'])
            elif item_type == '_Constant':
                if '.' in item_value:
                    stack.append(float(item_value))
                else:
                    stack.append(int(item_value))
                    
            elif item_type == 'BOOL_CONSTANT':
                if item_value == 'True':
                    stack.append(True)
                else:
                    stack.append(False)

            elif item_type == '_Operator':
                # 单目运算符
                if item_value in child_operators[0]:
                    right_operand = stack.pop()
                    if item_value == '!':
                        result = not right_operand
                    elif item_value == '++':
                        result = right_operand + 1
                    elif item_value == '--':
                        result = right_operand - 1
                    stack.append(result)
                # 双目运算符
                elif item_value in child_operators[1]:
                    right_operand = stack.pop()
                    left_operand = stack.pop()
                    if item_value == '+':
                        result = left_operand + right_operand
                    elif item_value == '-':
                        result = left_operand - right_operand
                    elif item_value == '*':
                        result = left_operand * right_operand
                    elif item_value == '/':
                        result = left_operand / right_operand
                    elif item_value == '%':
                        result = left_operand % right_operand
                    elif item_value == '~':
                        result = left_operand ** right_operand
                    elif item_value == '>':
                        result = left_operand > right_operand
                    elif item_value == '<':
                        result = left_operand < right_operand
                    elif item_value == '>=':
                        result = left_operand >= right_operand
                    elif item_value == '<=':
                        result = left_operand <= right_operand
                    elif item_value == '==':
                        result = left_operand == right_operand
                    elif item_value == '!=':
                        result = left_operand != right_operand
                    elif item_value == '&':
                        result = left_operand and right_operand
                    elif item_value == '|':
                        result = left_operand or right_operand
                    elif item_value == '^':
                        result = left_operand ^ right_operand
                    elif item_value == '=':
                        result = right_operand
                    stack.append(result)
                else:
                    print("operator {} not supported!".format(item_value))
                    raise ProgramError("operator {} not supported!".format(item_value))
                    
        return result
    
    # 处理某一种句型
    def _handler_block(self, node=None):
        if not node:
            return
        # 下一个将要遍历的节点
        if node.value in self.sentence_type:
            # 如果是根节点
            if node.value == 'Sentence':
                self.traverse(node.first_son)
            # 声明语句
            elif node.value == 'Statement':
                self._statement(node)
            
            # 函数声明，略过继续执行
            elif node.value == 'FunctionStatement':
                current_node = node.first_son
                while current_node:
                    if current_node.value == 'FunctionName':
                        self.current_function = current_node.first_son.value
                    if current_node.value == 'Sentence':
                        break
                    current_node = current_node.right
                self.traverse(current_node.first_son)

            # 函数调用
            elif node.value == 'FunctionCall':
                func_name = node.first_son.value
                
                # 如果函数尚未声明且非内置函数
                if func_name not in self.symbol_dict:
                    if func_name not in inside_function:
                        raise ProgramError("函数{}尚未定义，无法调用!".format(func_name))
                              
                if node.right and func_name not in inside_function:
                    self.function_statement_node_dict[func_name]['out_node'] = node.right
                self._function_call(node)
            # 赋值语句
            elif node.value == 'Assignment':
                self._assignment(node)
            # 变量初始化语句
            elif node.value == 'VARIABLE_INITIALIZATION':
                self._variable_initialization(node)
            # 控制语句
            elif node.value == 'Control':
                if node.type == 'IfElseControl':
                    self._control_if(node)
                elif node.type == 'ForControl':
                    self._control_for(node)
                elif node.type == 'WhileControl':
                    self._control_while(node)
                else:
                    print('control type not supported!')
                    raise ProgramError('control type not supported!')
            # break语句
            elif node.value == 'BREAK':
                self._break(node)
            # continue语句
            elif node.value == 'CONTINUE':
                self._continue(node)
            # 表达式语句
            elif node.value == 'Expression':
                self._expression(node)
            # return语句
            elif node.value == 'Return':
                self._return(node)
            else:
                print('sentence type not supported yet！')
                raise ProgramError('sentence type not supported yet！')

    # 遍历节点
    def traverse(self, node=None):
        self._handler_block(node)
        # break和continue语句
        if self.loop_finish_flag:
            next_node = None
        # 其他正常句型
        else:
            next_node = node.right
        while next_node:
            self._handler_block(next_node)
            if self.loop_finish_flag:
                next_node = None
            else:
                next_node = next_node.right

Lex = Lexer("testc.txt")
tokens = Lex.run()

Par = Parser(tokens)
Par.main()

ast = Par.tree.root
Par.display(ast)

Sem = Semantic(ast)
Sem.traverse(Sem.main_node)
