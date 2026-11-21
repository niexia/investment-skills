# 数据源登记表

选源标准：**官方优先、免密钥优先、可复现优先**。每一项都标注了限制，使用前先看"注意"。

## 公司披露

| 来源 | 覆盖 | 访问方式 | 成本 | 注意 |
| --- | --- | --- | --- | --- |
| [SEC EDGAR](https://www.sec.gov/edgar/search/) | 美股全部申报文件 | 网页 + 全文检索 | 免费 | 需设置 `User-Agent`（姓名 + 邮箱），遵守 10 req/s 限制 |
| [SEC XBRL companyfacts](https://data.sec.gov/api/xbrl/companyfacts/) | 美股结构化财务 | JSON API，`CIK` 10 位补零 | 免费 | 字段名随 us-gaap 标签变化，需映射；不是所有公司都全 |
| [HKEXnews](https://www1.hkexnews.hk/index.htm) | 港股公告、年报、中报、月报表 | 网页检索 | 免费 | 无开放 API；PDF 为主，需自行解析；检索按"标题类别" |
| 公司 IR 网站 | 财报、演示材料、电话会记录 | 网页 | 免费 | 披露口径可能与交易所文件略有差异，以交易所文件为准 |
| [巨潮资讯](http://www.cninfo.com.cn/) | A 股（A+H 公司对照用） | 网页 | 免费 | 仅用于 AH 对照，不用于港股定价 |

## 行情与指数

| 来源 | 覆盖 | 访问方式 | 成本 | 注意 |
| --- | --- | --- | --- | --- |
| 券商/交易所行情 API | 美股、港股实时或延迟 | API | 多为免费或有条件 | 各券商条款不同，注意再分发限制 |
| Yahoo Finance（非官方） | 全球 | `yfinance` 等非官方库 | 免费 | **非官方**，可能限流或改接口；只用于辅助校验 |
| [HKEX 市场数据](https://www.hkex.com.hk/) | 港股成交、市值 | 网页/报表 | 免费 | 日终数据为主 |
| [S&P Dow Jones Indices](https://www.spglobal.com/spdji/) | S&P 系列指数 | 网页 | 免费（部分） | 指数编制方案需注册下载的情况较多 |
| [MSCI](https://www.msci.com/) | MSCI 系列指数 | 网页 | 免费（部分） | 同上 |
| [恒生指数公司](https://www.hsi.com.hk/) | 恒生系列、恒生科技 | 网页 | 免费 | 编制方案 PDF 可直接下载 |

## 宏观与利率

| 来源 | 覆盖 | 访问方式 | 成本 | 注意 |
| --- | --- | --- | --- | --- |
| [FRED](https://fred.stlouisfed.org/) | 美国宏观、汇率、利率 | 网页 + API | 免费，API 需免费密钥 | 序列有修订，记录 `vintage` 日期 |
| [US Treasury](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve) | 国债收益率曲线 | 网页/CSV | 免费 | 用 10Y 作为无风险利率基准时注明取数日 |
| [HKMA](https://www.hkma.gov.hk/) | 港元利率、汇率、银行数据 | 网页 + [API](https://api.hkma.gov.hk/) | 免费 | 部分数据集需申请 |
| 香港政府统计处 | GDP、通胀、零售 | 网页 | 免费 | 发布滞后 |
| [Damodaran 数据集](https://pages.stern.nyu.edu/~adamodar/) | 行业 β、ERP、行业倍数 | 网页下载 | 免费 | 年度更新，作为假设来源要注明版本年份 |

## ETF 与基金

| 来源 | 覆盖 | 注意 |
| --- | --- | --- |
| 基金公司官网（iShares、Vanguard、SSGA、南方东英、华夏等） | 持仓、TER、跟踪差异 | **唯一权威**；第三方网站常滞后 |
| 指数公司编制方案 | 选样、加权、调仓 | 决定暴露的本质 |
| 交易所 ETF 专区 | 成交、折溢价 | 港股 ETF 注意庄家机制 |

## 明确不用的来源

- AI 生成的"财报摘要"、聚合类财经 App 的结构化数据（无法追溯原始科目）。
- 未署名的行业规模数据（"据测算，市场规模将达 X 亿"）。
- 任何需要付费订阅、且条款禁止再分发的数据库导出内容。

## 使用规范

1. 引用格式：`（来源，文件/序列 ID，报告期，抓取日期，链接）`。
2. 同一指标尽量两个来源交叉验证，偏差 > 1% 必须解释。
3. 抓取日期与报告期是两个不同字段，都要写。
4. 发现数据源不可用或口径变更，更新本表并在 `docs/changelog.md` 记一笔。
