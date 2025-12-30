# 豆瓣电影同步到Notion

一个简单易用的工具，将豆瓣电影信息一键同步到Notion，支持GitHub Actions定时同步。

## 核心特性

- 🎬 支持同步已看、想看、在看电影列表
- � 无需豆瓣API密钥，直接爬取数据
- � 支持全量同步和增量同步
- 📊 详细的同步日志和统计
- ⏰ 支持GitHub Actions定时执行
- 🎨 自动创建Notion数据库，包含电影海报
- 📋 简化的配置流程，提供配置向导
- 🔒 安全的环境变量管理

## 快速开始

📖 **新用户？** 查看 [快速开始指南](./QUICKSTART.md) 5分钟快速部署

### 方式一：本地运行

#### 1. 克隆项目

```bash
git clone https://github.com/yourusername/douban2notion.git
cd douban2notion
```

#### 2. 创建虚拟环境

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

#### 3. 安装依赖

```bash
pip install -r requirements.txt
```

#### 4. 配置环境变量

运行配置向导：

```bash
python setup.py
```

按照提示输入配置信息：

- **豆瓣用户名**：豆瓣个人主页URL中的用户名，例如 `https://movie.douban.com/people/username/` 中的 `username`
- **Notion集成密钥**：访问 [Notion集成页面](https://www.notion.so/my-integrations) 创建集成并获取
- **数据库配置**：选择使用现有数据库或自动创建新数据库
- **同步状态**：选择要同步的电影类型（已看/想看/在看）
- **增量同步**：选择是否只同步新电影

#### 5. 开始同步

```bash
python main.py
```

### 方式二：GitHub Actions部署

#### 1. Fork项目

访问项目GitHub页面，点击右上角 "Fork" 按钮

#### 2. 获取配置信息

| 配置项 | 获取方式 |
| ------ | -------- |
| DOUBAN_USER_ID | 豆瓣个人主页URL中的用户名 |
| NOTION_API_KEY | [Notion集成页面](https://www.notion.so/my-integrations) 创建集成获取 |
| NOTION_DATABASE_ID | Notion数据库页面URL中获取（32位字符） |
| NOTION_PARENT_PAGE_ID | Notion父页面URL中获取（32位字符，用于自动创建数据库） |

#### 3. 配置GitHub Secrets

在Fork仓库中，进入 `Settings > Secrets and variables > Actions`，添加以下Secrets：

| Secret名称 | 说明 |
| ---------- | ---- |
| DOUBAN_USER_ID | 豆瓣用户名 |
| NOTION_API_KEY | Notion集成密钥 |
| NOTION_DATABASE_ID | Notion数据库ID（可选） |
| NOTION_PARENT_PAGE_ID | Notion父页面ID（可选，用于自动创建数据库） |

#### 4. 手动触发同步

进入仓库的 `Actions > 豆瓣电影同步到Notion > Run workflow`，选择同步状态和是否增量同步，点击运行。

#### 5. 定时同步

工作流默认每天凌晨2点（北京时间）自动执行同步。如需修改，编辑 `.github/workflows/sync.yml` 中的 `cron` 表达式。

## 配置说明

### 环境变量

| 变量名 | 必需 | 说明 | 默认值 |
| ------ | ---- | ---- | ------ |
| DOUBAN_USER_ID | 是 | 豆瓣用户名 | - |
| NOTION_API_KEY | 是 | Notion集成密钥 | - |
| NOTION_DATABASE_ID | 否 | Notion数据库ID | - |
| NOTION_PARENT_PAGE_ID | 否 | Notion父页面ID | - |
| SYNC_STATUS | 否 | 同步状态(watched/wish/do) | watched |
| INCREMENTAL_SYNC | 否 | 增量同步(true/false) | false |

### 数据库配置说明

**选项1：使用现有数据库**
- 配置 `NOTION_DATABASE_ID`
- 确保数据库包含以下字段：电影名称、豆瓣ID、状态、评分、上映年份、导演、地区、豆瓣链接、海报、简介、用户评论、评分日期

**选项2：自动创建数据库**
- 配置 `NOTION_PARENT_PAGE_ID`
- 程序会自动在指定页面下创建数据库
- 确保Notion集成已添加到父页面

## Notion数据库字段

| 字段名称 | 类型 | 说明 |
| -------- | ---- | ---- |
| 电影名称 | 标题 | 电影中文名称 |
| 豆瓣ID | 文本 | 豆瓣电影唯一标识 |
| 状态 | 选择 | 已看/想看/在看 |
| 评分 | 数字 | 用户评分(1-10) |
| 上映年份 | 数字 | 电影上映年份 |
| 导演 | 文本 | 电影导演 |
| 地区 | 多选 | 制作地区 |
| 豆瓣链接 | URL | 豆瓣电影页面链接 |
| 海报 | 文件 | 电影海报图片 |
| 简介 | 文本 | 电影简介 |
| 用户评论 | 文本 | 用户评论 |
| 评分日期 | 日期 | 用户评分日期 |

## 使用技巧

### 1. 创建画廊视图

同步完成后，在Notion数据库中创建画廊视图：
1. 点击数据库右上角 `+` 添加视图
2. 选择 "Gallery" 类型
3. 设置封面属性为 "海报"
4. 调整卡片大小和显示字段

### 2. 增量同步

设置 `INCREMENTAL_SYNC=true` 可以只同步新电影，避免重复同步已有电影，提高同步效率。

### 3. 同步多种状态

可以分别同步已看、想看、在看电影：
```bash
# 同步已看电影
SYNC_STATUS=watched python main.py

# 同步想看电影
SYNC_STATUS=wish python main.py

# 同步在看电影
SYNC_STATUS=do python main.py
```

## 常见问题

### Q: 如何获取豆瓣用户名？
A: 打开豆瓣个人主页，URL格式为 `https://movie.douban.com/people/username/`，其中 `username` 就是用户名。

### Q: 如何获取Notion集成密钥？
A: 访问 [Notion集成页面](https://www.notion.so/my-integrations)，点击 "New integration"，填写名称并提交，复制生成的密钥（secret_开头）。

### Q: 如何获取Notion页面/数据库ID？
A: 打开Notion页面或数据库，URL中包含32位字符的ID，例如：`https://www.notion.so/username/Page-Name-32位ID`。

### Q: 同步失败怎么办？
A: 检查以下几点：
- 确保配置信息正确
- 确保Notion集成已添加到对应页面
- 检查网络连接
- 查看日志中的错误信息

### Q: 如何更新已有电影？
A: 使用全量同步（`INCREMENTAL_SYNC=false`），程序会自动检测并更新已有电影。

### Q: 可以同步其他类型的内容吗？
A: 当前版本仅支持电影同步，后续版本可能会支持书籍、音乐等内容。

## 技术栈

- **Python 3.8+**
- **requests** - HTTP请求
- **beautifulsoup4** - HTML解析
- **python-dotenv** - 环境变量管理
- **notion-client** - Notion API客户端

## 项目结构

```
douban2notion/
├── src/
│   ├── __init__.py
│   ├── config.py          # 配置管理
│   ├── douban_api.py      # 豆瓣爬虫
│   ├── models.py          # 数据模型
│   ├── notion_api.py      # Notion API
│   └── sync_service.py    # 同步服务
├── .github/
│   └── workflows/
│       └── sync.yml       # GitHub Actions工作流
├── main.py                # 主程序入口
├── setup.py               # 配置向导
├── requirements.txt       # 依赖列表
└── README.md             # 项目说明
```

## 开发说明

### 本地开发

```bash
# 激活虚拟环境
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 运行配置向导
python setup.py

# 运行同步
python main.py
```

### 调试模式

修改 `src/config.py` 中的日志级别为 `DEBUG` 可以查看更详细的日志信息。

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 更新日志

详情请查看 [CHANGELOG.md](./CHANGELOG.md)
