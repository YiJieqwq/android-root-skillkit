# 选型、隐藏、SUSFS 与证明链

## 1. 默认选型

### 新旗舰、小白、日用

若设备处于官方支持状态、GKI/KMI 与 LKM 条件匹配，优先评估官方 KSU LKM：它通常可保留厂商内核主体，更新路径也较直接。确认当前 LKM 实际包含最新版 SELinux hide；只更新 Manager APK 不等于更新了运行中的 `.ko`。

### 老内核测试靶机、不考虑隐藏

优先 Magisk：兼容和生态广，安装简单，适合调试。若目标本身是 KSU/KP 研究，再选定制内核或 AP/FP。

### KSU 显示“不支持”

Manager 显示 `Unsupported`，表示当前运行内核未被识别为官方支持的 KernelSU 环境，不能简化成“仅自动修补失败”。仍可根据设备条件：

1. 刷适配 KSU/SKU 内核；
2. 用内核源码手动 built-in；
3. 在适用设备上刷匹配 GKI/KMI 构建；
4. 在满足 GKI/KMI、模块配置和签名/符号条件时，由开发者适配 LKM。

官方状态中，`Not installed` 才表示设备受官方支持但尚未安装。

### 开发者、主力机、需要 KPM 和日用

优先 APatch/FolkPatch，而不是默认 SKU built-in：

- SuperKey 给 KPM 操作提供独立信任根；
- 防止“已获普通 Root = 可随意加载 EL1 KPM”；
- 不必同时维护 SKU + 裁剪 KP + SUSFS 的复杂自编译内核；
- AP/FP 的现成 KPM 管理/自动加载体验通常更完整。

默认搭配：

```text
AP/FP
+ NoHello KPM
+ selinux_hook.kpm
+ 按需 TEESimulator-RS
+ 按需 ZygiskNext/ReZygisk → HMA-OSS
+ 只有其他 Xposed 需求才加 LSPosed
```

## 2. DirtySepolicy / App Zygote SELinux oracle

2026 年公开的新型检测利用 App Zygote 必须具备的 SELinux 查询能力，把它当作全局 policy/context oracle。典型探测：

- `SELinux.checkSELinuxAccess()` / `/sys/fs/selinux/access` 查询 Root 特有 allow 规则；
- `/sys/fs/selinux/context` 判断敏感 context 是否存在；
- `/proc/self/attr/current` 根据 `EPERM`/`EINVAL` 等差异判断 context 是否存在。

例如查询：

```text
untrusted_app 是否可 call ksu binder
u:r:magisk:s0 / ksu_file / lsposed_file 等 context 或规则是否存在
```

这不是普通文件、挂载或包名检测。查询最终由内核 SELinux policy 作答，纯用户空间隐藏不能可靠解决。

### 公开时间线与锚点

- **Duck Detector（FldBudin）于 2026-05-10 首次公开披露**该检测面（DirtySepolicy）；
- KernelSU 数小时内推送内核级缓解 `selinux_hide`（PR #3457：hook selinuxfs `write_op` 表中 context/access 节点的写处理器；PR #3459：`/proc/self/attr/current` 旁路；PR #3495：SELinux status 页扩展）；
- SukiSU-Ultra 随后合并类似修复；
- AP/FP 侧对应内核模块为 `selinux_hook.kpm` 及其同类 KPM（如 geekbyter/dirtysepolicy_kpm、dsp_bypass）。

核对“运行中的内核/LKM 是否包含缓解”时，以上述 PR 是否存在于当前内核源码/分支为准，而不是 Manager APK 版本。

### KSU/SKU

新版 KSU/SKU 集成 SELinux hide：保存注入 Root 规则前的干净 policy 视图，对非授权查询返回干净结果，并补充 `attr/current` 等旁路。必须确认运行中的内核/LKM版本包含对应修复（见上），并在设置中开启。

### AP/FP

通常需要加载或嵌入针对 DirtySepolicy 的 KPM，但不同项目不能混写为同一实现：

- `Admirepowered/selinux_hook`：项目定位为 APatch 的 dirty SELinux rules 隐藏；
- `geekbyter/dirtysepolicy_kpm`：审查快照输出 `dirtyduck_selinux`，覆盖 access/context/status/procattr/clean-policy 等多个面；
- `dsp_bypass` 及其他同类项目：必须分别核对源码、产物名、Hook 面和兼容限制。

某些实现会修改 selinuxfs `write_op` 路径或对干净策略中不存在的 context 模拟 `-EINVAL`，另一些实现可能使用 syscall/LSM/函数 Hook。不要把一个项目的具体 Hook 点套给所有同类 KPM；它们都不等于把系统全局切为 Permissive。

### Magisk

纯 Magisk/用户空间隐藏无法可靠处理该类内核 oracle。若外加 KPM/定制内核修复，真正解决问题的是新增内核层，而不是 Magisk 本体。不要把这扩大成“Magisk 无法隐藏任何传统痕迹”。

## 3. KSU LKM 的日用隐藏栈

在较新手机、最新版 KSU LKM 条件下：

```text
设置：开启 SELinux 隐藏
TEESimulator-RS：Key Attestation/证书链
ZygiskNext：提供 Zygisk API
LSPosed：提供 Xposed/ART Hook
HMA-OSS：当前版直接使用 Zygisk 后端，处理应用列表、设置和安装来源等
```

HMA-OSS 当前不再依赖 LSPosed。非 Magisk Root 通常需要 ZygiskNext/ReZygisk 等 Zygisk provider；只有其他功能确实需要 Xposed API 时才另外安装 LSPosed。

不要无需求添加：

- NoHello KPM；
- KPatch-Next-Module；
- `selinux_hook.kpm`（若新版 KSU 自带并已开启同类 SELinux hide）；
- LSPosed/Zygisk（若没有任何功能需要它们）。

## 4. AP/FP 的日用隐藏栈

相较 KSU，额外需要：

```text
NoHello KPM
selinux_hook.kpm
```

再按需求使用：

```text
TEESimulator-RS
ZygiskNext/ReZygisk → HMA-OSS
只有其他 Xposed 需求才加 LSPosed
```

AP/FP 本身具备相应内核信息伪装能力，一般不为此引入 SUSFS。

## 5. SUSFS

SUSFS 是 KSU 生态的内核级隐藏方案，必须同时理解两部分：

```text
SUSFS kernel patches
+ ksu_susfs 用户空间工具/模块或管理器集成
```

常见能力：

- SUS_PATH：隐藏路径；
- SUS_MOUNT：隐藏挂载；
- SUS_KSTAT：伪装 kstat；
- SPOOF_UNAME：伪装内核版本/构建；
- SPOOF_CMDLINE：伪装 cmdline/bootconfig；
- OPEN_REDIRECT：路径访问重定向；
- 版本相关的 SUS_MAP、AVC spoof、Unicode/path 修复等。

### KSU built-in

内核必须打入 SUSFS 补丁；通常还需安装 SUSFS KSU 用户空间模块作为交互/配置界面。

### SKU built-in

同样必须打入 SUSFS 内核补丁。SKU“自带 SUSFS 支持”主要指集成和管理能力，不代表未打补丁的内核自动获得 SUSFS。部分功能可由 SKU Manager 管理，无需额外传统交互模块；完整能力以当前版本为准。

### LKM

KSU/SKU LKM 只加载 Root `.ko`，不会把 SUSFS VFS 补丁凭空加入 stock kernel。要在 LKM Root 下使用 SUSFS，运行的内核仍须预先集成 SUSFS补丁。

### 老内核/Unicode 问题

部分老内核/构建存在零宽字符、Unicode 或路径处理相关绕过。修复属于内核补丁/构建能力，不是只更新 Manager APK。新设备不要无需求堆叠旧内核补丁；老设备要核对对应分支和修复状态。

## 6. TrickyStore 与 TEESimulator-RS

两者处理 Android Key Attestation/证书链，使用或兼容类似配置：

```text
/data/adb/tricky_store/keybox.xml
/data/adb/tricky_store/target.txt
/data/adb/tricky_store/security_patch.txt
```

TEESimulator-RS 定位为 TrickyStore 的替代实现，通常二选一，不要同时启用两个 Attestation engine。有效结果还取决于 keybox、撤销状态、设备 TEE、GMS/Android 版本及目标 App 检测。

它们不解决：

- Root 路径或挂载隐藏；
- SELinux policy oracle；
- 敏感包名；
- Zygisk/LSPosed 注入痕迹。

## 7. 不做“模块越多越好”

每个模块必须回答：

```text
它修复哪一种真实检测？
该 Root 实现是否暴露这一检测面？
功能是否已由管理器/内核内置？
它增加了哪些攻击面、检测面、崩溃和 OTA 风险？
```

没有明确需求时，不引入 KPatch-Next、KPM、Zygisk、LSPosed、SUSFS 或重复的隐藏模块。

## 8. 最新性核对清单

回答当前方案前核对：

```text
□ Manager APK 版本
□ 实际内核 Root 驱动/KSU LKM 版本
□ built-in/LKM 模式
□ 内核 KMI、配置与补丁
□ KSU/SKU SELinux hide 是否编入并开启（对应 PR #3457/#3459/#3495 是否存在）
□ SUSFS 内核补丁和用户空间工具版本是否匹配
□ SKU 的 KPM 支持：核对 `kernel/kpm/`、`userspace/ksud/src/kpm.rs`、启动事件和 Manager Embed 路径；审查快照已具备 `/data/adb/kpm/*.kpm` 开机加载
□ AP/FP KernelPatch 与 SuperKey行为
□ KPatch-Next 当前源码是否仍删除 SuperKey 验证、替代边界是什么
□ NoHello KPM 的作者官方 Telegram 发布版本与哈希
□ TEESimulator-RS/TrickyStore 冲突与当前兼容性
□ Duck Detector/DirtySepolicy 检测项的当前覆盖面（检测 App 版本与缓解是否同步）
```
