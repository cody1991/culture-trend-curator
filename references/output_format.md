# Output Format

## Digest Structure

Use this structure by default:

```markdown
# 本周书影趋势推荐

> 策展口径：近 30 天公共热度 + 年度榜单 + 长期评分 + 多来源交叉验证。书籍以中文可读为主；影视以中文可看/可讨论为主，并保留 1 个全球影史经典补课位。

## 书籍

### 1. 《标题》 — 作者
- 类型：文学 / 历史 / 科幻 / 非虚构
- 推荐理由：一句话说明为什么值得读。
- 为什么现在读：近期上榜、获奖、讨论变多、新译本、影视化等。
- 质量信号：评分、评分人数、榜单来源、媒体推荐。
- 风险提示：节奏慢、门槛高、题材压抑、篇幅长等。
- 链接：URL

## 影视

### 1. 《标题》 — 导演/主创
- 类型：电影 / 剧集；剧情 / 悬疑 / 纪录片等。
- 推荐理由：一句话说明为什么值得看。
- 为什么现在看：热播、完结、获奖、流媒体上线、口碑发酵等。
- 质量信号：评分、评分人数、榜单来源、媒体评价。
- 中文可看/可讨论性：中文片名、中文评论/讨论、流媒体/院线/影迷社群可见度。
- 风险提示：节奏慢、暴力、压抑、门槛高、烂尾风险等。
- 链接：URL

## 本期观察

- 2-4 条总结公共趋势，例如“女性叙事升温”“历史非虚构热度延续”。

## 被排除但值得关注

- 可列 2-3 个热度高但质量证据不足的项目，说明为什么暂不推荐。
```

## Tone

Use concise editorial language. Avoid hype words unless backed by evidence. Prefer “值得关注”“适合补课”“口碑稳定” over “神作”“必看”.

## Evidence Requirements

Each recommended item should include at least two signals where possible:

- A recent trend/list signal.
- A quality signal such as rating, critic consensus, award, or repeated source endorsement.

If only one signal exists, explicitly mark it as exploratory.

## Notification Version

For WeCom, Slack, or short push notifications, compress to:

```markdown
# 本周书影推荐

## 书
1. 《标题》：推荐理由；风险提示。
2. 《标题》：推荐理由；风险提示。

## 影
1. 《标题》：推荐理由；风险提示。
2. 《标题》：推荐理由；风险提示。

完整来源与候选池见报告文件。
```
