本blog除部分译文外，所有内容均为原创，如有雷同，算我抄你:-)
##问题描述
在Xcode中断点调试时，鼠标停留在变量上，就能看到变量的信息。但对于自定义对象，通常Xcode提供的直接信息非常有限，像这样
![请输入图片描述][1]


想要了解这个对象具体的内容，需要展开左边的箭头
![请输入图片描述][2]

当开发者想要知道该对象具体某个成员(很可能也是一个对象，即对象的成员的成员.....)的值时，就不得不反复展开多个箭头，平添了不少debug时的焦躁=。=

</br>
</br>
##解决方案
其实LLDB的设计者并非没有考虑到这种情况，他们设计了一种机制，允许在浮动窗口和变量窗口中显示***自定义类型对象的概览***，称之为summary。
没错，就是浮动窗口上最后一行显示的summary，我们再看一次
![请输入图片描述][3]

Summary的原理很简单，就是保存一个"对象类型->概览"的映射表，在调试时查表进行显示。在console中输入
```sh
type summary list
```
可以查看当前LLDB支持的所有语言/平台的所有类型的summary，比如OC下的NSArray
```sh
type summary list NSArray
```
输出的结果里，可以找到
![请输入图片描述][4]
和平常使用过程中的情况一致。

LLDB支持为自定义类型添加summary。
</br>
</br>
##解决示例
直观起见，这里将写一个简单的对象并为之添加summary，下面请演员入场
```objc
@interface Rectangle : NSObject
{
    NSInteger _width;
    NSInteger _height;
}

@property (nonatomic, assign) NSInteger width;
@property (nonatomic, assign) NSInteger height;

@end
```
对于这个矩形类的实例，我希望能够直接看到它的面积。

>Summary可以简单地设置对象的概览为静态字符串，也可以设置为动态的如正则表达式，甚至可以设置为Python function(事实上LLDB就是使用了Python作为映射的)。

在这里，嗯。。。。。Python，就决定是你啦!
![请输入图片描述][5]

方便起见不直接在console里写入，而是把function单独放在一个文件里
```python
def Rectangle_summary (valobj,internal_dict):
    height_val = valobj.GetChildMemberWithName('_height')
    width_val = valobj.GetChildMemberWithName('_width')
    height = height_val.GetValueAsUnsigned(0)
    width = width_val.GetValueAsUnsigned(0)
    area = height*width
    return 'Area: ' + str(area)
```
保存成**summarys.py**

>保存起来而不是直接在console里写，将来就可以方便地添加其他自定义类型的summary，也可以将这个文件和开发组的成员共享:)

接下来导入到LLDB中
```sh
command script import /Users/XXX/Desktop/TypeSummaryTest/TypeSummaryTest/summarys.py
```
>P.S:这个命令目测只支持full path，请允许我在这里可耻地匿了=。=

然后将导入的function指定为映射即可
```sh
type summary add Rectangle -F summarys.Rectangle_summary
```

这时再次查看变量，Summary已经有内容啦:)
![请输入图片描述][6]

![请输入图片描述][7]

假如有多个自定义类型的summary，都可以如法炮制。进一步地，可以让Xcode自动加载summary。首先，把加载function这步也写入脚本
```sh
import lldb

def Rectangle_summary (valobj,internal_dict):
    height_val = valobj.GetChildMemberWithName('_height')
    width_val = valobj.GetChildMemberWithName('_width')
    height = height_val.GetValueAsUnsigned(0)
    width = width_val.GetValueAsUnsigned(0)
    area = height*width
    return 'Area: ' + str(area)

def __lldb_init_module(debugger, dict):
   	debugger.HandleCommand('type summary add Rectangle -F summarys.Rectangle_summary')
```
然后，让Xcode在启动时**自动导入这个文件**。在~/下新建一个.lldbinit文件，并在其中写入command script import来导入summary文件
```sh
command script import /Users/XXX/Desktop/TypeSummaryTest/TypeSummaryTest/summarys.py
```
>.lldbinit这个技巧来自于Facebook的[chisel][8]，是一个FB扩展的LLDB命令集

That's all for today, have fun~
![请输入图片描述][9]


##参考资料
[LLDB Tutorial][10]
[LLDB Data Formatters][11]
[Advanced Debugging with LLDB][12]
[LLDB Python Reference][13]


  [1]: http://segmentfault.com/img/bVcLk2
  [2]: http://segmentfault.com/img/bVcLk3
  [3]: http://segmentfault.com/img/bVcLk4
  [4]: http://segmentfault.com/img/bVcLk5
  [5]: http://segmentfault.com/img/bVcLk6
  [6]: http://segmentfault.com/img/bVcLk7
  [7]: http://segmentfault.com/img/bVcLk8
  [8]: https://github.com/facebook/chisel
  [9]: http://segmentfault.com/img/bVcLa4
  [10]: http://lldb.llvm.org/tutorial.html
  [11]: http://lldb.llvm.org/varformats.html
  [12]: https://developer.apple.com/videos/wwdc/2013/?id=217
  [13]: http://lldb.llvm.org/python-reference.html