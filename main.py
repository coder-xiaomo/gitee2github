
# #####################################################################################
# 脚本逻辑
# 首先在当前目录下创建一个临时目录，然后让用户授权Gitee和GitHub账号以获得账号中的所有Git仓库信息
# 最后使用 `git clone --mirror xxx` 命令克隆裸仓库，并使用 `git push --mirror xxx` 推送，
# 以达到转移仓库的目的
# #####################################################################################
# 脚本使用前置条件
#  - 电脑上已安装Python，并且安装了下方import的Python库
#    - 没有安装的话可以使用 `pip install <库名>` 进行安装
#    - 建议先配置好pip国内镜像，再使用pip安装，这样安装速度会快一些
#  - 电脑上已安装Git
#  - 已经配置好本地SSH信息
#    - 即可以直接使用git命令克隆或推送SSH地址git@git___.com:xxx.git
#    - 特别是对于您的私有仓库，只有配置好了SSH公钥的情况下才能直接使用git命令完成克隆
#  - 对于大多数在国内的用户，需要准备一个梯子，否则GitHub请求很容易超时，无法获取仓库信息
#    - 如果GitHub不需要使用代理，请将下方 githubProxies 变量中的代理配置设置为空
#    - 使用梯子请求的话，请将下方 githubProxies 变量中的代理配置设置为梯子的IP地址
#    - 如果Git提示SSL验证失败，可以使用 `git config --global http.sslVerify false` 关闭SSL验证
# #####################################################################################
# 注意事项
# - 使用时，需要使用Gitee和GitHub进行授权
# - 使用前，请注意备份数据，虽然我们已经使用我们自己的账号测试脚本没有问题，
#   但受由于执行环境的不同，不排除脚本出现错误等情况。
#   若因脚本执行错误或者您的失误导致数据丢失，我们不承担责任，感谢您的理解！
# #####################################################################################

import os # 执行系统命令
import requests # 发送请求
import signal # 捕获Ctrl+C退出信号
import webbrowser # 打开浏览器
import time # 时间模块 (倒计时退出，创建带时间戳的工作目录)
import shutil # 文件夹操作 （递归删除文件夹）
import json # 读写JSON
import configparser # 读取ini配置文件
import copy # 字典深拷贝

# ######################################## 工作路径 ########################################
# 当前目录
CurrentDir = os.path.dirname(os.path.abspath(__file__))

# 临时工作目录
WorkingDirName = "WorkingDir" # './temp-' + str(int(time.time() * 10 ** 6))
WorkingDir = os.path.abspath(os.path.join(CurrentDir, WorkingDirName))

# 设置保存路径
GlobalVarsSavePath = os.path.abspath(os.path.join(WorkingDir, "GlobalVars.json"))

# 准备工作目录
from assets.prepareWorkingDir import prepareWorkingDir
prepareWorkingDir(CurrentDir = CurrentDir, WorkingDir = WorkingDir)

# ######################################## 读取配置 ########################################
# 读取配置文件
from assets.readConfigFile import readConfigFile
config = readConfigFile(os.path.abspath("config.ini"))

if not 'Gitee' in config or not 'GitHub' in config:
    print("[error] 配置文件读取失败，请检查配置文件是否正确")
    exit()

if not 'ClientID' in config['Gitee'] or not 'ClientSecret' in config['Gitee']:
    print("[error] Gitee ClientID或ClientSecret配置错误，请检查配置文件是否正确")
    exit()
if not 'ClientID' in config['GitHub'] or not 'ClientSecret' in config['GitHub']:
    print("[error] GitHub ClientID或ClientSecret配置错误，请检查配置文件是否正确")
    exit()

# ClientID 与 ClientSecret
# Gitee
GiteeClientID = config['Gitee']['ClientID']
GiteeClientSecret = config['Gitee']['ClientSecret']
# GitHub
GitHubClientID =config['GitHub']['ClientID']
GitHubClientSecret = config['GitHub']['ClientSecret']

# Protocol: https or ssh
GiteeProtocol = 'https'
GitHubProtocol = 'https'
# Gitee
if 'Protocol' in config['Gitee'] and config['Gitee']['Protocol'] == 'ssh':
    GiteeProtocol = "ssh"
# GitHub
if 'Protocol' in config['GitHub'] and config['GitHub']['Protocol'] == 'ssh':
    GitHubProtocol = "ssh"

# 代理
# Gitee请求代理，默认为不使用代理  { "http": None, "https": None }
giteeProxies = { "http": None, "https": None }
if 'Proxy' in config['Gitee'] and config['Gitee']['Proxy'] != "":
    giteeProxies['http'] = config['Gitee']['Proxy']
    giteeProxies['https'] = config['Gitee']['Proxy']
# GitHub请求代理，默认为使用本地代理  { "http": "127.0.0.1:15732", "https": "127.0.0.1:15732" }
# python3 requests使用proxy代理,cookies https://www.cnblogs.com/lshan/p/11878638.html
githubProxies = { "http": None, "https": None }
if 'Proxy' in config['GitHub'] and config['GitHub']['Proxy'] != "":
    githubProxies['http'] = config['GitHub']['Proxy']
    githubProxies['https'] = config['GitHub']['Proxy']

# 请求超时时间
timeout = 10
if 'RequestTimeout' in config['Common'] and config['Common']['RequestTimeout'].isdigit():
    timeout = int(config['Common']['RequestTimeout'])
    print("[info] 请求超时时间设置为：" + str(timeout) + "秒")

# ######################################## 主函数 ########################################
if __name__ == '__main__':
    """
    主函数
    """
    from assets.common import saveJSON, readJSON, fileExists

    GlobalVars = {
        'lastRunTime': time.time(),
        'giteeRepos': {},
        'githubRepos': {},
        'RepoMatch': {},
    }

    # 如果存在之前的获取结果，则首先导入先前的结果
    importFileOrNot = ''
    if not fileExists(WorkingDir): # 如果工作目录不存在，那么不可导入
        importFileOrNot = 'n'
    if fileExists(GlobalVarsSavePath): # 如果JSON文件存在，那么询问用户否导入
        while(importFileOrNot != 'y' and importFileOrNot != 'n'):
            importFileOrNot = input("[info] 发现上次运行结果，是否读取？(y/n) 默认为y ")
            if importFileOrNot == '':
                importFileOrNot = 'y'
    else: # 如果JSON文件不存在，那么不可导入
        importFileOrNot = 'n'

    if importFileOrNot == 'y': # 导入
        # 读取上次的结果
        GlobalVars = readJSON(GlobalVarsSavePath)
        GlobalVars['RepoMatch'] = {}
        print("[info] 导入JSON文件成功")

    # 注册 Ctrl+C 退出处理程序
    # from assets.defineWorkingDirCleanFunction import defineWorkingDirCleanFunction
    # defineWorkingDirCleanFunction(saveJSONFunction = saveJSON)

    # 询问用户是否重新获取Gitee仓库列表
    if GlobalVars['giteeRepos']:
        userInput = 'unknown'
        while userInput != 'y' and userInput != 'n' and userInput != '':
            userInput = input("[info] 已经获取过Gitee仓库列表，是否重新获取？(y/n) 默认为n ")
        if userInput == 'y':
            GlobalVars['giteeRepos'] = {} # 清空之前的记录

    if not GlobalVars['giteeRepos']:
        # 读取 Gitee 仓库列表
        from assets.giteeOauth import giteeOauth
        [GlobalVars['giteeReposOrigin'], GlobalVars['giteeRepos']] = \
            giteeOauth(GiteeClientID = GiteeClientID, GiteeClientSecret = GiteeClientSecret, giteeProxies = giteeProxies, timeout = timeout)
        print("[info] 获取到 {} 个Git仓库".format(len(GlobalVars['giteeRepos'])))
        # 保存JSON文件
        saveJSON(GlobalVars, GlobalVarsSavePath)
        print("[info] 保存JSON文件完成")

    # 询问用户是否重新获取Gitee仓库列表
    if GlobalVars['githubRepos']:
        userInput = 'unknown'
        while userInput != 'y' and userInput != 'n' and userInput != '':
            userInput = input("[info] 已经获取过GitHub仓库列表，是否重新获取？(y/n) 默认为n ")
        if userInput == 'y':
            GlobalVars['githubRepos'] = {} # 清空之前的记录

    if not GlobalVars['githubRepos']:
        # 读取 GitHub 仓库列表
        from assets.githubOauth import githubOauth
        [GlobalVars['githubReposOrigin'], GlobalVars['githubRepos']] = \
            githubOauth(GitHubClientID = GitHubClientID, GitHubClientSecret = GitHubClientSecret, githubProxies = githubProxies, timeout = timeout)
        print("[info] 获取到 {} 个Git仓库".format(len(GlobalVars['githubRepos'])))
        # 保存JSON文件
        saveJSON(GlobalVars, GlobalVarsSavePath)
        print("[info] 保存JSON文件完成")

    # 匹配仓库
    from assets.repoMatching import repoMatching, printMatchintInfo
    matchList = repoMatching(repo1 = GlobalVars['giteeRepos'], repo2 = GlobalVars['githubRepos'])
    GlobalVars['RepoMatch'] = matchList

    # 保存JSON文件
    saveJSON(GlobalVars, GlobalVarsSavePath)
    print("[info] 保存JSON文件完成")

    # 打印匹配信息
    printMatchintInfo(matchList, repo1Name = "Gitee", repo2Name = "GitHub")

    # 转移仓库
    input("[info] 确认无误后按回车继续: ")
    print("[info] 开始同步仓库")
    from assets.transferRepos import transferRepos
    transferRepos(matchList.get('match'), WorkingDir, fromRepoProtocol = GiteeProtocol, toRepoProtocol = GitHubProtocol)
    print("程序结束，将退出")
    os.system("pause")
