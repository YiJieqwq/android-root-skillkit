---
name: android-root-skillkit
summary: Android Root/玩机安全一体化 skillkit，合并原 android-root-basics、android-bricker-defense、android-root-commercial-hardening：术语与选型、环境隐藏与证明链、格机威胁与防御、商业闭源 App/KPM 加固设计。
description: 当任务涉及 Android Root、玩机、Magisk、KernelSU/KSU、SukiSU-Ultra/SKU、APatch、FolkPatch、KernelPatch/KPM、LKM/built-in/GKI、SUSFS、Zygisk/LSPosed、NoHello、SELinux 隐藏、DirtySepolicy、TrickyStore、TEESimulator-RS、Play Integrity、管理器/模块选型、格机/防格/bricker/wiper、恶意 Root 程序、防格 KPM、Root 安全工具、真机恶意样本实验室、威胁模型评审、商业闭源 App 或付费 KPM 加固、商业壳/VMP、服务器 Grant、设备指纹、Watchdog/Main KPM、授权与破解对抗时使用。提供防御、分析和安全设计知识；不生成可直接用于破坏真实设备的代码或操作步骤。
---

# Android Root Skillkit：玩机安全套件

> 由三个 skill 合并：android-root-basics（术语/选型/隐藏）+ android-bricker-defense（格机威胁与防御）+ android-root-commercial-hardening（商业 App/KPM 加固）。
> **时点基线：2026-08-08**。涉及版本、功能是否内置、最近检测等事实，必须联网核对上游源码/PR/Release/作者官方频道；本文件不是永久事实。

## 使用路由

先判断任务属于哪个域，再读取对应深度文件：

| 域 | 任务特征 | 深度文件 |
|---|---|---|
| 术语/选型/隐藏 | 解释架构、管理器/模块选型、SUSFS、NoHello、SELinux hide、Key Attestation | `basics/concepts.md`、`basics/selection-and-hiding.md` |
| 格机威胁/防格 | 格机/bricker/wiper、全天候防格、针对性分析、恶意样本、威胁模型评审 | `bricker-defense/threats.md`、`bricker-defense/defense-architecture.md` |
| 商业加固 | 商业闭源 App/KPM 的授权、设备绑定、加密拟合、壳/VMP、验收 | `commercial-hardening/root-device-hardening-template.md`、`commercial-hardening/review-checklist.md`、`commercial-hardening/solution-outline.md` |

简单问题可直接按下方速查回答；涉及深度设计/评审时必须读取对应文件。

## 标准执行流程

1. 判断任务属于 basics、bricker-defense、commercial-hardening 或跨域任务；
2. 收集会改变结论的设备、Android、内核、Root 实现、安装模式、产品类型和用户目标；信息不足时先提问；
3. 读取对应深度文件，不加载无关模块栈；
4. 将结论区分为稳定架构事实、版本相关事实、默认建议和未验证渠道信息；
5. 对版本、PR、功能是否内置、模块兼容性和发布渠道进行联网核对；
6. 来源优先级：目标分支源码/运行构建 > 上游 PR/commit > 官方 Release > 官方文档 > 作者频道 > 社区测试 > 二手教程；
7. 先输出结论，再说明依赖、风险、替代方案、核对时点和不确定项。

## 共享基础：总体分层

```text
启动镜像/ramdisk 层
├── Magisk：修补 ramdisk，植入 magiskinit
└── KSU/SKU LKM：修补 ramdisk，早期加载 kernelsu.ko

内核 Root/补丁层
├── KSU/SKU built-in：代码编进内核
├── KSU/SKU LKM：运行时加载 .ko
└── KernelPatch：二进制内核修补、SuperCall、KPM 运行基础

用户空间管理与模块层
├── Magisk / magiskd / Magisk 模块
├── KSU/SKU / ksud / KSU 模块 / Meta Module
└── AP/FP / apd/fpd / APM

内核扩展层
├── KPM：KernelPatch Module，*.kpm
└── LKM：标准 Loadable Kernel Module，*.ko

进程注入层
├── Zygisk / ZygiskNext
├── LSPosed
└── Xposed 模块（不等于内核模块）

隐藏与证明层
├── KSU/SKU SELinux hide：策略/context oracle
├── SUSFS：路径、挂载、kstat、uname/cmdline 等内核视图
├── NoHello KPM：主要用于 AP/FP 的路径/环境痕迹
├── selinux_hook.kpm：AP/FP 对抗新型 SELinux oracle
├── HMA-OSS：当前版直接 Zygisk 模块，用于应用列表/设置等隔离，不再依赖 LSPosed
└── TEESimulator-RS/TrickyStore：Key Attestation/证书链，不等于 Root 隐藏
```

## 共享术语锚点

- “Root 管理器”= Manager APK + 底层实现 + 守护进程 + 授权库 + 模块系统，严格分析时拆开；
- `boot/init_boot` 是容器/分区，Magisk 实际修补的是其中的 **ramdisk**（Android 13+ 多在 init_boot）；
- **built-in ≠ “GKI 模式”**：built-in 是集成方式，GKI 是内核架构；非 GKI 内核同样可 built-in；
- KPM 运行于内核空间（EL1），`.ko` 是标准 LKM，Zygisk/Xposed 模块在用户空间，不能互称；
- **SuperKey** 是 KernelPatch/APatch SuperCall 及相关特权控制面的认证秘密，是 KPM 管理链的重要信任根，但不等于整个 EL1 的完整安全边界；审查快照中的 KPatch-Next 以 UID 0 作为 SuperCall 门槛，与 SuperKey 模型不等价；
- NoHello 主流 KPM 仅在作者 Telegram 频道发布（带版本+哈希，如 `Nohello-v1.0.0-13-6106b0a-release.kpm`），GitHub 同名 Zygisk 项目不是其上游；
- SUSFS 是“内核补丁 + 用户空间控制”，未打补丁的内核装 ZIP 无效；
- TEESimulator-RS 与 TrickyStore 处理 Key Attestation，通常二选一，不解决 Root 路径/SELinux/包名隐藏。

## 域一速查：术语与选型（深度：basics/）

1. 用户说“修补 boot/init_boot”时，指出实际修改对象可能是其中的 ramdisk 或 kernel Image。
2. 用户说“GKI 模式”时，理解社区常指 built-in，但注明这不是严格术语。
3. 推荐管理器前判断：内核、Android 版本、是否小白、是否日用隐藏、是否需要 KPM、编译能力、是否重视 SuperKey。
4. “日用”默认考虑环境隐藏，但不承诺“绝对/完美不可检测”。
5. 讨论 KPatch-Next 必须评估删除 SuperKey 验证后的信任边界。
6. NoHello KPM 默认面向 AP/FP；KSU/SKU 无相同检测面时不要推荐。
7. SUSFS 先确认运行内核已打补丁。
8. TEES-RS/TrickyStore 处理 Attestation，不替代 SELinux/挂载/包名隐藏。
9. KSU/SKU 是否内置 SELinux hide、SKU KPM 自动加载等必须按当前源码/Release 复核。
10. 作者仅 TG 发布的模块，明确发布渠道与可审计性，不把 GitHub 同名项目当上游。

```text
新旗舰 + 小白 + 日用：优先官方 KSU LKM
老内核测试靶机 + 不隐藏：优先 Magisk
KSU 显示 `Unsupported`：当前运行内核/官方直接安装路径不受支持；仍可自行编译 built-in 或刷可信适配内核，但不能简化为“仅自动修补失败”
开发者 + 主力机 + KPM + 日用：优先 APatch/FolkPatch，重视 SuperKey
KSU LKM 日用隐藏：启用 SELinux hide；按需 TEES-RS + Zygisk provider + HMA-OSS；只有其他 Xposed 需求才加 LSPosed
KSU/SKU built-in 深度隐藏：内核必须有 SUSFS 补丁
AP/FP 日用隐藏：按实际检测面评估 NoHello KPM 与 DirtySepolicy 缓解；按需 TEES-RS + Zygisk provider + HMA-OSS；只有其他 Xposed 需求才加 LSPosed
```

以上只是默认决策，不替代设备级兼容性核对。

## 域二速查：格机与防格（深度：bricker-defense/）

**两类产品**：

- A. 全天候防格：常驻、窄而可靠地保护启动链/分区表/关键固件/persist 等真实资产；不全局禁止块设备访问；有认证限时维护窗口；自身不能成为 bootloop 来源。
- B. 针对性分析/围堵：用户显式注册目标，追踪血统与异步请求，危险操作模拟成功，导出证据；不默认应用到整台日用设备。

**典型载荷形态**：自解压 sh 包装 + 内嵌 ELF → 解压到 /data/local/tmp、/cache、$TMPDIR → chmod +x → root 执行。黑名单只看到 sh，破坏者是 ELF；归因追踪 sh→ELF 的 exec 血统；最终防线看真实资产的 I/O 落点。

**核心原则**：资产中心不是命令中心；最终落点保护与因果归因分离；分层拦截（打开→VFS→block/BIO 兜底→模块入口→系统服务→恢复）；区分会话策略 `TRACE/AUTO/STRICT/EXPERT`、策略决策 `PASS/SIMULATE/SUPPRESS/ALERT/VERIFY/RECOVER` 和执行结果；维护授权作用域化（身份+资产+操作+时限+启动会话）；同权限域（EL1）不承诺绝对安全。

**基础回答顺序**：列真实资产 → 按 dev_t 归一化别名 → 拒绝未授权写打开关键块设备 → 补 ioctl/fallocate/mmap/异步 → 关键资产 block/BIO 兜底 → 防系统服务/内核扩展转移 → 认证维护窗口兼容 OTA → 审计/完整性/恢复材料 → 样本分析才启用会话与模拟成功 → 测试只用 loop 虚拟块设备。

## 域三速查：商业加固（深度：commercial-hardening/）

**适用前提**：本域只讨论从产品定义开始就专门面向 Root/玩机用户的商业付费软件，不适用于普通消费者 App、银行/支付 App，或仅希望兼容少量 Root 用户的一般应用。目标用户被假定为理解刷机、换内核和模块变更的后果，并接受严格设备绑定、指纹漂移后拒绝签发、官网手动解绑、解绑冷却期和必要的人工复核。由用户主动玩机行为触发的假阳性属于已接受的产品取舍，不自动视为设计缺陷。

**先分类（决定是否允许用 KPM）**：

- A. Root 玩家付费用户空间软件（核心功能不在 KPM，数量最多）：服务器授权 + 严格设备绑定 + 资产级 AEAD + 签名 Grant + 壳/VMP。默认不要求用户安装 KPatch-Next/APatch/FolkPatch 等内核组件。
- B. 产品本身就是付费内核模块（少数）：付费 KPM 产品很少；**内核级校验（Watchdog/Main KPM）是拓展方案，不是默认**；卖的不是 KPM 却要求用户加载 KPM 属强人所难（多数 Root 用户跑 Magisk/KSU 用户空间栈，没有 KPM 加载链）。默认采用仅当：① 核心功能本身就是内核模块/需 EL1；② 目标用户具备 KPM 能力且自愿；③ 能维护多内核版本稳定性。
- C. Root 安全分析工具：评审低层数据面、session/lineage、控制面认证、证据完整性、fail-closed、异步归属缺口。

**加密 + 拟合**：加密让未授权者缺少不可替代的数据（皇冠能力留服务器、本地密文、只向当前设备/版本签发）；拟合让攻击者必须重建跨 Grant→设备绑定→会话→UI→Native→资产子密钥→真实功能的串行状态。避免所有检查汇聚到同一个 `licenseVerified`。

**工作流**：收集事实 → 画当前架构与最短攻击链 → 设计目标架构（服务端签名→设备绑定→资产加密→业务真实消费→拟合→壳→可选 KPM→运行时擦除）→ 路线图 → 反向攻击验收（强制 UI 成功但功能不可用、跳过服务器拿不到密钥、A 设备材料不能用于 B、去壳断链、无 fallback、密钥可轮换）。

## 安全边界（所有域共用）

- 只提供防御、分析和安全设计知识；不输出针对真实设备的破坏脚本、可执行分区清零流程或绕过防护的实战载荷；
- 不承诺“绝对不可检测/不可破解/绝对防格”；明确 EL1/EL2/TEE/RPMB 等信任域边界；
- 不编造私有 Telegram 模块源码、Hook 点或安全机制；
- 商业加固场景不把破解版产物作为交付目标，可分析攻击链并转化为防御验收。

## 输出要求

- 先给明确结论，再解释依赖和边界；
- 使用“严格术语 + 社区俗称”双重表述；说明每个模块依赖谁、运行于内核还是用户空间、解决什么、不解决什么；
- 区分“管理器 App 已更新”和“运行中的内核/LKM 已更新”；
- 避免堆叠无需求模块（每加一个内核补丁/Zygisk/LSPosed 组件都增加攻击面与检测面）；
- 涉及最新事实时优先官方仓库源码/PR/Release/官方频道，社区教程只能作为线索。

## 时效性核对锚点

```text
□ Manager APK 与内核 Root 驱动/LKM 版本、built-in/LKM 模式
□ KSU/SKU SELinux hide 是否编入并开启（PR #3457/#3459/#3495 是否存在）
□ SUSFS 内核补丁与用户空间工具版本匹配
□ SKU KPM：核对 `kernel/kpm/`、`userspace/ksud/src/kpm.rs`、启动事件与 Manager Embed 路径；审查快照已具备 `/data/adb/kpm/*.kpm` 开机加载
□ AP/FP KernelPatch 与 SuperKey 行为；KPatch-Next 是否仍删除 SuperKey 验证
□ NoHello KPM 作者官方 TG 版本与哈希；TEESimulator-RS/TrickyStore 冲突与兼容
□ Duck Detector/DirtySepolicy 检测项当前覆盖面
```

一手来源与审查 commit 统一记录在仓库根目录的来源清单（SOURCES.md）。DirtySepolicy 时间线应区分 LSPosed 声称的 2024-08 私下发现与 Duck Detector 在 2026-05 的公开实现锚点，不做无法独立证明的绝对首创裁定。
