# 核心概念与术语

## 1. Root 是什么

Android Root 是一套受控提权机制，使指定用户空间进程获得 UID 0、Linux capabilities 及配套 SELinux 权限。UID 0 不会自动绕过 SELinux；Root 框架通常还需处理策略、上下文、守护进程和授权。

“Root 管理器”是社区统称，常同时指：

- Manager APK；
- 底层 Root 实现；
- 用户空间守护进程；
- 授权数据库；
- 模块系统。

严格分析时应拆开。

## 2. Magisk

Magisk 修补启动镜像承载的 **ramdisk**，植入 `magiskinit`、启动配置及相关文件，再重新打包：

- 旧布局通常落在 `boot.img`；
- Android 13 启动的新设备常落在 `init_boot.img`；
- 特殊设备可能使用其他启动/Recovery 布局。

所以：

```text
boot/init_boot = 被刷写的镜像容器/分区
ramdisk = Magisk 的实际主要修补对象
```

Magisk Root 主要由用户空间 `magiskd` 管理，自带 Zygisk。它不是内核级 Root 管理器；给 Magisk额外添加 KPatch-Next 并不改变 Magisk 本体的架构归类。

## 3. KernelSU / SukiSU-Ultra

### built-in

将 KSU/SKU 代码与补丁集成到内核源码并编译进 kernel Image。社区经常把它叫“GKI 模式”，因为 GKI 内核易于统一编译和分发，但严格说：

```text
built-in = 集成/加载方式
GKI = Android 内核架构和兼容体系
```

非 GKI 内核同样可以 built-in。

### LKM

将 KSU/SKU Root 驱动编译为 `.ko`，修补启动 ramdisk，使早期启动流程加载该模块。较新设备通常修补 `init_boot.img` 中的 ramdisk。其优点是：

- 不替换厂商内核主体；
- 最轻量；
- 保留厂商优化；
- 更新和 OTA 更方便。

其可用性取决于启动布局、GKI/KMI、内核模块配置、签名与符号条件。Manager 显示“不支持”通常只代表无法自动匹配/修补，不等于不能通过适配内核、手动构建或 built-in 使用。

### SKU 与 KernelPatch

SKU 集成了以 KPM 为重点的 KernelPatch 派生实现。运行内核需要正确开启 KPM 支持：

```text
CONFIG_KPM=y
```

非 GKI 还可能要求匹配的 KALLSYMS 条件。普通 SKU LKM 不能凭空把 KPM 所需内核实现加入未集成该能力的 stock kernel。审查快照 `SukiSU-Ultra@3546754` 中，Manager 的 Embed 模式会把 KPM 保存到 `/data/adb/kpm/`，`ksud` 在启动阶段调用 `booted_load()` 枚举并加载该目录中的 `.kpm`，安全模式下跳过。回答当前状态时必须重新核对 `kernel/kpm/`、`userspace/ksud/src/kpm.rs`、`userspace/ksud/src/init_event.rs` 及 Manager Embed 路径。

## 4. APatch / FolkPatch / KernelPatch

KernelPatch 是内核二进制修补、Hook 和 KPM 运行框架，可提供：

- 内核 Image 静态修补；
- 内核函数 inline hook；
- syscall table hook；
- SuperCall；
- KPM 加载。

APatch = KernelPatch + Android Root/授权管理 + APM/KPM 管理。

FolkPatch 是 APatch 下游，扩展 UI、模块管理、自动加载等功能，底层仍基于 KernelPatch。

### SuperKey

SuperKey 是 KernelPatch/APatch 的高权限认证信任根。KPM 进入 EL1；仅判断调用者“是不是 Root”不足以防止已获 Root 的恶意程序加载恶意 KPM。对开发者、KPM 测试机或对抗 Root 恶意程序的产品，SuperKey 是管理器选型的重要安全边界。

KPatch-Next-Module 为 Magisk/KSU 打包独立 KPM 支持。审查快照 `KPatch-Next-Module@b5612ad` 所使用的 `KPatch-Next@0fe6d14` 在 SuperCall 入口以 `current_uid()==0` 作为门槛，未采用当前上游 KernelPatch 的 SuperKey 参数认证模型。该结论绑定上述 commit；不能在未审计新版本源码时假定行为不变或存在等价替代认证。

## 5. 模块分类

| 名称 | 依赖 | 运行位置 | 说明 |
|---|---|---|---|
| Magisk 模块 | Magisk | 通常用户空间 | ZIP、脚本、文件挂载、二进制，可包含 Zygisk 模块 |
| KSU 模块 | ksud/KernelSU | 通常用户空间 | 格式近似 Magisk；系统文件修改可能依赖 Meta Module |
| APM | APatch/FolkPatch | 用户空间 | APModule，类似 Magisk/KSU 模块 |
| KPM | KernelPatch/KPM Loader | 内核空间 | `*.kpm`，可做内核 Hook/注入 |
| `.ko` | Linux LKM | 内核空间 | 标准 Linux Kernel Object，依赖 ABI/符号/签名等 |
| Zygisk 模块 | Zygisk API | 用户空间进程 | 注入 Zygote/App，不是内核模块 |
| Xposed 模块 | LSPosed/Xposed | 用户空间进程 | ART/Java Hook，不是内核模块 |

KPM 与 `.ko` 功能可相似，但格式、加载器和兼容模型不同，不能互称。

## 6. Zygisk、ZygiskNext、Xposed、LSPosed

- Zygisk：Magisk 的 Zygote 注入环境/API。
- ZygiskNext：独立 Zygisk 实现，可为 KSU/SKU/AP/FP 提供 Zygisk API；Magisk 使用时通常需关闭内置 Zygisk。
- Xposed：Android 运行时/ART 方法 Hook API 与生态。
- LSPosed：现代 Xposed API 兼容框架，通常作为 Zygisk 模块运行。
- HMA-OSS：当前版为直接 Zygisk 模块，已用 Zygisk 后端替代 LSPosed 依赖；用于应用列表、设置和安装来源等隔离，不解决内核路径或 Key Attestation。只有另有 Xposed 需求时才需要 LSPosed。

## 7. NoHello

### 主流 NoHello KPM

- 当前使用更广；
- 仅在作者 Telegram 频道发布，未在 GitHub 正式发布（作者有同名 GitHub 组织，但正式 Release 走 TG 渠道）；
- 运行于内核空间；
- 不依赖 ZygiskNext；
- 主要为 APatch/FolkPatch 的特有路径与环境隐藏设计。

可审计性示例：官方 TG 发布带完整文件名与 SHA-256（如 `Nohello-v1.0.0-13-6106b0a-release.kpm`，附哈希），并注明内核支持范围（4.19/5.4、4.18 及以下）与改动摘要。核对时应以作者官方频道发布信息为准，不要用第三方转载或 ROM 站版本代替。

### GitHub NoHello Zygisk

- 用户空间 Zygisk 模块；
- 功能目标相近；
- 依赖 Zygisk 环境；
- 不是主流 KPM 版本的公开源码。

默认不要给 KSU/SKU 推荐 NoHello：KSU/SKU不会暴露 AP/FP 的相同路径检测面，无需求时也不应为此引入 KPatch-Next。

## 8. 常用核对锚点

涉及版本、功能是否内置、安全机制时，优先核对以下一手来源（不要只信第三方教程/营销页）：

| 主题 | 锚点 |
|---|---|
| KernelSU（含 selinux_hide） | github.com/tiann/KernelSU；PR #3457（write_op 表）/ #3459（attr/current 旁路）/ #3495（status 页） |
| SukiSU-Ultra | github.com/SukiSU-Ultra/SukiSU-Ultra；KPM 实现见 `kernel/kpm/`，是否自动加载查 manager 源码 |
| KernelPatch / APatch | github.com/bmax121/KernelPatch、github.com/bmax121/APatch |
| DirtySepolicy KPM | github.com/geekbyter/dirtysepolicy_kpm、github.com/Ccccccccvvm/dsp_bypass |
| Duck Detector | FldBudin 的 Duck Detector（2026-05-10 首次公开 DirtySepolicy 检测） |
| NoHello KPM | 作者官方 Telegram 频道（GitHub 同名组织无正式 Release） |
| TrickyStore / TEESimulator-RS | 各自官方仓库与 Release |

社区教程、ROM 站、转载频道只能作为线索；与一手来源冲突时以一手来源为准。
