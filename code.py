
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
import signal
import webbrowser # 打开浏览器
import time # 时间模块 (倒计时退出，创建带时间戳的工作目录)
import shutil # 文件夹操作 （递归删除文件夹）
import json # 读写JSON

# ######################################## 配置 ########################################
# Gitee
GiteeClientID = 'ce043c6768fcddf97b334f5d3615ff20e9448eedf8a0c2701015de3e831f3f59' # 'YOUR_CLIENT_ID'
GiteeClientSecret = '334742850f8dd650239cc8d3c7522090d22c6f7aeab12a340a532bc8de0d2b0d' # 'YOUR_CLIENT_SECRET'

# GitHub
GitHubClientID = 'Iv1.0c2a4dbf1b897e8f' # 'YOUR_CLIENT_ID'
GitHubClientSecret = 'bcc97770136b22abce5f4bb0444df0621c4386b2' # 'YOUR_CLIENT_SECRET'

# Gitee请求代理，默认为不使用代理  { "http": None, "https": None }
giteeProxies = { "http": None, "https": None }

# GitHub请求代理，默认为使用本地代理  { "http": "127.0.0.1:15732", "https": "127.0.0.1:15732" }
githubProxies = { "http": "127.0.0.1:15732", "https": "127.0.0.1:15732" }
# python3 requests使用proxy代理,cookies https://www.cnblogs.com/lshan/p/11878638.html

# GitHub请求超时时间
timeout = 5

# ######################################## 工作路径 ########################################
# 当前目录
CurrentDir = os.path.dirname(os.path.abspath(__file__))

# 临时工作目录
TempWorkingDirName = "TempWorkingDir" # './temp-' + str(int(time.time() * 10 ** 6))
TempWorkingDir = os.path.abspath(os.path.join(CurrentDir, TempWorkingDirName))

# 设置保存路径
GlobalVarsSavePath = os.path.abspath(os.path.join(TempWorkingDir, "../GlobalVars.json"))
RepoMatchSavePath = os.path.abspath(os.path.join(TempWorkingDir, "../RepoMatch.json"))

# ######################################## 全局变量 ########################################
giteeRepos = {}
githubRepos = {}

GlobalVars = {
    'lastRunTime': time.time(),
    'giteeRepos': giteeRepos,
    'githubRepos': githubRepos
}

def prepareWorkingDir():
    """
    准备工作目录
    """
    print("################################ 正在准备工作目录 ################################")
    print("当前目录", CurrentDir) # 获取当前文件所在目录
    print("工作目录", TempWorkingDir)
    # print(os.getcwd()) # 获取当前脚本运行目录

    if os.path.exists(TempWorkingDir):
        # 工作目录已存在，如果非空就创建
        if not os.listdir(TempWorkingDir):
            print("工作目录已存在且为空，无需创建")
        else:
            print('工作目录已存在且非空，请检查是否有其他程序正在使用，如果确认无其他程序在使用，请手动删除工作目录，然后重试！')
            print()
            print("是否删除工作目录中的文件? (Y: 删除, N: 不删除)")
            userInput = ''
            while userInput == '':
                userInput = input("\r>").strip().lower ()
            if userInput in ['y', 'yes']:
                # os.rmdir(TempWorkingDir) # 只能删除空文件夹
                shutil.rmtree(TempWorkingDir)    #递归删除文件夹
                os.mkdir(TempWorkingDir)
                print("成功清空工作目录", TempWorkingDir)
            else:
                input('按回车键退出...')
                exit()
    else:
        # 工作目录不存在，创建该目录
        os.mkdir(TempWorkingDir)
        print("成功创建工作目录", TempWorkingDir)


    # os.mkdir(TempWorkingDir)
    # os.makedirs(TempWorkingDir)

    # os.system("chdir")
    # print(__file__)

def defineWorkingDirCleanFunction():
    """
    定义Ctrl+C退出时 工作目录清理函数
    """
    def cleanWhenExit(signum, frame):
        print()
        print('程序正在清理工作目录，准备退出...')
        os.rmdir(TempWorkingDir)
        print('完成！')
        print()
        for countdown in range(3, 0, -1):
            print('\r' + "{} 秒后退出{}".format(countdown, '.' * (4 - countdown)), end='')
            time.sleep(1)
        exit()
    # 注册信号处理函数
    signal.signal(signal.SIGINT, cleanWhenExit)
    signal.signal(signal.SIGTERM, cleanWhenExit)

def giteeOauth():
    print("################################ Gitee 授权 ################################")
    input("按回车开始进行Gitee账号授权：")

    # ######################################## 获取Gitee用户的 access_token ########################################
    # Api文档： https://gitee.com/api/v5/oauth_doc#/
    # 认证地址
    oauth_url = 'https://gitee.com/oauth/authorize?client_id={ClientID}&redirect_uri={redirect_uri}&response_type=code&scope=user_info%20projects' \
        .format(ClientID=GiteeClientID, redirect_uri='https://www.only4.work/appHelper/gitee_show_code_param.php')

    # 打开浏览器让用户授权
    webbrowser.open(oauth_url)

    # 让用户手动输入授权码
    print("请在新打开的页面进行授权，授权完成后，请将授权码拷贝到此处，然后按回车继续")
    code = input("您的授权码：")

    while(True):
        try:
            r = requests.post('https://gitee.com/oauth/token', params = {
                "grant_type": "authorization_code",
                "code": code,
                "client_id": GiteeClientID,
                "redirect_uri": "https://www.only4.work/appHelper/gitee_show_code_param.php",
                "client_secret": GiteeClientSecret,
            }, proxies = giteeProxies, timeout = timeout)
            break
        except:
            continue

    # print(r.text)
    access_token = r.json()['access_token']
    print("您的access_token为：" + access_token)
    # {"access_token":"83b5de53fc28079d80830983be587774","token_type":"bearer","expires_in":86400,"refresh_token":"6d445558db02909f8755383193bfb87648b897b6f92654e4f5d3e6ad61b0d515","scope":"user_info projects","created_at":1647013348}

    # ######################################## 获得用户仓库信息 ########################################
    # Api文档： https://gitee.com/api/v5/swagger#/getV5UserRepos
    while(True):
        try:
            r = requests.get('https://gitee.com/api/v5/user/repos', params = {
                "access_token": access_token,
                "visibility": "all",
                "sort": "full_name",
                "page": 1,
                "per_page": 100,
            }, proxies = giteeProxies, timeout = timeout)
            break
        except:
            continue

    # print(r.text)
    print()
    print("################################ 成功获取到您的仓库信息 ################################")
    for repo in r.json():
        print(repo['human_name'])
        print(repo['html_url'])
        print(repo['full_name'])
        print()
        # giteeRepos.append()
        giteeRepos[repo['full_name']] = {
            'human_name': repo['human_name'],
            'html_url': repo['html_url'],
            'full_name': repo['full_name'],
            # 'path': repo['path'], # 仓库的路径  如 /only4/appHelper 的 appHelper
            'name': repo['name'], # 仓库名称  如 仓库同步助手
            # 'public': repo['public'], # 是否公开
            'private': repo['private'], # 是否私有
            # 'internal': repo['internal'], # 是否内部仓库
            # 'empty_repo': repo['empty_repo'], # 是否为空仓库
            'pushed_at': repo['pushed_at'], # 最后提交时间
        }
    print("######################################################################################")

def githubOauth():
    print("################################ GitHub 授权 ################################")
    input("按回车开始进行GitHub账号授权：")

    # ######################################## 获取GitHub用户的 access_token ########################################
    # Api文档：
    # https://docs.github.com/cn/developers/apps/building-oauth-apps/authorizing-oauth-apps
    # https://docs.github.com/cn/developers/apps/building-oauth-apps/scopes-for-oauth-apps
    # 认证地址
    oauth_url = 'https://github.com/login/oauth/authorize?client_id={ClientID}&redirect_uri={redirect_uri}&response_type=code&scope=user,repo' \
        .format(ClientID=GitHubClientID, redirect_uri='https://www.only4.work/appHelper/github_show_code_param.php')

    # 打开浏览器让用户授权
    webbrowser.open(oauth_url)

    # 让用户手动输入授权码
    print("请在新打开的页面进行授权，授权完成后，请将授权码拷贝到此处，然后按回车继续")
    code = input("您的授权码：")

    while(True):
        try:
            r = requests.post('https://github.com/login/oauth/access_token', headers = {
                'Accept': 'application/json'
            }, params = {
                "code": code,
                "client_id": GitHubClientID,
                "redirect_uri": "https://www.only4.work/appHelper/github_show_code_param.php",
                "client_secret": GitHubClientSecret,
            }, proxies = githubProxies, timeout = timeout)
            break
        except:
            continue

    print(r.text)
    access_token = r.json()['access_token']
    print("您的access_token为：" + access_token)
    # {"access_token":"ghu_NgIJEFtrQz4FtTqfewVaHlR9Xnb30R26oMwM","expires_in":28800,"refresh_token":"ghr_mu8iw6A33ae1AoIo3hMFVX7VssbPmGIlfSKyc2CTQIPootRSMnr48c3WVevQpYfwLL9MaQ0vWvTR","refresh_token_expires_in":15897600,"token_type":"bearer","scope":""}

    # ######################################## 获得用户仓库信息 ########################################
    while(True):
        try:
            # Api文档： https://docs.github.com/cn/rest/reference/repos#list-repositories-for-the-authenticated-user
            r = requests.get('https://api.github.com/user/repos', headers = {
                'Accept': 'application/vnd.github.v3+json',
                "Authorization": "token " + access_token,
                # 👆 https://developer.github.com/changes/2020-02-10-deprecating-auth-through-query-param/
            }, params = {
                "access_token": access_token,
                "visibility": "all",
                "sort": "full_name",
                "page": 1,
                "per_page": 100,
            }, proxies = githubProxies, timeout = timeout)
            break
        except:
            continue

    # print(r.text)
    print()
    print("################################ 成功获取到您的仓库信息 ################################")
    for repo in r.json():
        print(repo['full_name'])
        print(repo['html_url'])
        # githubRepos.append()
        githubRepos[repo['full_name']] = {
            # 'human_name': repo['human_name'],
            'html_url': repo['html_url'],
            'full_name': repo['full_name'],
            # 'path': repo['path'], # 仓库的路径  如 /only4/appHelper 的 appHelper
            'name': repo['name'], # 仓库名称  如 仓库同步助手
            # 'public': repo['public'], # 是否公开
            'private': repo['private'], # 是否私有
            # 'internal': repo['internal'], # 是否内部仓库
            # 'empty_repo': repo['empty_repo'], # 是否为空仓库
            'pushed_at': repo['pushed_at'], # 最后提交时间
        }
        print()
    print("######################################################################################")


def repoMatching(giteeRepos, githubRepos):
    matchingList = {
        'matchedList': {},
        'mismatchedList': {
            'gitee': [],
            'github': [],
        },
    }
    for giteeRepoFullName in giteeRepos.keys():
        # print(giteeRepoFullName)
        if(giteeRepoFullName in githubRepos.keys()):
            matchingList.get('matchedList')[giteeRepoFullName] = {
                'from': giteeRepos[giteeRepoFullName],
                'to': githubRepos[giteeRepoFullName],
            }
            # del giteeRepos[giteeRepoFullName]
            del githubRepos[giteeRepoFullName]
        else:
            # del giteeRepos[giteeRepoFullName]
            matchingList.get('mismatchedList').get('gitee').append(giteeRepos[giteeRepoFullName])

    for githubRepoFullName in githubRepos.keys():
        # print(githubRepoFullName)
        matchingList.get('mismatchedList').get('github').append(githubRepos[githubRepoFullName])
        # del githubRepos[githubRepoFullName]
    return matchingList

def printMatchintInfo(matchingList):
    print("  ################## 以下仓库会被同步 ################## ")
    print("  Gitee 与 GitHub 两侧相同的仓库")
    for i in matchingList.get('matchedList'):
        print('      ' + i)
    print()
    print("  ################## 以下仓库不会同步 ################## ")
    print("  Gitee 有但是 GitHub 没有的仓库")
    for i in matchingList.get('mismatchedList').get('gitee'):
        print('      ' + i['html_url'])
    print()
    print("  GitHub 有但是 Gitee 没有的仓库")
    for i in matchingList.get('mismatchedList').get('github'):
        print('      ' + i['html_url'])

def transferRepos(matchedList, TempWorkingDir):
    # print(matchedList)
    # 切换路径
    targetPath = os.path.abspath(TempWorkingDir)
    os.chdir(targetPath)
    if(os.path.abspath(os.getcwd()) != targetPath):
        print("[error] 切换路径失败")
        print("当前路径", os.path.abspath(os.getcwd()))
        print("想要切换到的路径", targetPath)
        input("按回车键退出...")
        exit()

    for repoFullName in matchedList:
        repo = matchedList[repoFullName]
        print(repo['from'])
        preCommand = [
            # "cd .", # 切换到当前目录下
            # "mkdir temp_repo_dir", # 创建临时目录
            # "cd temp_repo_dir", # 切换到临时目录
            'chdir',
            "git clone --mirror {repo_url}".format(repo_url = repo['from']['html_url']), # 下载仓库
            "cd {folder_name}".format(folder_name = repo['from']['name'] + ".git"), # 切换到仓库目录
            "git push --mirror {repo_url}".format(repo_url = repo['to']['html_url']), # 同步仓库
        ]
        for commandForExecute in preCommand:
            print(commandForExecute)
            os.system(commandForExecute)

        os.system("pause")

    # @echo off

    # :: 创建文件夹
    # mkdir D:\gitTransTempDir

    # :: 切换到文件夹
    # D:
    # cd D:\gitTransTempDir

    # :: 如果之前有没删除的话就删除
    # rd /s /q D:\gitTransTempDir\chrome-extension.git
    # cls

    # git clone --mirror https://gitee.com/bitdance-team/chrome-extension

    # cd ./chrome-extension.git

    # git push --mirror git@github.com:bitdance-team/chrome-extension.git

    # cd ../../

    # rd /s /q D:\gitTransTempDir

    # pause

def saveJSON(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def readJSON(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def fileExists(filename):
    return os.path.exists(filename)

if __name__ == '__main__':
    """
    主函数
    """
    if fileExists(GlobalVarsSavePath):
        print("[info] JSON文件已存在，跳过获取仓库信息")
        GlobalVars = readJSON(GlobalVarsSavePath)
        giteeRepos = GlobalVars['giteeRepos']
        githubRepos = GlobalVars['githubRepos']
        print("[info] JSON文件加载完成")
    else:
        prepareWorkingDir()
        print("[info] 工作目录准备完成")

        defineWorkingDirCleanFunction()
        print("[info] 工作目录清理函数准备完成")

        giteeOauth()
        print("[info] Gitee账号授权完成")

        githubOauth()
        print("[info] GitHub账号授权完成")

        saveJSON(GlobalVars, GlobalVarsSavePath)
        print("[info] 保存JSON文件完成")

    matchingList = repoMatching(giteeRepos, githubRepos)
    print("[info] 仓库匹配完成")

    # 打印匹配信息
    printMatchintInfo(matchingList)

    # 转移仓库
    transferRepos(matchingList.get('matchedList'), TempWorkingDir)
    exit()

    # 保存匹配信息
    saveJSON(matchingList, RepoMatchSavePath)

    # print("[info] 开始同步仓库")


    # input("程序执行完毕，按回车键继续...")

input("按回车键退出...")
exit()
