# Android 格机威胁分类

## 1. 后果等级

### 数据格/软格

主要破坏用户数据、应用和加密元数据：

- 应用私有数据；
- 内部存储；
- userdata；
- metadata/FBE 相关状态。

通常可通过清除数据、重建文件系统或完整刷机恢复设备使用，但数据不可恢复。

### 系统砖/启动砖

主要破坏系统和启动镜像：

- boot/init_boot/vendor_boot；
- dtbo/vbmeta；
- super 或逻辑分区元数据；
- recovery。

设备可能卡 Logo、Fastboot 或 Recovery。只要早期 Bootloader 和底层刷写入口仍在，通常仍有恢复机会。

### 硬砖/永久异常

破坏早期启动链、分区表、关键固件、设备身份或校准：

- GPT；
- EFISP、XBL、ABL；
- TZ/HYP/AOP/RPM 类固件；
- Keymaster/KeyMint 等固件；
- selected persist、NV、校准和身份材料；
- RPMB、熔丝、存储固件等更高/外部信任域。

可能无法进入普通刷机模式，或设备虽能启动但硬件、身份、DRM、基带永久异常。

## 2. T1：直接用户空间破坏

常见类别：

- 文件删除、rename、truncate、fallocate；
- 文件系统格式化或元数据破坏；
- 原始块设备覆盖；
- 把错误镜像写入分区；
- discard、secure-discard、zero-out；
- Recovery/factory reset；
- reboot/poweroff 触发破坏结果生效。

特点：通常使用普通系统调用，容易归因到进程树，但不能只按工具名识别。

### 典型载荷形态：自解压 sh + ELF

现实中“格机”常以分阶段载荷出现，而不是单个命令：

- 外层是自解压 sh：脚本头部（含元数据、解压/解密逻辑）+ 内嵌 ELF（base64 块或脚本尾部二进制）；
- 运行时把 ELF 解压到 `/data/local/tmp`、`/cache` 或 `$TMPDIR`，`chmod +x` 后以 root 执行；
- 可能多阶段：sh → 第一阶段 ELF（探测/提权/下载）→ 第二阶段破坏载荷；
- 破坏前常做反分析：检测 Frida/ptrace/LD_PRELOAD、杀安全进程、延迟重启等。

对防御的启示：

- 进程名/命令黑名单（sh、dd 等）完全无效——破坏者是解出的 ELF；
- 归因要追踪 sh → ELF 的 exec 血统，而非初始 PID；
- 解压、chmod、exec 本身可作为分析会话的事件点；
- 最终防线仍是“ELF 对真实资产的最终 I/O 落点”，与载荷形态无关。

## 3. T2：替代、异步与间接 I/O

- 直接 syscall 绕过 libc Hook；
- 相对路径、软链接、目录 FD、mapper/by-name 别名；
- 已打开 FD 或 SCM_RIGHTS 传递；
- mmap + MAP_SHARED + 脏页写回；
- direct I/O、writev；
- io_uring worker；
- splice/copy_file_range；
- Device Mapper；
- kworker 延迟 writeback；
- Binder/系统服务 confused deputy；
- 厂商私有存储接口。

关键问题：最终执行 I/O 的线程不一定是最初目标，PID/进程名策略会丢失因果关系。

## 4. T3：受控内核扩展入口

- init_module/finit_module；
- KPM 加载；
- eBPF；
- Root 管理器扩展；
- 厂商 debug 驱动。

攻击者试图从 Root 用户空间进入 EL1，再绕过用户空间/VFS防护或拆除防格 Hook。

## 5. T4：任意 EL1 执行

- 已加载恶意内核模块/KPM；
- 内核漏洞；
- 任意内核内存写；
- 直接提交 BIO/blk-mq；
- 直接 UFS/SCSI 命令；
- 篡改防格策略、日志和缓存。

同 EL1 防守不能提供绝对保证。只能做入口冻结、完整性检测、最终资产兜底、信任降级和条件恢复。

## 6. T5：更高或外部信任域

- EL2/Hypervisor；
- TEE/Secure World；
- RPMB；
- Baseband；
- 熔丝；
- 存储控制器/固件；
- 物理攻击。

普通 KPM、Root 模块或 Android 内核防格通常无法覆盖。

## 7. 信息窃取与反分析

真实格机程序可能在破坏前：

- 收集设备型号、序列号、分区和 Root 环境；
- 截图、拍照或读取用户文件；
- 上传日志、令牌和样本执行结果；
- 检测 Frida、ptrace、LD_PRELOAD、VPN、模拟器或旧设备；
- 杀死终端、监控、更新和恢复进程；
- 延迟重启或制造干扰。

因此针对性分析工具不能只保护写入，还应逐步加入敏感源读取、网络/Binder/共享文件外泄和证据保护。

## 8. 不可靠的单点防御

以下只能作为一层：

- 命令黑名单；
- 进程名/包名黑名单；
- 路径字符串匹配；
- libc Hook；
- 只 Hook write；
- 只保护 by-name 节点；
- 只杀恶意进程；
- 只备份关键分区；
- 只依赖 SELinux；
- 只阻止 Root、不阻止内核扩展。
