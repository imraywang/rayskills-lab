<div align="center">

# rayskills-lab · 孵化中的实验 Skill

**[rayskills](https://github.com/imraywang/rayskills) 的试验田：这里的 Skill 还没毕业——随时会改、会坏、会消失。**

</div>

---

## 这个仓库是什么

[rayskills](https://github.com/imraywang/rayskills) 是发布线：全量安装、结构校验与 eval 全绿、README 里的每个徽章都是承诺。

**rayskills-lab 是孵化线**：新 Skill 在这里公开开发和真实使用，达到毕业标准后整目录迁入 rayskills。两条线的区别不是私有与公开，而是**承诺等级**——lab 里的一切明确标注"实验性"。

| | rayskills | rayskills-lab |
|---|---|---|
| 安装方式 | 全量安装，`/ray` 统一路由 | 只装你需要的单个 Skill |
| 质量承诺 | 结构校验 + evals + 对照实测全绿 | 无承诺，可能随时变更或删除 |
| 接口稳定性 | 语义化演进，不随意破坏 | 随时可能重命名、改参数、改行为 |

已安装的 lab Skill 与 rayskills 装进同一个本地目录，`/ray` 路由照常识别，两边可以混用。

## 安装（只装单个，不要全装）

先看仓库里有什么可装：

```bash
npx -y skills add imraywang/rayskills-lab -l
```

只装你需要的那一个。**`-s` 不能省**——skill 名放在别的位置会被忽略，变成整仓库全装：

```bash
npx -y skills add imraywang/rayskills-lab -g -s <skill名> -y
```

不要使用 `--all`（它是 `--skill '*' --agent '*' -y` 的缩写）——孵化区按定义不适合整包安装。
输出里若出现个别 agent 不支持全局安装的提示（如 PromptScript），忽略即可，不影响其他 agent。
装之前读一下该 Skill 目录里的 SKILL.md，确认它处于什么状态。

## ⚠️ 免责声明

- 这里的 Skill **没有质量承诺**：可能有未修复的边界问题，eval 可能不全或不过。
- 接口**随时会破坏性变更**，更新后行为可能与你上次使用时不同。
- Skill 可能**随时被删除**（毕业迁走，或实验失败归档）。
- 涉及写文件、发布、部署等动作的 Skill，使用前自行确认它的安全边界。

## 孵化中

| Skill | 一句话 | 状态 | 开始孵化 |
|---|---|---|---|
| [ray-dashboard](skills/ray-dashboard/) | 给本地知识库安装、启动、升级和诊断零依赖的可视化工作台 | 安装/启停/升级/诊断链路已实测；launchd 自启仅文档 | 2026-07 |

## 已毕业 🎓

| Skill | 毕业去向 | 毕业日期 |
|---|---|---|
| _暂无_ | | |

## 毕业标准

一个 Skill 迁入 rayskills 前，必须**全部满足**以下六条（可机械检查，不接受"感觉差不多了"）：

1. **结构校验 pass**：通过 rayskills 工具链的 validate。
2. **evals 全绿**：至少覆盖 happy-path 与 boundary 两类用例，全部通过。
3. **触发准确**：description 经过 benchmark 验证，该触发时触发、不该触发时不触发。
4. **真实使用满两周**：在作者自己的真实工作流中连续使用，不是只跑过 demo。
5. **无个人信息**：路径、账号、API 配置全部外置，仓库内零个人数据。
6. **文档完整**：SKILL.md 写清固定原则、安全边界与完成标准，陌生人可直接使用。

## 毕业与降级流程

**毕业**：整目录复制进 rayskills 的 `skills/` 并入构建 → 从本仓库删除该目录 → 在上方"已毕业"表登记去向。Skill 目录自包含，迁移就是一次复制。

**降级**：rayskills 中质量掉队或不再维护的 Skill，可退回本仓库继续孵化或直接归档，主仓库的徽章数字随之更新。发布线只进不出会烂，这条路必须存在。

## 开发新 Skill

从 `templates/skill-template/` 复制一份骨架到 `skills/<新名字>/` 开始，用 skill-creator 做 evals 和
description benchmark。孵化期就按毕业标准的方向写，毕业那天不用返工。

**约定：`skills/` 下只放可安装的真实 Skill。**安装器会把该目录下的每一个 Skill 都视为可安装对象，
模板、草稿、废弃实验都不能放在这里。

## License

[CC BY-NC 4.0](LICENSE)，与 rayskills 一致——毕业迁移不产生许可摩擦。
