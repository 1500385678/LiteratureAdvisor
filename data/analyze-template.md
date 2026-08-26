# 文本精读模板 v1.0 · 5 维拆解

> 用途:对任意文学作品做**结构化精读**——输出可入库的 JSON / Markdown 卡片。
> 5 维:**结构 / 主题 / 语言 / 修辞 / 影响**。
> 落地:Phase 0 资产,Phase 1 `/analyze` 接口直接消费此模板。
> 版本:v1.0 · 2026-08-27

---

## 一、模板 Schema(JSON,可直接入库)

```json
{
  "work_id": "hongloumeng",
  "title": "红楼梦",
  "analyzed_at": "2026-08-27",
  "analyzer": "08-文学-Literature",
  "dimensions": {
    "structure": {
      "form": "章回小说",
      "narrative_pov": "全知视角 + 限知视角穿插",
      "timeline": "由盛而衰,草蛇灰线",
      "chapters_or_parts": "120 回(前 80 回曹雪芹,后 40 回高鹗续)",
      "structural_features": ["网状结构", "伏笔千里", "诗化叙事"]
    },
    "themes": {
      "primary": ["爱情悲剧", "家族衰落"],
      "secondary": ["人生无常", "女性命运", "儒释道交融"],
      "thesis": "繁华到虚空的挽歌,以情悟道"
    },
    "language": {
      "register": "文白相间,诗词穿插",
      "dialect": "北方官话为主,夹吴语",
      "lexicon_features": ["诗词化对白", "判词伏笔", "谐音寓意"],
      "style_period": "古典白话巅峰"
    },
    "rhetoric": {
      "figures": ["比喻(葬花)", "象征(石头/花/镜)", "反讽(好了歌)"],
      "symbols": ["通灵宝玉(本质)", "大观园(理想)", "金陵十二钗(命运)"],
      "irony": "盛筵必散,月满则亏"
    },
    "impact": {
      "literary_history": "中国古典小说巅峰,百科全书式作品",
      "cross_cultural": "红学成为国际显学,影响东亚文学数百年",
      "modern_influence": ["张爱玲继承", "白先勇续书", "当代影视改编母本"]
    }
  },
  "score": {
    "structure": 9.5,
    "themes": 9.8,
    "language": 9.7,
    "rhetoric": 9.6,
    "impact": 10.0,
    "overall": 9.7
  }
}
```

---

## 二、5 维字段说明

| 维度 | 必填字段 | 选填字段 | 评分依据(0-10) |
|------|----------|----------|----------------|
| **结构 structure** | form / narrative_pov / timeline | structural_features / chapters_or_parts | 完整性、内部逻辑、节奏控制 |
| **主题 themes** | primary / thesis | secondary | 深度、层次、普世性 |
| **语言 language** | register / style_period | dialect / lexicon_features | 精确性、表现力、美学高度 |
| **修辞 rhetoric** | figures / symbols | irony | 创新性、契合度、复现密度 |
| **影响 impact** | literary_history | cross_cultural / modern_influence | 史定位、传播广度、衍生力 |

---

## 三、评分口径

- **9.0-10.0**:开宗立派/百科全书级(《红楼梦》《追忆似水年华》)
- **7.5-8.9**:经典一流(《平凡的世界》《百年孤独》)
- **6.0-7.4**:优秀之作,值得精读
- **4.5-5.9**:可读但需选读
- **< 4.5**:不入精读库

---

## 四、使用流程(Phase 1 接入)

```
作品(work_id)
  ↓
LLM 装载本模板 + 作品全文
  ↓
按 5 维逐项生成
  ↓
score 加权(结构 20% + 主题 25% + 语言 20% + 修辞 15% + 影响 20%)
  ↓
入库 data/analyzes/{work_id}.json
```

---

## 五、变更记录

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-08-27 | v1.0 | 初版 5 维 Schema + 评分口径 + 红楼梦示例;Phase 0 资产就位 |

---

> **入库路径**:`data/analyze-template.md`(本文件)
> **消费方**:Phase 1 `/analyze` 接口(待建)
> **维护方**:08-文学-Literature 顾问
