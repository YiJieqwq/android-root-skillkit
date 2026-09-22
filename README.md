# android-root-skillkit

**English** | [中文](README.zh-CN.md)

Android root / modding security knowledge and review skillkit for AI assistants.

It merges three related domains into a single routed Skill:

1. **Root fundamentals, selection and hiding**: Magisk, KernelSU, SukiSU-Ultra, APatch, FolkPatch, KernelPatch/KPM, LKM/built-in/GKI, SUSFS, Zygisk, DirtySepolicy, Attestation, and more;
2. **Bricker threats and defense**: asset-centric protection, final I/O landing point, session and causal attribution, maintenance windows, evidence and recovery boundaries;
3. **Hardening for paid root-enthusiast software**: server-signed grants, strict device binding, asset encryption, runtime state fitting, packers/VMP, and KPM-based approaches used only when there is a genuine EL1 requirement.

## Important Scope Note

The commercial hardening part applies only to:

> Commercial paid software that was designed from the start for root/modding users.

It does not apply to ordinary consumer apps, banking/payment apps, or general apps that merely want to tolerate a few rooted users.

This target audience is assumed to understand that flashing, swapping kernels, installing modules, and system upgrades can change device identity, and to accept:

- strict device information binding;
- fail-closed behavior after fingerprint drift;
- manual unbinding through a web portal;
- unbinding cooldowns, rate limits, and manual review where necessary.

False positives triggered by a user's own modding activity are therefore an explicitly accepted product security trade-off, not automatically treated as a design defect.

## Contents

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

The build artifact lives at:

```text
dist/android-root-skillkit.skill
```

`.skill` is a ZIP file containing the `android-root-skillkit/` root directory.

## Usage

Import `dist/android-root-skillkit.skill` into an AI client that supports Skills, or drop the `android-root-skillkit/` directory straight into the client's Skills directory.

Answers about versions, whether a feature is built in, detection surface, and module compatibility must re-check the upstream source, PRs, releases, or the author's channels for the target version. `SOURCES.md` only records a snapshot of this formal review; it is not permanent fact.

## Security Boundaries

This project provides defensive, analytical, architectural-review, and security-design knowledge. It does not provide destructive code targeting real devices or executable partition-erasure procedures, and it makes no promise of:

- absolute undetectability;
- absolute uncrackability;
- absolute immunity to bricking;
- resistance to arbitrary malicious KPMs, arbitrary kernel execution, EL2/TEE/RPMB, storage firmware, or physical attacks.

Anti-bricking experiments should only use disposable loop/virtual block devices.

## Review Notes

The content was partly compiled with AI assistance, but sensitive conclusions about major versions were verified against upstream source before the 2026-08-08 public release. See [`SOURCES.md`](SOURCES.md) and [`CHANGELOG.md`](CHANGELOG.md) for review commits and known boundaries.

## License

[MIT](LICENSE)
