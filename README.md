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

### V3.0

2023 5.14

- 增加了IDE界面，内嵌模拟控制台
- 完善了大部分报错提醒

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

语法示例：打印1~100的质数

~~~c
func main(){
	int i, j;

	printf("Prime numbers between 1 and 100£º");

	for (i = 2; i <= 100; i=i+1) {
		for (j = 2; j < i; j=j+1) {
			if (i % j == 0) {
				break;
			}
		}

		if (j == i) {
			printf(i);
			printf(" ");
		}
	}
}
~~~

Output:

~~~
Prime numbers between 1 and 100：2 3 5 7 11 13 17 19 23 29 31 37 41 43 47 53 59 61 67 71 73 79 83 89 97 
~~~

## IDE

![IDE](https://summerfoam233-image.oss-cn-beijing.aliyuncs.com/img/IDE.png)

## TODO

- 增加函数递归调用功能
- 增加数组变量类型
- 字符串内支持引号

## Environment

- Python version 3.9.7