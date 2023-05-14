# CLike Interpreter

## Summary

使用python编写类C语言的解释器，涉及词法分析、语法分析和语义分析并解释执行。

## LOGS

### V1.0

2023 5.6

- 实现基本的词法分析、语法分析和语义分析和语义解释
- 输出Token和语法树，以及程式的运行结果
- 基本的报错提醒，未标志行列

### V2.0

2023 5.9

- 实现了嵌套的循环功能
- 增加`break`和`continue`关键字及其功能实现
- 添加`bool`类型常量

## Functions

基本变量类型：int float string bool

基本四则运算：+ - * \

基本比较运算：> < == >= <= !=

基本逻辑运算：& | ! ^

变量声明、变量赋值、变量初始化

函数声明、函数调用、函数返回值

控制语句IfElse分支，While和For循环

内置函数`printf`,`readInt`,`readFloat,`,`readString`

## Example

语法示例：

~~~c
func test(int a,int b){
	if (a>b){
		printf("yes");
	}
	return a;
}

func main(){
	int a = 4;
	int b = 3;
	
	for (int i = 0;i<5;i=i+1){
		int result = test(a,b);
	}
}
~~~

Output:

~~~
yesyesyesyesyes
~~~

## TODO

- 增加函数递归调用功能
- 增加数组变量类型
- 美观的IDE界面以及友好的报错提醒
- 字符串内支持引号

## Environment

- Python version 3.9.7