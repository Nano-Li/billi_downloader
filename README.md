# billi_downloader

面向 Obsidian 知识库的轻量下载 skill。直接调用 [yutto](https://github.com/yutto-dev/yutto)，根据用户提供的链接、SESSDATA、视频或音频选项，将资源保存到指定位置。

普通视频保留声音；仅音频使用 yutto 的 `--audio-only`。不额外生成笔记、总结或转录。默认不下载弹幕、字幕和封面。分 P、批量、画质和格式选择直接使用 yutto 原生参数。

## 安装到知识库

将本仓库完整目录保存为 `billi_downloader`，放入调用工具支持的知识库内 skill 目录，或在调用工具中将该目录配置为 skill 来源。入口是 [SKILL.md](SKILL.md)，`agents/openai.yaml` 提供可选界面信息。Codex、Claudian 的发现路径由各自版本和配置决定，目录复制本身不代表已被工具加载；调用模型还需要能够执行本地命令。

skill 目录和知识库根目录可以不同。虚拟环境统一创建在知识库根目录 `.venv`，不放进 skill 的发布内容。每台电脑独立安装环境，不同步 `.venv`。

需要 Python 3.11 或更新版本，以及安装依赖时的网络访问。下面以 Windows PowerShell 为例，将两个路径替换为实际位置：

```powershell
$vaultPath = 'D:\MyVault'
$skillPath = 'D:\MyVault\skills\billi_downloader'
python "$skillPath\scripts\setup.py" --vault "$vaultPath"
$pythonPath = Join-Path $vaultPath '.venv\Scripts\python.exe'
```

安装脚本复用已有 `.venv`，按 `requirements.txt` 安装 yutto 2.3.1。优先使用系统 FFmpeg；缺失时安装 `imageio-ffmpeg==0.6.0`，从它提供的二进制中取得 FFmpeg，不修改系统 PATH。安装完成会输出 Python、FFmpeg 的位置和版本。现有环境不完整时停止，不删除重建。

macOS/Linux 使用同一个 `setup.py --vault`，后续 Python 入口为 `<知识库>/.venv/bin/python`。当前版本已在 Windows、Python 3.13 环境验证；其他平台尚未实测。

## 配置 SESSDATA

这里的登录字段名是 `SESSDATA`，也可以输入包含此字段的 Cookie 字符串。`bili_jct` 可选，不需要完整浏览器 Cookie。

在交互终端运行，输入内容不会显示：

```powershell
& $pythonPath "$skillPath\scripts\configure_auth.py"
```

脚本将值写入 yutto 的本机默认认证文件，并使用 `billi_downloader` profile，保留其他 profile。Windows 默认位置为用户目录下的 `AppData\Roaming\yutto\auth.toml`，macOS/Linux 通常为 `~/.config/yutto/auth.toml`；设置 `XDG_CONFIG_HOME` 时遵循 yutto 的规则。脚本输出实际路径，不输出凭据，也不将保存成功误报为登录有效。

也支持 `--auth-file "本机私人文件路径"` 和 `--profile "名称"`。非交互调用可读取已有环境变量 `BILIBILI_SESSDATA`。不要在公开命令、提交或日志中填写真实值。

手动配置时可参考 [auth.example.toml](assets/auth.example.toml)，将填写后的文件保存在知识库同步范围之外。用户已向 Agent 提供凭据时，Agent 可直接编辑这个本机认证文件，不重复要求输入。

检查登录状态：

```powershell
& $pythonPath -m yutto auth status --auth-profile billi_downloader
```

若配置时指定了其他文件，检查和下载命令都应附加 `--auth-file "该文件路径"`。

## 使用

加载 skill 后可以直接告诉 Agent：

> 使用 billi_downloader，将这个 B 站链接下载为带声音的视频，保存到我指定的目录，使用已配置的 SESSDATA。

> 使用 billi_downloader，只下载这个链接的音频，保存到我指定的目录。

也可以直接调用 yutto。以下命令从系统或虚拟环境取得 FFmpeg 路径；将示例链接和输出目录替换为实际值：

```powershell
$ffmpegCommand = Get-Command ffmpeg -ErrorAction SilentlyContinue
$ffmpegPath = if ($ffmpegCommand) { $ffmpegCommand.Source } else {
    & $pythonPath -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())"
}
$videoUrl = 'https://www.bilibili.com/video/实际BV号/'
$outputPath = 'D:\MyVault\Attachments'

# 带声音的视频，不要加 --video-only（该参数会去掉声音）。
& $pythonPath -m yutto $videoUrl -d $outputPath --ffmpeg-path $ffmpegPath --no-danmaku --no-subtitle --no-cover --auth-profile billi_downloader --login-strict

# 仅音频。
& $pythonPath -m yutto $videoUrl -d $outputPath --ffmpeg-path $ffmpegPath --audio-only --no-danmaku --no-subtitle --no-cover --auth-profile billi_downloader --login-strict
```

匿名下载公开资源时去掉 `--auth-profile billi_downloader --login-strict`。指定 MP3 时增加 `--output-format-audio-only mp3`。其余能力参照当前安装版本的 `--help`。不默认使用覆盖参数，下载完成后核对实际文件；批量下载需要核对各项结果。

## 文件与验证范围

- `SKILL.md`：供调用模型读取的下载流程。
- `scripts/setup.py`：知识库虚拟环境和依赖安装。
- `scripts/configure_auth.py`：隐藏输入并保存 yutto 原生认证信息。
- `requirements.txt`：yutto 固定版本。
- `assets/auth.example.toml`：不含真实凭据的配置模板。

已验证依赖安装、认证文件读写及其他 profile 保留、无效输入保护、yutto 视频/音频参数、FFmpeg 本地视频和音频输出。尚未使用真实用户凭据验证 B 站下载；实际下载也受链接、登录状态和账号权限影响。

仓库不包含虚拟环境、用户凭据、下载内容或个人知识库配置。`.gitignore` 仅保护 Git 提交，不会替代其他同步工具的排除设置。
