# 📒 简单记账本

基于 **Python + Streamlit + SQLite3** 的个人记账 Web 工具，适合编程新手学习和日常使用。

## 功能

| 功能 | 说明 |
|------|------|
| 📝 添加账目 | 填写金额、分类、日期、备注，表单提交 |
| 📋 查看列表 | 按月份和分类筛选，表格展示所有记录 |
| 🗑️ 删除账目 | 输入 ID 删除，删除前二次确认 |
| 📊 分类统计 | 柱状图 + 汇总表，按分类聚合金额 |

预设 6 个分类：**餐饮、交通、购物、娱乐、居住、其他**

## 技术栈

- **UI 框架**：[Streamlit](https://streamlit.io/)
- **数据库**：SQLite3（Python 标准库）
- **数据处理**：pandas
- **图表**：Plotly

## 快速开始

```bash
# 1. 克隆仓库
git clone git@github.com:May-iiii/finance_cli.git
cd finance_cli

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动应用
streamlit run app.py
```

浏览器会自动打开 `http://localhost:8501`。

## 项目结构

```
finance_cli/
├── app.py              # 界面层：4 个 Tab 页面 + 入口
├── database.py         # 数据层：建表、增删查、分类统计
├── config.py           # 常量定义：分类列表、数据库路径
├── requirements.txt    # Python 依赖
└── CLAUDE.md           # AI 助手指南
```

## 数据库

单表 `records`，字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键，自增 |
| amount | REAL | 金额，大于 0 |
| category | TEXT | 6 个预设分类之一 |
| date | TEXT | 日期（YYYY-MM-DD） |
| note | TEXT | 备注，可选 |
| created_at | TIMESTAMP | 创建时间，自动填充 |

## 许可

MIT
