# 自动化工具

本工具支持 Windows 和 Mac 操作系统。以下说明适用于所有这些平台，除非特别注明。

## 前置要求

1. Python 3.7 或更高版本
   - Windows 用户：
     - 访问 [Python 官方网站](https://www.python.org/downloads/windows/)
     - 下载并安装 Python，确保勾选"Add Python to PATH"选项
   - Mac 用户（以下步骤基于 AI 生成，可能需要进一步验证）：
     - 推荐使用 Homebrew 安装 Python：
       ```
       /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
       brew install python
       ```
     - 或访问 [Python 官方网站](https://www.python.org/downloads/mac-osx/) 下载安装程序

2. pip（Python 包管理器，通常随 Python 一起安装）

3. Git
   - Windows 用户：访问 [Git for Windows](https://gitforwindows.org/) 下载并安装
   - Mac 用户（以下步骤基于 AI 生成，可能需要进一步验证）：
     - 通过 Homebrew 安装：`brew install git`
     - 或下载 [Git for Mac](https://git-scm.com/download/mac)

## 安装说明

1. 克隆仓库：
   ```
   git clone https://github.com/yiyi-20/automation.git 
   cd automation 
   ```

2. 创建并激活虚拟环境（可选但推荐）：
   - Windows：
     ```
     python -m venv venv
     venv\Scripts\activate
     ```
   - Mac（以下步骤基于 AI 生成，可能需要进一步验证）：
     ```
     python3 -m venv venv
     source venv/bin/activate
     ```

3. 安装所需的依赖：
   ```
   pip install -r requirements.txt
   ```

## 使用方法

1. 确保您在项目根目录下，并且虚拟环境已激活（如果使用）。

2. 运行 Flask 应用：
   ```
   python run.py # 访问
   ```
   注意：数据库会在应用首次运行时自动初始化，无需手动操作。

3. 访问应用：
   - 在本地浏览器中访问 `http://localhost:5000` 来访问应用。
   - 同一网络内的其他设备可以通过 `http://[执行应用的电脑IP]:5000` 来访问应用。
     例如：如果您的电脑 IP 是 192.168.1.100，其他 192.168.1.xxx 的设备可以访问 `http://192.168.1.100:5000`。

## 注意事项
- 确保您的防火墙允许应用程序访问网络。
- 如果遇到任何问题，请查看 `logs/flask.log` 文件以获取详细的错误信息。

### Windows 用户注意事项
- 如果在命令行中遇到 "flask: command not found" 错误，请尝试使用 `python -m flask run` 来运行应用。
- 确保您的 Python 安装路径已添加到系统的 PATH 环境变量中。

### Mac 用户注意事项（以下内容基于 AI 生成，可能需要进一步验证）
- 如果您使用的是系统自带的 Python，可能需要使用 `sudo` 来安装全局包。
- 确保已安装 Xcode 命令行工具：`xcode-select --install`
- 使用 `python3` 命令代替 `python` 命令，除非您已经设置了别名。
