# 简单记账本 (Finance CLI)

基于 **Python + Streamlit + SQLite3** 的个人记账 Web 工具。

## 技术栈

- **UI 框架**: Streamlit
- **数据库**: SQLite3（Python 标准库）
- **数据处理**: pandas
- **图表**: Plotly（柱状图）

## 项目结构

| 文件 | 职责 |
|------|------|
| `config.py` | 常量定义：预设分类列表、数据库文件路径 |
| `database.py` | 数据层：建表、增删查、分类统计，全部 SQL 操作 |
| `app.py` | 界面层：4 个 Tab 页面的 UI 渲染 + 入口 `streamlit run app.py` |

## 数据库

单表 `records`：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK AUTOINCREMENT | 主键 |
| amount | REAL NOT NULL | 金额，CHECK > 0 |
| category | TEXT NOT NULL | 预设 6 分类之一 |
| date | TEXT NOT NULL | ISO 格式 YYYY-MM-DD |
| note | TEXT | 备注，可为空 |
| created_at | TIMESTAMP | 自动填充 |

预设分类：`餐饮`、`交通`、`购物`、`娱乐`、`居住`、`其他`

## 功能

1. **添加账目** — 表单输入金额、分类、日期、备注
2. **查看列表** — 按月份 + 分类筛选，表格展示
3. **删除账目** — 按 ID 删除，删除前显示详情确认
4. **分类统计** — 柱状图 + 汇总表（笔数、总金额、平均金额）

## 启动方式

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 代码规范

- 函数返回值统一为 `(bool, str)` 元组表示操作结果
- SQL 全部参数化查询（`?` 占位符），禁止字符串拼接
- 数据库连接在 `finally` 块中关闭
- 所有注释和 UI 文案使用中文

## 注意事项

- `finance.db` 已加入 `.gitignore`，不提交到版本库
- Streamlit 每次交互会重新执行整个脚本，数据库连接不能跨请求持有
- `database.py` 中的查询函数每次调用都会新建连接，用完即关
