# workbuddy-points-radar

**WorkBuddy 积分雷达** —— 一个合规的积分领取助手 Skill：汇总全部积分渠道、追踪连签天数、每日早晚两次提醒手动领取、支持截图补录。

> ⚠️ **本 Skill 刻意不做"自动签到"**：所有领取动作由用户在客户端手动完成（约 10 秒），Skill 只承担提醒、记录与情报整理。

## 为什么没有"自动签到"

- WorkBuddy 官方服务协议第 9.2 条禁止破解技术保护措施抓取数据、禁止超出常规频率的自动化请求与批量操作，违规可限制功能甚至封禁账号（第 9.4 条）；
- 客户端 v5.6.2 起对本地登录态启用信封加密，读取 token 即踩红线；曾流行的开源 `workbuddy-checkin` 已于 2026-09-28 因合规风险下架；
- 官方开放平台不提供积分/签到状态查询 API，自动补录无合规通道。

因此本 Skill 的真实数据只来自两个合规来源：**用户口头确认** 或 **用户主动分享的客户端截图**。

## 功能

- ⏰ **每日早晚两次提醒**（WorkBuddy 自动化驱动）：早提醒"今天能领什么、连签风险"，晚催报"没记录就催"（连签倒计时 + 断签代价）；
- 📸 **截图补录**：发一张 Buddy加油站/派猫猫面板截图，自动提取连签天数/积分并记录（图中数据优先，可校准本地记录）；
- 📊 **连签追踪**：本地 CSV 流水，连签天数计算、漏领日期、周回顾、断签前预警（Buddy 加油站连签第 7 天 1000 积分大奖断签清零）；
- 🗺️ **积分渠道情报**：Buddy 加油站、派猫猫旅行、成长计划/任务中心、社区发文、邀请好友、每月免费额度，以及省积分技巧；
- 🔒 **零风险**：不调用任何接口、不读取登录态、不模拟点击、数据只存本地。

## 安装

**方式一：skills CLI（推荐，任何支持 Skills 的 Agent 平台）**

```bash
# GitHub 简写（自动发现 skills/ 下的 skill）
npx skills add Candace666/workbuddy-points-radar

# 或直接指定 skill 路径（官方文档格式）
npx skills add https://github.com/Candace666/workbuddy-points-radar/tree/main/skills/workbuddy-points-radar
```

**方式二：手动（任何平台）**

```bash
git clone https://github.com/Candace666/workbuddy-points-radar.git
cp -R workbuddy-points-radar/skills/workbuddy-points-radar ~/.workbuddy/skills/
```

安装后重启 WorkBuddy 或新开对话即可触发。

## 使用

### 1. 配置每日提醒（推荐）

在 WorkBuddy「自动化」中新建两个每日任务，prompt 直接抄 SKILL.md 的「工作流 A1（早提醒）/ A2（晚催报）」，建议时间 09:10 与 21:00。

### 2. 日常命令

```bash
python3 scripts/streak.py status                          # 今日状态 + 各渠道连签 + 大奖倒计时
python3 scripts/streak.py claim buddy-station             # 记录今日已手动领取
python3 scripts/streak.py claim buddy-station --date 2026-10-20 --note 截图补录   # 补录
python3 scripts/streak.py week                            # 本周领取记录 + 漏领日期
python3 scripts/streak.py channels                        # 列出已知渠道标识
```

渠道标识：`buddy-station`（Buddy 加油站）、`cat-travel`（派猫猫旅行）、`growth-task`（成长计划/任务中心）、`community-post`（社区发文）、`invite`（邀请好友）、`monthly-quota`（每月免费额度）、`other`（其他）。

### 3. 截图补录

把客户端积分/连签面板截图发给 WorkBuddy，它会读图提取连签天数与积分，自动 `claim --date` 补录；图中数据与本地记录不一致时以图中为准。

## 数据与隐私

- 领取记录仅存本地 `data/streak.log`（已在 .gitignore 中），永不上传；
- Skill 不访问网络、不读写登录态；
- 演练测试可设 `WB_POINTS_LOG=/tmp/xxx.log` 使用备用日志。

## 文件结构

本仓库采用 `skills/<skill-name>/` 多 skill 布局（[skills CLI 官方约定](https://github.com/vercel-labs/skills)），便于未来在同一仓库新增其他 skill：

```
workbuddy-points-radar/               # 仓库根目录
├── skills/
│   └── workbuddy-points-radar/       # ← skill 本体
│       ├── SKILL.md                  # Skill 入口（工作流与合规红线）
│       ├── references/
│       │   └── channels.md           # 积分渠道情报（规则/入口/收益/生态风险）
│       └── scripts/
│           └── streak.py             # 连签追踪工具（纯标准库，零依赖）
├── README.md
├── LICENSE
└── .gitignore                        # data/（领取记录）已忽略，永不上传
```

## 维护与同步

本仓库是 skill 的唯一源头。更新流程：

```bash
# 1. 在仓库内修改 skills/workbuddy-points-radar/ 下的文件
cd workbuddy-points-radar
git add . && git commit -m "..." && git push

# 2. 同步到本机已安装位置（WorkBuddy 实际加载的副本）
cp -R skills/workbuddy-points-radar/SKILL.md \
      skills/workbuddy-points-radar/references \
      skills/workbuddy-points-radar/scripts \
      ~/.workbuddy/skills/workbuddy-points-radar/
```

> `data/streak.log`（个人领取记录）不属于仓库内容，两个位置各自独立，互不影响。

## 免责声明

本 Skill 仅提供提醒、记录与公开情报整理，不参与、不协助任何形式的自动化签到。积分与活动规则以 WorkBuddy 官方当期页面为准；因违反官方服务协议产生的一切后果由使用者自行承担。

## License

MIT
