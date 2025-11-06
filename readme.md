目前进度的话，两个需求里的第一个需求已经做的差不多了，就是下载文件需要一些时间，然后还有整理下载下来的文件，目前的话对于整理的数据我是有一些疑问，但已经放在企业微信群里章老师项目那里了。

# 需求一



<img src="https://quanttide.feishu.cn/space/api/box/stream/download/asynccode/?code=NjZlNGVmNjIwNzRlNDE4MzFkZjc3M2EwZDc5ODljYjZfTndURjd2eDlabjhONm1WbWk0dXNaMGQzM2lZeDAxOW1fVG9rZW46QlRDNGJXTW9Ub0MzdDl4R3ExR2NuQkZDblU0XzE3NjI0MTIxMTI6MTc2MjQxNTcxMl9WNA" alt="img" style="zoom:50%;" />

原文链接就是用Ai翻译和方便理解的文档，原文的github链接是https://github.com/ryansmccoy/py-sec-edgar，章老师给的那个版本有点老不推荐。

然后是创建python项目和环境配置，首先就是win+R在命令行依次执行方法一的命令，然后验证安装没错之后，第一步的环境配置和代码部分实际上都解决的差不多了

<img src="https://quanttide.feishu.cn/space/api/box/stream/download/asynccode/?code=MTNhYzM2YTlmM2YwOWNjMTNiYjFhOWE5YmU1MTI5NzVfcUc1TTdFa2J4SzJhRGlyR3ZJU2M4eEVwY21YT0VlS25fVG9rZW46SVM4R2JaOWdsb1QwRzF4bXNQVWN4Z090bkVoXzE3NjI0MTIxMTI6MTc2MjQxNTcxMl9WNA" alt="img" style="zoom:50%;" />

因为要求是2004年开始，**把setting.py里的第200行左右的代码里的时间改成8030天，即22年前开始**

<img src="https://quanttide.feishu.cn/space/api/box/stream/download/asynccode/?code=ZThiMTJkZmI2NjY3OGE5NWUwNTEwYzYzMjNmNGMwZWRfN1Iybzc1YkhITFZJWDZsRkh6VFZUd3hvNFhTbUVhUFRfVG9rZW46SXJ3aGIwVVp3bzBuWWt4ZkpSOWNQa0xUbkJnXzE3NjI0MTIxMTI6MTc2MjQxNTcxMl9WNA" alt="img" style="zoom:50%;" />

<img src="https://quanttide.feishu.cn/space/api/box/stream/download/asynccode/?code=Yzk0MTAyMmViZWM2MzZlZDdiNDVmMWYyM2I1MTVjNDFfT2dwSkdvT0RSbkluQVVBdVEzVzlSNGZHVjE4NmZtYUdfVG9rZW46UldLVWJGRGpxb2RXVk14bXUyRGNZTjBXblNmXzE3NjI0MTIxMTI6MTc2MjQxNTcxMl9WNA" alt="img" style="zoom:50%;" />

这里的原文链接，例如如下几张图，都有教学：

<img src="https://quanttide.feishu.cn/space/api/box/stream/download/asynccode/?code=MmVlZWFkOTk0ZTFhNjYwMWIwNjRlNWFmMTI3MDI3Y2FfeHluUEU4VU9jN25mM3g2RkhKdzZIaGZrYUpLbVp0ckNfVG9rZW46U3l0eWJMbU9Tb3k0cGF4dkx1ZWMzVlU4bldiXzE3NjI0MTIxMTI6MTc2MjQxNTcxMl9WNA" alt="img" style="zoom:50%;" />



然后因为我们要爬取的是8-k文件、任意公司等要求,就可以在uv run python......后面的语句改一下。

下载命令：
```cmd
uv run python -m py_sec_edgar workflows full-index --start-date 2004-01-01 --end-date 2004-03-31 --forms "8-K" --no-ticker-filter --download --extract
```

> [!tip]
>
> 这里的下载数据较慢，建议以季度为单位下载，预估花费若干小时
>
> 可能原因在于梯子链接不稳定

下载的文件结构如下

```
│data/
├── Archives/edgar/data/
│   └── 320193/                    # 公司的CIK
│       └── 000032019324000123/    # 特定filing
│           ├── 0001-aapl-20240930.htm  # 主要8-K文档（有时也可能是txt格式）
│           ├── 0002-(ex...).htm  #其他附件（也存在txt格式）
│           └── 
│		└── 000032019324000123.txt #主要8-K文档txt格式
```



<img src="https://quanttide.feishu.cn/space/api/box/stream/download/asynccode/?code=YzlmN2EyZDMyODJhYjk4NTRiMDJkNTI1ZWU0ZDFkN2Vfd2ZSN0RSbU5MQ01HbzduVE02ejV2dXV3SFNBeUhQOXVfVG9rZW46TEE0WmJ3WnRPb0ZOcWh4bGZoVWNFRjdZblNmXzE3NjI0MTIxMTI6MTc2MjQxNTcxMl9WNA" alt="img" style="zoom:50%;" />

<img src="https://quanttide.feishu.cn/space/api/box/stream/download/asynccode/?code=NGUxNjg4ZTAzN2RjODE3OTA1YjEyNDNhOTEwZDhlZTZfR2RQNzk4VEFzNHBMOHNOQlc0WEY1azQ0U0ZhMUYzY0VfVG9rZW46UExJUmJYaktRb3puVE94OGZySGNlZ1dybk1xXzE3NjI0MTIxMTI6MTc2MjQxNTcxMl9WNA" alt="img" style="zoom:50%;" />



上面下载命令`--extract`指令会默认下载所有附件，需要后期确认一文件是否为贷款文件。

# 需求二

目前先仅用了关键词匹配希望能找到对应信息，成效不好，一些合同中的格式不了解导致文本分析效率较低。主要挑战任务为nlp处理文本内容以得到正确信息