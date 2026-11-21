# 研究报告目录

## 命名

```
reports/<类型>/<公司或主题>-<YYYYMMDD>.md
```

日期是**数据截止日**，不是写作日。同一标的不同日期可以并存，不覆盖。

## 类型

| 目录 | 内容 | 产出 skill |
| --- | --- | --- |
| `company-research/` | 公司深度研究（13 节备忘录） | `company-research` |
| `financial-analysis/` | 单独的财报分析 | `financial-analysis` |
| `etf-analysis/` | ETF / 指数基金分析 | `etf-analysis` |
| `theses/` | 投资论点（含 diff 与决策日志） | `investment-thesis` |
| `portfolio-review/` | 组合复盘 | `portfolio-review` |

## 规则

- 新报告从 `_template/` 对应模板开始，不自定义结构。
- 报告头必须写数据截止日、币种、信息丰富度评级。
- 结论只允许四档：`通过` / `有条件通过` / `灰色地带` / `不通过`。
- 更新报告时保留旧版本；论点文件尤其不能覆盖。
- 报告里的每个关键数字都能追溯到 `data/` 或原始披露链接。
