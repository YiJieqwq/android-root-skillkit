# Sources and audit pins

本文件记录 2026-08-08 正式审查使用的上游快照。它用于说明结论依据，不代表未来版本仍保持相同行为。

## 证据等级

| 标签 | 含义 |
|---|---|
| `SOURCE` | 目标版本源码直接确认 |
| `OFFICIAL` | 官方文档、PR 或 Release |
| `AUTHOR-CHANNEL` | 作者/发布频道声明或二进制发布 |
| `BEHAVIOR-TEST` | 可复现行为测试，但未必有源码 |
| `COMMUNITY` | 社区经验，只作线索 |
| `UNVERIFIED` | 尚未独立确认 |

## 审查快照

| 项目 | Commit | 日期 | 用途 |
|---|---|---|---|
| [tiann/KernelSU](https://github.com/tiann/KernelSU) | `e6cc0ef` | 2026-08-07 | LKM、SELinux Hide、Manager/内核版本边界 |
| [SukiSU-Ultra/SukiSU-Ultra](https://github.com/SukiSU-Ultra/SukiSU-Ultra) | `3546754` | 2026-07-25 | KPM、`CONFIG_KPM`、`ksud::kpm::booted_load()` |
| [bmax121/KernelPatch](https://github.com/bmax121/KernelPatch) | `169b2b5` | 2026-08-08 | KPM、SuperCall、SuperKey |
| [bmax121/APatch](https://github.com/bmax121/APatch) | `9a63e0f` | 2026-08-06 | APatch、KPM/APM、SuperKey |
| [KernelSU-Next/KPatch-Next](https://github.com/KernelSU-Next/KPatch-Next) | `0fe6d14` | 2026-01-20 | UID 0 SuperCall 门槛 |
| [KernelSU-Next/KPatch-Next-Module](https://github.com/KernelSU-Next/KPatch-Next-Module) | `b5612ad` | 2026-03-06 | KPatch-Next 打包关系 |
| [geekbyter/dirtysepolicy_kpm](https://github.com/geekbyter/dirtysepolicy_kpm) | `490c971` | 2026-06-30 | DirtySepolicy KPM 实现面 |
| [LSPosed/DirtySepolicy](https://github.com/LSPosed/DirtySepolicy) | `0cda3b8` | 2026-05-29 | App Zygote SELinux oracle 与时间线声明 |
| [eltavine/Duck-Detector-Refactoring](https://github.com/eltavine/Duck-Detector-Refactoring) | `f94e7d9` | 2026-08-01 | 检测覆盖与公开实现锚点 |
| [Enginex0/TEESimulator-RS](https://github.com/Enginex0/TEESimulator-RS) | `6d241e5` | 2026-07-11 | Key Attestation、TrickyStore 配置兼容 |
| [frknkrc44/HMA-OSS](https://github.com/frknkrc44/HMA-OSS) | `72fd0f1` | 2026-07-10 | 直接 Zygisk 后端，替代 LSPosed 依赖 |
| [LyraVoid/FolkPatch](https://github.com/LyraVoid/FolkPatch) | `2cbdc7a` | 2026-08-08 | FolkPatch、KPM 自动加载与产品定位 |

## 关键来源

### Magisk

- [安装文档](https://github.com/topjohnwu/Magisk/blob/master/docs/install.md)
- [启动过程](https://github.com/topjohnwu/Magisk/blob/master/docs/details.md)

结论：目标镜像可能是 `boot`、`init_boot` 或 `recovery`；Magisk 主要修改其中的 ramdisk/init 链，不能仅按 Android 版本机械判断目标分区。

### KernelSU 状态语义

- [KernelSU Installation](https://kernelsu.org/guide/installation.html)
- [KernelSU FAQ](https://kernelsu.org/guide/faq.html)

`Unsupported` 表示当前内核/官方直接安装路径不受支持；`Not installed` 才表示官方支持但尚未安装。

### KernelSU SELinux Hide

- [PR #3457](https://github.com/tiann/KernelSU/pull/3457)：基础 SELinux Hide/selinuxfs 查询面
- [PR #3459](https://github.com/tiann/KernelSU/pull/3459)：`attr/current`
- [PR #3495](https://github.com/tiann/KernelSU/pull/3495)：SELinux status

### SukiSU-Ultra KPM 自动加载

`SOURCE`：

- `kernel/kpm/`
- `userspace/ksud/src/kpm.rs`
- `userspace/ksud/src/init_event.rs`
- Manager KPM Embed 路径

审查快照中，Embed 模式保存到 `/data/adb/kpm/`，`ksud` 启动阶段调用 `booted_load()` 加载该目录中的 `.kpm`；安全模式跳过。

### KPatch-Next

`SOURCE`：`KPatch-Next@0fe6d14/kernel/patch/common/supercall.c` 的入口以 `current_uid()==0` 为门槛。该结论不能不经复核套用于未来版本。

### HMA-OSS

当前 README 和 commit `72fd0f1` 明确 HMA-OSS 已用直接 Zygisk 后端替代 LSPosed 依赖。只有其他 Xposed 功能需要时才安装 LSPosed。

### DirtySepolicy 时间线

据 LSPosed 项目说明：LSPosed 团队声称 2024-08 已私下发现但未公开；FldBudin 于 2026-05 在 Duck Detector 中独立公开。这里区分私下发现声明与公开实现锚点，不做绝对首创裁定。

### NoHello

`AUTHOR-CHANNEL`：Telegram Web 预览可核对：

- `Nohello-v1.0.0-13-6106b0a-release.kpm`
- SHA-256：`4072617b516930bd4b0a42b65997e0527e98f9ab004654636ca091c12e18bfb3`

[MhmRdd/NoHello](https://github.com/MhmRdd/NoHello) 当前是 Zygisk 模块，不能当作上述 KPM 的公开源码。文件 Hash 证明发布文件身份，不等于源码可审计。

### DirtySepolicy KPM 项目必须分开

- [Admirepowered/selinux_hook](https://github.com/Admirepowered/selinux_hook)
- [geekbyter/dirtysepolicy_kpm](https://github.com/geekbyter/dirtysepolicy_kpm)
- `dsp_bypass` 等其他实现

这些项目的产物名、Hook 面、兼容性和审计状态不同，不能把一个项目的实现细节套给全部同类 KPM。

### SUSFS

- [simonpunk/susfs4ksu](https://gitlab.com/simonpunk/susfs4ksu)
- [sidex15/susfs4ksu-module](https://github.com/sidex15/susfs4ksu-module)

内核补丁与用户空间控制组件是两个部分；用户空间模块不能给未集成补丁的 stock kernel 凭空增加 SUSFS VFS 能力。
