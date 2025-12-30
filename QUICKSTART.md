# 快速开始指南

## 5分钟快速部署

### 本地运行

```bash
# 1. 克隆项目
git clone https://github.com/yourusername/douban2notion.git
cd douban2notion

# 2. 创建虚拟环境
python -m venv venv
venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 运行配置向导
python setup.py

# 5. 测试配置
python test.py

# 6. 开始同步
python main.py
```

### GitHub Actions部署

```bash
# 1. Fork项目到你的GitHub账号

# 2. 配置GitHub Secrets
# 在仓库设置中添加以下Secrets:
# - DOUBAN_USER_ID: 豆瓣用户名
# - NOTION_API_KEY: Notion集成密钥
# - NOTION_DATABASE_ID: Notion数据库ID (可选)
# - NOTION_PARENT_PAGE_ID: Notion父页面ID (可选)

# 3. 手动触发同步
# 进入 Actions > 豆瓣电影同步到Notion > Run workflow
```

## 配置说明

### 必需配置

| 配置项 | 获取方式 | 示例 |
| ------ | -------- | ---- |
| DOUBAN_USER_ID | 豆瓣个人主页URL中的用户名 | `username` |
| NOTION_API_KEY | [Notion集成页面](https://www.notion.so/my-integrations) | `secret_xxxxx` |

### 可选配置

| 配置项 | 说明 | 默认值 |
| ------ | ---- | ------ |
| NOTION_DATABASE_ID | 现有数据库ID | 空 |
| NOTION_PARENT_PAGE_ID | 父页面ID（用于自动创建数据库） | 空 |
| SYNC_STATUS | 同步状态(watched/wish/do) | watched |
| INCREMENTAL_SYNC | 增量同步(true/false) | false |

## 常见问题

### 1. 如何获取豆瓣用户名？

打开豆瓣个人主页，URL格式为 `https://movie.douban.com/people/username/`，其中 `username` 就是用户名。

### 2. 如何创建Notion集成？

1. 访问 [Notion集成页面](https://www.notion.so/my-integrations)
2. 点击 "New integration"
3. 填写名称（如：豆瓣电影同步）
4. 选择工作区
5. 点击提交
6. 复制生成的密钥（secret_开头）

### 3. 如何获取Notion页面/数据库ID？

打开Notion页面或数据库，URL中包含32位字符的ID，例如：
`https://www.notion.so/username/Page-Name-32位ID`

### 4. 如何使用自动创建数据库功能？

1. 在Notion中创建一个页面
2. 将集成添加到该页面（点击页面右上角 `...` > `Add connections`）
3. 复制页面ID
4. 配置 `NOTION_PARENT_PAGE_ID`
5. 运行程序，会自动创建数据库

### 5. 同步失败怎么办？

1. 检查配置是否正确
2. 运行 `python test.py` 测试连接
3. 确保Notion集成已添加到对应页面
4. 查看日志中的错误信息

## 使用技巧

### 增量同步

设置 `INCREMENTAL_SYNC=true` 可以只同步新电影，避免重复同步已有电影。

### 同步多种状态

可以分别同步已看、想看、在看电影：

```bash
# 同步已看电影
SYNC_STATUS=watched python main.py

# 同步想看电影
SYNC_STATUS=wish python main.py

# 同步在看电影
SYNC_STATUS=do python main.py
```

### 创建画廊视图

同步完成后，在Notion数据库中创建画廊视图：
1. 点击数据库右上角 `+` 添加视图
2. 选择 "Gallery" 类型
3. 设置封面属性为 "海报"
4. 调整卡片大小和显示字段

## 下一步

- 查看 [README.md](./README.md) 了解更多功能
- 查看 [CHANGELOG.md](./CHANGELOG.md) 了解更新历史
- 提交 [Issue](https://github.com/yourusername/douban2notion/issues) 反馈问题
