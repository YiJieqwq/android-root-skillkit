# Changelog

## 2026-08-08

### Added

- 首次公开版 `android-root-skillkit`；
- 标准执行流程与来源优先级；
- `SOURCES.md` 上游审查 commit 和证据等级；
- Root 玩家付费软件的明确适用范围；
- 严格设备绑定、官网手动解绑、冷却期和旧凭据吊销要求；
- 防格 PolicyMode、Decision、ExecutionResult 三维枚举；
- `dev_t` 仅作为当前运行时身份的边界说明；
- Shadow FD/Readback 等能力的实验性标注。

### Corrected

- 项目和 Skill 名从 `android-root-toolkit` 改为 `android-root-skillkit`；
- SukiSU-Ultra 当前已具备 `/data/adb/kpm/*.kpm` 开机加载链，不再错误声称“没有 KPM 自动加载”；
- HMA-OSS 当前为直接 Zygisk 模块，不再要求 LSPosed；
- KernelSU `Unsupported` 表示当前内核/官方安装路径不受支持，而不只是“自动修补失败”；
- KPatch-Next 的 UID 0 门槛归因到具体 KPatch-Next commit，而不是笼统归因于打包模块；
- 分开描述 `selinux_hook`、`dirtysepolicy_kpm` 与其他 DirtySepolicy KPM；
- DirtySepolicy 时间线区分较早私下发现声明与公开实现锚点；
- 商业加固方案 A 改名为“Root 玩家付费用户空间软件”。

### Security

- 保留“不输出真实设备破坏代码”的边界；
- 防格测试限定为 disposable loop/虚拟块设备；
- 不承诺抵抗任意 EL1、EL2、TEE/RPMB、存储固件或物理攻击。
