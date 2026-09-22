# android-root-skillkit

[English](README.md) | **中文**

面向 AI 助手的 Android Root / 玩机安全知识与审查 Skillkit。

它将三个相关领域合并为一个带路由的 Skill：

1. **Root 基础、选型与隐藏**：Magisk、KernelSU、SukiSU-Ultra、APatch、FolkPatch、KernelPatch/KPM、LKM/built-in/GKI、SUSFS、Zygisk、DirtySepolicy、Attestation 等；
2. **格机威胁与防御**：资产中心防护、最终 I/O 落点、会话与因果归因、维护窗口、证据和恢复边界；
3. **Root 玩家付费软件加固**：服务器签名 Grant、严格设备绑定、资产加密、运行状态拟合、壳/VMP，以及仅在确有 EL1 需求时采用的 KPM 方案。

## 重要范围说明

商业加固部分只适用于：

> 从产品定义开始就专门面向 Root/玩机用户的商业付费软件。

它不适用于普通消费者 App、银行/支付 App，也不适用于仅希望兼容少量 Root 用户的一般应用。

该目标群体被假定为理解刷机、换内核、安装模块和系统升级可能改变设备身份，并接受：

- 严格设备信息绑定；
- 指纹漂移后 fail-closed；
- 登录官网手动解绑；
- 解绑冷却期、频率限制和必要的人工复核。

因此，由用户主动玩机行为触发的假阳性是明确接受的产品安全取舍，而非自动视为设计缺陷。

## 目录

```text
android-root-skillkit/
├── SKILL.md
├── basics/
│   ├── concepts.md
│   └── selection-and-hiding.md
├── bricker-defense/
│   ├── threats.md
│   └── defense-architecture.md
└── commercial-hardening/
    ├── root-device-hardening-template.md
    ├── review-checklist.md
    └── solution-outline.md
```

构建产物位于：

```text
dist/android-root-skillkit.skill
```

`.skill` 是包含 `android-root-skillkit/` 根目录的 ZIP 文件。

## 使用

将 `dist/android-root-skillkit.skill` 导入支持 Skill 的 AI 客户端，或直接把 `android-root-skillkit/` 目录放入客户端的 Skills 目录。

涉及版本、功能是否内置、检测面和模块兼容性的回答，必须重新核对目标版本的上游源码、PR、Release 或作者渠道。`SOURCES.md` 只记录本次正式审查的快照，不是永久事实。

## 安全边界

本项目提供防御、分析、架构评审和安全设计知识，不提供针对真实设备的破坏代码或可执行分区清零流程，也不承诺：

- 绝对不可检测；
- 绝对不可破解；
- 绝对无法格机；
- 能抵抗任意恶意 KPM、任意内核执行、EL2/TEE/RPMB、存储固件或物理攻击。

防格实验只应使用 disposable loop/虚拟块设备。

## 审查说明

内容曾由 AI 辅助整理，但在 2026-08-08 公开发布前，对主要版本敏感结论进行了上游源码复核。审查 commit 和已知边界见 [`SOURCES.md`](SOURCES.md) 与 [`CHANGELOG.md`](CHANGELOG.md)。

## License

[MIT](LICENSE)
