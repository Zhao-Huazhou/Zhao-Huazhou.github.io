---
title: "如何用一顿火锅的钱，运行一个 7x24 小时帮你干活的 AI 助手"
date: 2026-03-15T10:30:00+08:00
author: "Andy"
draft: false
tags: ["OpenClaw", "AI"]
---

不到一顿火锅的钱，养一只 7×24 小时在线打工的 🦞

把我的配置经验整理了一下，希望能帮到想入坑的你 🚀

---

## 1. 云服务器

一开始，我在自己的 MacBook Air 上体验了 OpenClaw。但考虑到 7×24 小时运行的需求，最终还是决定租一台云服务器。

反复对比之后，我选择了 **火山引擎·香港**：
- 配置：2核4G
- 价格：约 ¥99/月

2G 内存虽然更便宜，但实测跑 agent-browser skill 时会爆内存，因此调大了一点内存。

**香港服务器的优势**：
- **默认自带翻墙，能直连 Github、Google、Clawhub**
- 但由于是机房 IP，OpenAI、Anthropic、Gemini API 会被墙
- 这个问题不大，可以通过 [WildCard](https://gptsapi.net/) 解决

我之前尝试过用国内服务器 + Clash 订阅代理，但在安装 OpenClaw 下载 git、node 时就遇到了 502 Bad Gateway，估计和云服务器的网络配置有些冲突。于是思来想去，为了省心就直接选香港服务器了——事实上效果确实让我省心很多。

**相关链接**：
- [火山引擎香港实例购买](https://console.volcengine.com/ecs/region:ecs+cn-hongkong/buy)

---

## 2. Minimax Coding Plan

![Minimax Coding Plan](./minimax-coding-plan.webp)

推荐先用最低版 **¥29/月** 的套餐体验一下，后续按需提升。

**相关链接**：
- [订阅套餐](https://platform.minimaxi.com/subscribe/coding-plan)
- [Coding Plan API Key](https://platform.minimaxi.com/user-center/payment/coding-plan)

---

## 3. 原生安装 OpenClaw

这里不太推荐使用云服务器厂商的应用模板，配置起来不爽。

直接使用官方原生安装方式就好，香港服务器配上 200Mbps 带宽，安装起来很快。

```bash
# Linux/MacOS
curl -fsSL https://openclaw.ai/install.sh | bash
```

按步骤配置即可。**注意跳过 OpenClaw 内置的飞书配置！**

### 3.1 配置 Brave Search

Brave Search 是给 🦞 用的 Web Search 工具，每个月都有免费额度，足够体验使用。

**缺点**：开通订阅时需要绑定美国信用卡。**建议找闲鱼代绑**，30 元以内解决。

#### 获取 API 密钥
1. 在 [Brave Search API](https://brave.com/search/api/) 创建账户
2. 在控制面板中选择 "Data for Search" 套餐并生成 API 密钥
3. 将密钥配置到 OpenClaw 中

配置示例：
```json
{
  "tools": {
    "web": {
      "search": {
        "provider": "brave",
        "apiKey": "你的BRAVE_API_KEY",
        "maxResults": 5,
        "timeoutSeconds": 30
      }
    }
  }
}
```

**参考**：[Brave Search 文档](https://docs.openclaw.ai/zh-CN/brave-search)

---

## 4. 安装 OpenClaw 飞书官方插件

不要用 OpenClaw 内置的飞书 channel，用飞书官方插件，体验真的很赞。

在命令行终端中，执行以下安装指令。

```SHELL
# 安装飞书官方插件
npx -y @larksuite/openclaw-lark-tools install
```

验证是否安装成功：在飞书对话中发送 `/feishu start`。  
若返回了版本号信息，则代表安装成功。

用 `/feishu auth` 一键完成授权，后续让 OpenClaw 使用云文档、多维表格都畅通无阻。

**参考**：[飞书官方插件文档](https://bytedance.larkoffice.com/docx/MFK7dDFLFoVlOGxWCv5cTXKmnMh)

---
## 5. 接入企业微信（含个人微信互通）

### 5.1 安装 wecom 插件

``` bash
# 安装插件
openclaw plugins install @yanhaidao/wecom
openclaw plugins enable wecom
```

### 5.2 互动向导式配置（推荐）

在终端中执行：

``` bash
# 添加 IM 渠道
openclaw channels add
```

然后按提示进行操作：

-   在 **Select channel** 选择：`WeCom (企业微信)`
-   企业微信 **接入标识** 选择：`default`

### 5.3 两种不同的接入模式


**方式一：智能机器人（简单快速）**

适合快速体验，几分钟就能跑通。

1.  登录[企业微信管理后台](https://work.weixin.qq.com/wework_admin/loginpage_wx)

2.  进入 **安全与管理 → 管理工具 → 智能机器人**

3.  创建机器人：
    -  选择：**手动创建 - API 模式创建**
    -  填写名称、简介，设置可见范围
    -  连接方式选择：**长连接**
    -  获取 `Bot ID` 和 `Secret`

4.  回到 [向导式配置](#52-互动向导式配置推荐)：
    -  接入模式选择：**Bot 模式**
    -  填入 `Bot ID` 和 `Secret`

5.  完成配置后，重启 OpenClaw Gateway：

``` bash
# 重启 OpenClaw Gateway
openclaw gateway restart
```

然后在企业微信里给机器人发消息，就能收到 AI 回复了。

**方式二：自建应用（支持个人微信互通）**

自建应用相比智能机器人，支持的功能更多：

| 功能           | 智能机器人 | 自建应用 |
|----------------|------------|----------|
| 接收/回复文本  | ✅         | ✅       |
| 接收语音       | ✅         | ✅       |
| 接收图片       | ✅         | ✅       |
| 回复图片       | ❌         | ✅       |
| 回复文件       | ❌         | ✅       |
| 主动发送消息   | ❌         | ✅       |
| 个人微信互通   | ❌         | ✅       |


**第一步：创建自建应用**

1. 企业微信管理后台 → **应用管理 → 创建应用**

2. 设置应用 Logo、名称、可见范围

3. 创建完成后，记录以下关键参数：

| 参数                     | 获取位置 |
|--------------------------|----------|
| Corp ID（企业 ID）       | 我的企业 → 企业信息 → 页面底部 |
| Corp Secret（应用密钥）  | 应用详情 → Secret → 查看 → 发送到企业微信 |
| Agent ID（应用 ID）      | 应用详情页，与 Secret 同一位置 |
| Token                    | 应用详情 → 功能 → 接收消息 → 设置 API 接收 → 随机生成 |
| EncodingAESKey           | 同上，随机生成 |

**第二步：配置 OpenClaw**

在刚才的[向导式配置](#52-互动向导式配置推荐)中：
-  接入模式选择：**Agent 模式**
-  依次填入上面 5 个参数

**第三步：配置回调 URL（重点！）**

> **注意：必须先在 OpenClaw 配置完 5 个参数后，再保存回调 URL，否则会失败！**

在应用的「接收消息」设置中填写 API 回调 URL：

`http://你的服务器IP:18789/plugins/wecom/agent/default`

**常见坑点排查**：
1.  需要放行服务器的 `18789` 公网入站端口
2.  可能需要编辑 `~/.openclaw/openclaw.json` 中的 `gateway.bind` 为 `lan`
3.  其他问题建议直接丢给 AI 处理

**第四步：配置可信 IP**

在应用详情页底部找到「企业可信 IP」，填入你的服务器公网 IP。

**第五步：重启 OpenClaw Gateway**

``` bash
# 重启 OpenClaw Gateway
openclaw gateway restart
```

**第六步：开通个人微信互通（杀手级功能！）**

这是很多人最期待的功能——让个人微信也能用上 AI 助手！

1. 在企业微信管理后台 → **我的企业 → 微信插件**
2. 扫描二维码，将企业应用添加到个人微信
3. 完成后，你在个人微信中就能看到该应用，直接发消息给它即可

> **注意**： 通过微信插件访问的应用只支持一对一私聊，不支持拉入微信群。因为它本质上是企业微信的应用，而非微信好友。

**参考**：
- [YanHaidao/wecom](https://github.com/YanHaidao/wecom)
- [OpenClaw 接入微信、钉钉、飞书、QQ 详细教程来啦！](https://zhuanlan.zhihu.com/p/2013706717012186762)

## 6. 设置 tools.profile 为 full / coding 模式

因为我这是独立隔离的服务器，所以直接省心用 full 模式玩了，谨慎点也可以使用 coding 模式。

编辑 `~/.openclaw/openclaw.json`，将 `tools.profile` 设置为 `full` / `coding`即可。

**参考**：[Tools 文档](https://docs.openclaw.ai/zh-CN/tools)

---

## 和 🦞 对话吧！

现在就可以开始养龙虾啦！

后续可以自己凭兴趣下载些 Skill 玩玩：[ClawHub](https://clawhub.ai/)

个人推荐：
- **aliyun-asr**：接入阿里云 ASR API 实现语音识别，然后就可以用语音和你的 🦞 对话了。能听懂你说的话（但还不能说话）。个人感觉阿里云 ASR 比 Whisper 好用——本地运行 Whisper 挺吃配置，效果也不如 API
- **weather-zh**：中文天气查询工具，使用中国天气网获取实时天气（无需 API 密钥，不依赖大模型），输出格式也非常不错，会提供各种生活指数，如紫外线、穿衣建议、运动指数、洗车指数等
- **agent-browser**：贼好玩，让 Agent 像打工人一样刷网页干活。之前用 2 核 2G 内存的时候，让它给我的 GitHub 项目点个赞，结果把内存炸了 🤭

---

## 写在最后

OpenClaw 确实是一个让人眼前一亮的项目。

也许它就是下一个时代的 Android 呢？

玩得开心 🎉

<div style="text-align: right">
<em>本文编辑：🦞 Andy</em>
</div>
