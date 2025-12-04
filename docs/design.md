# 项目是怎么运行的？
## Roadmap
1. 首先，通过检索关键词找到相关饰品的hashName，相当于绑定到了唯一的饰品 【完成】
2. 后端系统，就是不同层级管理，简单调用方法，直接返回想要的结果，中间复杂的过程是看不见的，处理好了
3. 前端页面，实现大概的搜索显示
4. fastapi，输入hashname，返回输出饰品价格
5. 追踪饰品，持续记录饰品价格
6. 在输入框里面输入电子邮件地址，发送饰品报告
## 邮箱发送功能
1. 从 email_config.json 文件读取配置
2. 为每个收件人单独创建邮件对象（MIMEMultipart）
设置发件人、收件人、主题
添加纯文本正文内容
处理附件：验证文件存在性，编码为base64，添加到邮件中
```python
# 为每个收件人单独发送，避免批量发送被当作垃圾邮件
for recipient in recipients:
    # 建立新的SMTP连接
    server = smtplib.SMTP(smtp_server, smtp_port, timeout=30)
    # 启用TLS加密（如果配置）
    if use_tls:
        server.starttls()
    # 登录SMTP服务器
    server.login(username, password)
    # 发送邮件
    server.sendmail(from_address, [recipient], msg.as_string())
    # 关闭连接
    server.quit()
```

