# Buff Tracker

CS2 饰品价格追踪工具

## 快速使用

### get_price - 自动获取价格
```bash
python get_price.py --hashname "AK-47 | Redline (Field-Tested)"
```
自动分配空闲 API key，返回价格数据

## 工具集

### ddrager - 数据获取
```bash
python utils/ddrager.py --apikey YOUR_KEY --hashname "AK-47 | Redline (Field-Tested)"
```
返回原始 JSON 数据

### api-manager - 额度查询
```bash
# 查看所有密钥
python utils/api-manager.py

# 查看指定密钥
python utils/api-manager.py --api-key YOUR_KEY
```

## 配置

创建 `.env` 文件:
```env
API_KEYS=key1,key2,key3
```

## 安装
```bash
pip install -r requirements.txt
```

## 项目结构
```
buff-tracker/
├── get_price.py         # 自动获取价格
├── utils/
│   ├── ddrager.py       # 数据获取
│   └── api-manager.py   # 额度管理
├── .env                 # API密钥
└── requirements.txt     # 依赖
```
