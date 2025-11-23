# 便携饰品跟踪器
hi~各位导🐕中午好!我谨代表导🐕联盟设计出便携获取不同平台饰品价格的工具，我的开发计划和代码仓库都会实时更新在这里！

## RoadMap
1. ✅ 简单的查询价格 (已完成)
2. 饰品价格追踪
3. 邮箱通知
4. 实时自动交易

## DDrager - 核心数据获取工具

DDrager 是一个轻量级的数据获取核心工具，专注于从 SteamDT API 获取原始价格数据。

### 设计理念
- ✅ **纯粹的数据获取** - 只返回原始 JSON 数据，不做任何格式化
- ✅ **简洁的接口** - 仅需两个参数：`--apikey` 和 `--hashname`
- ✅ **可被调用** - 其他工具可以通过命令行调用 ddrager 获取数据
- ✅ **轻量级** - 无依赖的核心功能

### 安装依赖
```bash
pip install -r requirements.txt
```

### 使用方法

**基本用法:**
```bash
python ddrager.py --apikey YOUR_API_KEY --hashname "AK-47 | Redline (Field-Tested)"
```

**输出原始 JSON 数据:**
```json
{
  "success": true,
  "data": [
    {
      "platform": "BUFF",
      "sellPrice": 35.0,
      "sellCount": 19,
      "biddingPrice": 23.1,
      ...
    }
  ]
}
```

### 在其他工具中调用

```python
import subprocess
import json

# 调用 ddrager 获取数据
result = subprocess.run(
    ['python', 'ddrager.py', '--apikey', 'YOUR_KEY', '--hashname', 'AK-47 | Redline (Field-Tested)'],
    capture_output=True,
    text=True
)

# 解析返回的 JSON 数据
data = json.loads(result.stdout)
```

```bash
# 在 Shell 中调用
data=$(python ddrager.py --apikey YOUR_KEY --hashname "AWP | Asiimov (Field-Tested)")
echo $data | jq .
```

### 项目结构

```
buff-tracker/
├── ddrager.py         # 核心数据获取工具
├── test.py           # 测试脚本
├── requirements.txt  # 依赖项
├── .env             # API密钥配置(可选)
└── README.md        # 说明文档
```
