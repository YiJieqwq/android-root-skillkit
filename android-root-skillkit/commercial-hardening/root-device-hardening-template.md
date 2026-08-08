# Android Root 玩家付费软件加固方案 · 参考模板

> **范围限定：本模板仅适用于从产品定义开始就专门面向 Root/玩机用户的商业付费软件。**它不适用于普通消费者 App、银行/支付 App，也不适用于仅希望兼容少量 Root 用户的一般应用。
>
> 目标用户被假定为理解刷机、换内核、安装模块和系统升级的后果，并接受严格设备绑定、指纹漂移后拒绝签发、官网手动解绑、解绑冷却期和必要的人工复核。由用户主动玩机行为触发的假阳性属于已接受的安全取舍，不自动视为可用性缺陷。
>
> 技术定位：用户主动 Root、允许安装模块，且 TEE/Keystore/系统完整性不可默认可信。
>
> 核心目标不是让持有设备控制权的专业攻击者永远无法提取明文，而是：
>
> 1. 无授权时拿不到高价值数据或有效运行状态；
> 2. 设备 A 上取得的授权、数据包和运行材料，不能直接复制到设备 B/C/D 使用；
> 3. 制作稳定、通用、低门槛破解版的成本，高于版本主要商业生命周期。

---

## 0. 适用边界

### 0.1 默认攻击者能力

攻击者可以：

- 获取、反编译、修改并重签名 APK；
- 拥有 Root 权限，读取应用私有文件；
- Hook Java/JNI/native，Dump 用户态内存和 memfd；
- 购买合法卡密，在设备 A 上完成一次正常授权；
- 安装 Magisk/KSU/KPatch 模块，包括 TrickyStore 等环境伪装模块；
- 使用商业脱壳、Frida、ptrace、宿主执行等常见逆向方法。

### 0.2 不依赖的信任基础

本方案不把以下能力作为强制前提：

- TEE、StrongBox 或硬件 Keystore 可信；
- Play Integrity 一定通过且结果不可伪造；
- bootloader 锁定；
- 系统属性和 Java API 返回值可信；
- 360 等商业加固能够单独构成授权根。

TEE/Keystore/完整性证明可以作为**附加保护或风控信号**，但产品必须保留适用于目标 Root 用户的软件授权路径；这里的“降级”只指不依赖硬件证明，不代表放宽设备绑定。软件路径仍依靠服务器授权、严格设备绑定和运行时材料维持主要商业目标。

### 0.3 必须诚实的安全边界

- 在纯用户态架构中，合法用户设备上使用过的密钥和明文最终可能被针对性抓取；
- 设备指纹通常不是秘密，不能单独充当内容加密根密钥；
- 用户态读取的指纹字段可能被 Hook 或伪造；
- 如果产品拥有 EL1 Watchdog/KPM，可把设备复核和运行授权下沉到内核态，显著提高跨设备复用成本，但仍不抵抗恶意 KPM、被修改的内核或加载器。

因此，本模板保护的是：

> **反低成本传播、反“一次破解全设备通用”，而不是绝对不可提取。**

---

# 1. 两类推荐架构

## 1.1 方案 A：Root 玩家付费用户空间软件 + 设备个性化数据包

适合高价值内容是模块、配置、素材、规则库或独立数据文件的应用。

```text
APK
├── 壳/商业加固层
├── NativeGuard
├── 通用密文资产或资产索引
└── Java/Kotlin UI 与业务调度

授权服务器
├── 卡密/账号/设备绑定
├── 当前版本策略
├── 服务端签名 Grant
├── 每设备/每版本/每资产密钥派生
└── 吊销、换绑、限流和审计
```

目标：

```text
设备 A 获得的：
- device_credential
- 签名 Grant
- 资产密钥
- 个性化数据包

复制到设备 B 后不能直接使用；
攻击者必须额外修改指纹采集、Grant 绑定、资产解密和业务消费链。
```

## 1.2 方案 B：App + Watchdog KPM + Main KPM

适合付费内核模块或核心功能本身运行在 EL1 的产品。

> **适用前提（市场现实）**：专门做付费 KPM/内核模块的商业产品本身很少；内核级校验是**拓展方案，不是默认方案**。卖的不是 KPM 却要求用户加载 KPM 属于强人所难——多数 Root 用户跑 Magisk/KSU 用户空间栈，没有 KPM 加载链。默认采用方案 B 仅当：① 产品核心功能本身就是内核模块或必须 EL1 能力；② 目标用户确定具备 KPM 加载能力且自愿启用；③ 团队能维护多内核版本的 KPM 稳定性。普通 App 可将内核级校验作为可选增强（检测到用户已有 KPM 能力时提示启用），默认路径必须零内核依赖。

```text
Android App/VMP
  ├─ UI、网络、设备凭据
  ├─ 获取当前启动 Grant
  ├─ 短暂解密 Main KPM
  └─ 调用原版 KPatch-Next 加载
     （KPatch-Next 仅作加载器；其删除了上游 KernelPatch 的 SuperKey 验证，
       不能视为信任根，安全根在 Grant/绑定/状态机，详见本 skill 的 basics/concepts.md）

watchdog.kpm
  ├─ EL1 读取硬件指纹
  ├─ boot_nonce / boot_session_id
  ├─ 验证服务端签名 Grant
  ├─ 保存 Runtime Seed
  └─ 与 Main KPM 握手、心跳

main.kpm
  ├─ 默认 DORMANT
  ├─ 独立验签和复核设备/启动会话
  ├─ Runtime Seed 参与必要运行状态初始化
  └─ 通过后进入 ACTIVE 并启用核心 Hook
```

这一方案的核心不是“Watchdog 永远不会被攻破”，而是：

> Dump 出 Main KPM，不等于获得任意设备可直接运行的通用模块。

---

# 2. 设备指纹设计

## 2.1 可选字段

优先收集稳定且能在目标机型上可靠读取的字段：

- SoC unique ID 或 SoC fuse 派生标识；
- bootloader serial；
- 存储设备 CID/序列标识；
- board ID、硬件序列号；
- IMEI/MEID（仅在合法、可访问、用户知情且业务确有必要时使用）；
- Android ID、应用安装实例 ID（仅作为辅助字段）；
- verified boot key digest、内核构建标识、KPatch 版本（作为启动环境指纹，不等同于硬件身份）。

注意：不同 SoC、ROM、Android 版本和权限环境下，可读取字段差异很大。IMEI 可能因权限、多 SIM、无基带设备或隐私限制而缺失；SoC ID 也不是所有平台都公开提供。

## 2.2 规范化格式

禁止简单字符串拼接。使用固定版本、字段编号、状态和长度：

```text
FP_V1 = SHA-256(
    "ROOT_APP_HW_FP_V1"
    || field_id || status || length || normalized_value
    || ...
)
```

其中 `status` 至少区分：

```text
PRESENT / UNAVAILABLE / PERMISSION_DENIED / READ_ERROR
```

同时生成字段可用性位图：

```text
field_bitmap
```

服务器保存：

- 最终指纹 Hash；
- 字段可用性位图；
- 必要的逐字段不可逆 Hash；
- 指纹算法版本。

原则上不保存 IMEI、序列号等原始值。

## 2.3 严格绑定策略

面向 Root 玩家时可以采用严格匹配：

```text
current_hardware_fingerprint == bound_hardware_fingerprint
```

不匹配时采用 fail-closed，不自动宽松匹配：

```text
拒绝签发新 Grant
→ 引导用户登录官网手动解绑
→ 解绑冷却期/频率限制/必要时人工审核
→ 旧设备凭据吊销
→ 新指纹重新绑定
```

对于本模板的 Root 玩家付费软件，刷机、换内核或字段可见性变化造成的误报属于有意接受的安全成本。

必须提前定义：

- 换机；
- 主板维修；
- 多 SIM 变化；
- 刷机、换内核；
- 卸载重装；
- 某个硬件字段在系统更新后突然不可读。

## 2.4 指纹与密钥的关系

禁止纯客户端方案：

```text
K_asset = KDF(SoC_ID || IMEI || serial)
```

因为这些字段通常不是秘密，攻击者知道算法后可以离线复算。

推荐：

```text
K_asset_device = HKDF(
    server_master,
    salt = license_id || device_instance_id || release_id,
    info = fingerprint_hash || asset_id || asset_version
)
```

这里的秘密来自服务端；设备指纹负责绑定派生上下文。客户端只能在授权后短暂获得当前设备、当前版本需要的材料。

---

# 3. 授权与数据包设计

## 3.1 首次绑定

首次请求至少包含：

```text
protocol_version
app_version
card_key
hardware_fingerprint
field_bitmap
boot_environment_fingerprint
request_nonce
encrypted_asset_manifest_hash
request_proof
```

服务端成功后生成：

```text
device_instance_id
device_credential
```

后续使用设备凭据，不长期保存卡密原文。`device_credential` 不应只是脱离设备上下文即可复用的长期 bearer token；服务端签发和消费时还要核对 license/account、device_instance_id、严格硬件指纹、字段位图与算法版本、App/release/asset 版本、nonce、有效期和当前解绑/吊销状态。

## 3.2 启动 Grant

服务端返回规范化并签名的 Grant：

```text
grant_version
grant_id
license_id
device_instance_id
hardware_fingerprint_hash
boot_environment_fingerprint_hash
app/release/asset versions
asset_manifest_hash
request_nonce
boot_nonce / boot_session_id（如有 Watchdog）
issued_at
expires_at
runtime_seed（按架构需要）
wrapped_asset_keys 或短期解密材料
```

签名建议使用 Ed25519 或其他成熟、固定编码的签名方案。客户端必须验证：

- 签名；
- 请求 nonce；
- 设备实例；
- 指纹 Hash；
- 版本和资产清单 Hash；
- 有效期；
- 当前启动会话（如有）。

## 3.3 数据包个性化

根据业务成本选择：

### 模式 1：通用密文 + 每设备短期密钥

优点：CDN 和发布简单。
缺点：设备 A 抓到明文密钥后，仍可能通过深度二改在其他设备复用。

### 模式 2：每设备重新封装数据密钥

资产密文保持通用，但资产内容密钥通过设备/授权上下文单独封装。适合大多数应用。

### 模式 3：每设备个性化密文包

服务器或构建服务为设备生成不同密文、清单和可选水印。传播价值最低，但存储、缓存、下载和换绑成本最高。

对“数据包只能在这台设备上解密功能”的目标，推荐至少使用模式 2；皇冠资产可使用模式 3。

## 3.4 业务必须消费正确数据

禁止：

```text
if (licenseVerified) enableAllButtons();
```

推荐：

- 关键功能必须读取授权后才能解开的资产；
- Runtime Seed 参与必要常量、表项、控制消息认证或参数初始化；
- UI 显示成功不代表真实功能进入 ACTIVE；
- Java 侧布尔值只能控制展示，不承担最终授权。

## 3.5 加密与拟合

Root 场景下的核心目标不是让代码绝对不可逆向，而是同时做到：

```text
加密：未授权时缺少必要数据，绕过 UI/Java 判断也无法使用功能
拟合：正常授权流程产生跨 UI、Native、资产和运行会话的真实状态
```

建议让流程逐层产生后续功能所需的输入：

```text
Grant 验签
  → 设备/版本绑定
  → 会话初始化
  → UI/点击 capability
  → Native runtime context
  → 资产子密钥
  → 真实功能执行
```

因此不要把所有检查都汇聚到 `licenseVerified`。按钮状态、点击调度、Root 检查、异步回调和工作进程可以互相拟合，用于增加逐层定位成本；但最终安全边界必须是服务端 Grant、设备绑定密钥、资产清单和实际功能数据。

攻击者即使完成脱壳，也应面对：

- 补 Java 状态后仍缺少资产密钥；
- 强制按钮可用后仍缺少点击/调度 capability；
- 强制 Root 成功后仍缺少 Native/资产运行状态；
- 设备 A 的 Grant、缓存和数据包不能直接在设备 B 使用。

拟合不应通过大量崩溃、恶意重启或数据破坏实现。正版异常应能安全恢复；Debug 构建保留状态诊断，Release 构建移除敏感诊断。

# 4. 商业加固（壳/VMP/反调试）

## 4.1 商业加固的职责

360 等商业加固主要用于：

- 延迟 DEX/native 定位和脱壳；
- 提高 Hook、调试和重打包成本；
- 增加当前版本补丁迁移成本；
- 保护 Grant 解析、指纹组装和短暂解密窗口。

它不负责：

- 生成服务端签名；
- 长期保管服务端根密钥；
- 单独证明设备可信；
- 保证运行时明文永不被 Dump。

## 4.2 Native 关键链

优先放入 native/VMP 的区域：

1. 指纹字段采集和规范化；
2. Grant 解析、验签和上下文核对；
3. 资产密钥恢复；
4. 数据包清单验证；
5. 懒解密和业务消费入口；
6. Watchdog/Main 的加载与激活顺序；
7. 当前版本 Request Proof。

## 4.3 密码实现

- 禁止自实现 AES-GCM、HKDF、Ed25519 等密码原语；
- 使用成熟、经过测试的实现；
- AEAD nonce 在同一密钥下必须唯一；
- AAD 绑定协议版本、设备实例、资产 ID、资产版本和清单 Hash；
- 解密失败不允许回退到固定密钥、旧算法或明文资产。

## 4.4 明文生命周期

- 明文不进入 Java/Kotlin `String` 或长期 `byte[]`；
- 使用 native 缓冲区，按最小资产粒度解密；
- 使用后调用不会被优化掉的安全清零函数；
- 不写普通临时文件、日志、Crash 上报或提取诊断；
- memfd 只能缩短和收敛暴露窗口，不能保证 Root 环境下不可 Dump。

## 4.5 反调试

优先交给现有商业加固，并只作为延迟和风险信号。自研部分重点放在：

- 关键链完整性；
- Grant/密钥/资产的绑定；
- 失败关闭；
- 服务端风控和版本轮换。

不要把单一 TracerPid、端口、线程名或 maps 字符串检测作为授权根。

---

# 5. 付费内核模块样板

## 5.1 Watchdog 最小职责

Watchdog 应保持小而可审计：

- 在 EL1 读取硬件指纹；
- 生成每次加载或每次启动唯一的 `boot_nonce`、`boot_session_id`；
- 验证服务端签名 Grant；
- 核对设备、版本、密文 Hash 和当前启动会话；
- 保存 Runtime Seed；
- 与 Main KPM 完成握手和随机周期心跳；
- 授权失效时通知 Main 安全停止功能。

第一版不建议做：

- 全局隐藏所有模块；
- 大范围 Hook `/proc`、`kallsyms`；
- 对其他调试模块进行攻击性阻断；
- 授权失败后触发 kernel panic、重启或破坏数据。

## 5.2 Main KPM 状态机

```text
UNINITIALIZED
    ↓
DORMANT
    ↓ Grant + Watchdog handshake + Runtime Seed 成功
ACTIVE
    ↓ 心跳失败/Watchdog 消失/会话变化
DORMANT 或 ERROR
    ↓ 安全撤销 Hook
EXITED
```

Main 必须：

- 默认 DORMANT；
- 独立验证签名 Grant；
- 独立读取并复核设备指纹；
- 让 Runtime Seed 参与少量但必要的真实运行状态；
- ACTIVE 前不启用核心 Hook；
- 降级时安全撤销 Hook。

## 5.3 剩余风险

Watchdog 架构仍不抵抗：

- 恶意 KPM 读取目标模块内存；
- 被修改的 KPatch-Next；
- 被修改的 boot image、内核或加载器；
- 针对目标版本的 EL1 动态分析；
- 服务端签名私钥泄露。

它的商业价值在于把攻击从“补 Java 布尔值”升级为“需要理解并二改当前版本 EL1 状态机”。

---

# 6. 推荐实施顺序

### Phase 0：清理

- 删除固定密钥和 fallback；
- 删除明文导出 JNI/调试接口；
- 删除密钥、明文头、memfd 路径和完整 Grant 日志；
- 建立 Debug/Release 严格隔离。

### Phase 1：服务器协议

- 设备实例和换绑；
- 严格指纹匹配；
- 签名 Grant；
- nonce、防重放、版本状态、吊销和限流；
- Release/资产密钥轮换。

### Phase 2：资产门控

- 资产独立 AEAD 加密；
- 清单签名/Hash；
- 每设备密钥封装；
- native 懒解密和安全清零；
- Java 全量补丁后仍拿不到有效资产。

### Phase 3：App 加固

- 商业壳/VMP 接入关键咽喉；
- 壳与资产消费链耦合；
- 完整性检查；
- 多版本构建变异和自动化。

### Phase 4：可选 Watchdog/Main KPM

- Watchdog 最小状态机；
- Main 默认 DORMANT；
- 签名 Grant 和启动会话；
- Runtime Seed；
- EL1 内部握手与心跳；
- 多内核版本稳定性测试。

---

# 7. 验收清单

## 7.1 App/资产

```text
□ 无卡密或无设备凭据时，无法取得有效资产密钥
□ 强制 Java UI 显示授权成功，关键功能仍不可用
□ 修改或重放 Grant，验签或上下文核对失败
□ 把设备 A 的凭据、Grant、密钥缓存和数据包复制到设备 B，不能直接使用
□ 替换 APK 签名、资产清单或资产版本后，授权链失败
□ 删除壳/native 后，资产消费链断开
□ 不存在固定密钥、明文 fallback 和生产导出接口
□ 明文按最小粒度出现，不写入普通文件、日志和 Java 长期对象
□ 服务端密钥可按版本轮换，设备和版本可吊销
```

## 7.2 Watchdog/Main KPM

```text
□ 只加载 Dump 出的 Main KPM，保持 DORMANT
□ 设备 A 的 Grant 不能激活设备 B
□ 旧启动会话的 Grant 在 Watchdog 重载或重启后失效
□ 修改 App 布尔授权状态，Main 仍不能 ACTIVE
□ Watchdog 缺失、版本错误或心跳失败时，Main 安全撤销功能
□ 网络、验签或授权失败不会导致 kernel panic、重启或数据损坏
□ 恶意/异常输入经过 fuzz 和边界测试
□ 每个支持的内核版本完成加载、卸载、Hook 撤销和长时间稳定性测试
```

---

# 8. 一句话总结

> **Root 玩家场景下，不要求环境“干净”，而要让授权、设备指纹、当前版本、当前启动会话和高价值数据形成同一条消费链：设备 A 被抓到的材料不能直接变成设备 B/C/D 可安装即用的通用破解版。**
