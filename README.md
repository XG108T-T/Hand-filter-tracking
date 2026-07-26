# Hand-filter-tracking

基于 MediaPipe 的实时手指滤镜交互工具  
灵感来源于 [RealityFrame](https://github.com/RuthvikJ/RealityFrame)，用 Python 重新实现并加入了更多玩法。

---

---项目打包由"user-415"提供在此感谢
---可直接下载exe版本，无需运行环境
---https://github.com/XG108T-T/Hand-filter-tracking/releases/tag/original_version

## 📁 文件说明

| 文件 / 文件夹 | 作用 |
|---------------|------|
| `XXG/` | 文件夹里有一键安装运行环境的脚本，双击即可自动配置 Python 环境 |
| `FingerMagic_vx.py` | 基础模板版本，无特效，适合想自己修改代码的开发者 |
| `FingerMagic_v3.py` | 正式版本，功能完整，推荐直接运行这个 |
| `hand_landmarker.task` | 核心模型文件（已包含在仓库中，无需额外下载） |
| `requirements.txt` | Python 依赖清单 |
| `setup.bat` / `setup.sh` | 一键安装依赖的脚本 |

> ✅ 所有文件均已包含，下载即可使用，无需去其他地方额外下载。

---

## 🎮 玩法说明

用双手的手指拉出一个四边形，框内会自动应用特效。

- 伸出 2-5 根手指，调整四边形大小
- 移动双手，特效区域会跟随变化
- 按快捷键切换不同的滤镜风格

---

## 🎯 快捷键

| 按键 | 功能 |
|------|------|
| `2-5` | 选择参与的手指数量 |
| `Q` `W` `E` `R` | 切换滤镜风格（漫画/反转/像素/热感） |
| `1` | 切换简单 / 丰富模式 |
| `空格` | 黑白反转 |
| `ESC` | 退出程序 |

---

## 🚀 快速开始

### 第一步：安装 Python（如果没有）
访问 [python.org](https://www.python.org/downloads/) 下载并安装 Python 3.8 或更高版本。  
**安装时务必勾选“Add Python to PATH”**。

### 第二步：安装依赖
- **Windows 用户**：双击 `XXG` 文件夹内的 `setup.bat`
- **Mac/Linux 用户**：运行 `bash setup.sh`

### 第三步：运行程序
- **正式版**：双击 `FingerMagic_v3.py` 或在终端运行 `python FingerMagic_v3.py`
- **开发版**：如果想修改代码，可以编辑 `FingerMagic_vx.py`

---

## 🤝 贡献

欢迎大家在此基础上修改、优化，让这个项目变得更好！

- 可以提交 Issue 或 Pull Request
- 可以自由修改代码，但禁止商业用途

---

## 📄 许可证

本项目采用 **CC BY-NC 4.0** 许可证，禁止商业使用，允许自由修改和分享。
