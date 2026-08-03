# Output Format

## Digest Structure

Use this structure by default:

```markdown
# 本周书影趋势推荐

> 策展口径：近 30 天公共热度 + 年度榜单 + 长期评分 + 多来源交叉验证。书籍以中文可读为主；影视以中文可看/可讨论为主，并保留 1 个全球影史经典补课位。

## 书籍

### 1. [《标题》](https://book.douban.com/subject/ID/)｜作者
> 作品档案｜出版：YYYY｜豆瓣：8.8（32,598 人评价）｜类型：文学 / 历史 / 科幻 / 非虚构

第一段写作品如何成立：叙述角度、结构、语言、人物关系或一个可感知的细节。

第二段写它在本周为什么值得读；把榜单、讨论或长期口碑作为判断底色，不要把评分信息再写成流水账。

提示：节奏、题材或阅读门槛。

## 影视

### 1. [《标题》](https://movie.douban.com/subject/ID/)｜导演/主创
> 作品档案｜上映：YYYY｜豆瓣：8.8（329,186 人评价）｜类型：电影 / 剧情 / 家庭

第一段写镜头、表演、剪辑、声音或叙事安排如何工作。

第二段写它与本期主题的关系，以及中文语境里的观看理由。

提示：节奏、题材或观看门槛。

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
- A verified canonical Douban link on the title. Every normal pick must be at least 8.5 with 2,000+ book ratings or 10,000+ film/TV ratings.

At most one item in the whole issue may be labelled `新作观察位`; it must still clear 8.2 and the lower 500/2,000 rating floors. If none qualifies, do not create an observation slot.

If only one signal exists, explicitly mark it as exploratory.

## Notification Version

For WeCom, Slack, or short push notifications, compress to:

```markdown
# 本周书影推荐

## 书
1. [《标题》](URL)（槽位）：推荐理由；稳定性/风险一句话。
2. [《标题》](URL)（槽位）：推荐理由；稳定性/风险一句话。

## 影
1. [《标题》](URL)（槽位）：推荐理由；稳定性/风险一句话。
2. [《标题》](URL)（槽位）：推荐理由；稳定性/风险一句话。

完整来源与候选池见报告文件。
```

For group messages, keep each item to 2-3 lines unless the user asks for a long report.
