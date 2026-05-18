---
name: bug-helper
description: 禅道 bug 辅助
---

# 禅道 Bug 辅助

当用户提到禅道相关问题时，自动执行 bug 查询和分析。

**触发条件：**
TRIGGER when: 用户提到"禅道 bug"、"查看 bug"、"bug 分析"、"禅道上的问题"、"指派给我的 bug"等关键词

DO NOT TRIGGER when: 用户明确在执行其他开发任务，未提及 bug 或禅道

**前置配置：**
如果用户首次使用，提醒在项目根目录 `.env` 中配置：

```env
ZENTAO_URL=http://your-zentao/zentao
ZENTAO_TOKEN=your-token
ZENTAO_PRODUCT_ID=your-product-id
```

## 列出 Bug

当用户要求查看 bug 列表时：

1. 执行脚本获取数据：

```bash
python3 plugins/zentao/skills/bug-helper/scripts/bug-helper.py bug-list [limit]
```

2. 解析 JSON 输出，按以下格式展示：

Bug 列表 (产品: {productName})

| ID   | 标题  | 严重程度 | 优先级 | 状态  |
|------|-----|------|-----|-----|
| #123 | xxx | 主要   | P3  | 激活  |
| #122 | xxx | 次要   | P4  | 已解决 |

共 {n} 条

严重程度映射：1-致命 2-严重 3-主要 4-次要 5-建议

## 分析 Bug

当用户要求分析某个 bug 时：

1. 执行脚本获取详情：

```bash
python3 plugins/zentao/skills/bug-helper/scripts/bug-helper.py bug-detail <bug-id>
```

2. 如果返回的 JSON 中包含 `_images` 字段，用 Read 工具读取每张图片进行分析。

3. 按以下格式输出分析报告：

Bug #{id} 分析报告

**基本信息**

| 字段   | 值             |
|------|---------------|
| 标题   | {title}       |
| 产品   | {productName} |
| 模块   | {moduleTitle} |
| 严重程度 | {severity}    |
| 优先级  | P{pri}        |
| 状态   | {statusName}  |
| 指派给  | {assignedTo}  |

**问题描述**

{steps 清理 HTML 标签后的纯文本}

**截图分析**（如有）

{对截图的分析}

**问题分析**

{根据描述和截图分析可能的原因}

**建议修复方向**

1. {建议1}
2. {建议2}
