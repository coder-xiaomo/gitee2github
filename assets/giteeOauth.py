import webbrowser
import requests
import time

def giteeOauth(GiteeClientID, GiteeClientSecret, giteeProxies, timeout):
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

    r = None # 定义变量

    tryTime = 10
    while(tryTime > 0):
        tryTime = tryTime - 1
        try:
            print("正在获取Gitee access_token...")
            r = requests.post('https://gitee.com/oauth/token', params = {
                "grant_type": "authorization_code",
                "code": code,
                "client_id": GiteeClientID,
                "redirect_uri": "https://www.only4.work/appHelper/gitee_show_code_param.php",
                "client_secret": GiteeClientSecret,
            }, proxies = giteeProxies, timeout = timeout)
            break
        except Exception as err:
            print(err)
            print("出错啦，正在重试，还剩{}次机会".format(tryTime))
            time.sleep(1)
            continue

    print("[info] Gitee账号授权完成")

    # print(r.text)
    access_token = r.json()['access_token']
    print("您的access_token为：" + access_token)
    # {"access_token":"83b5de53fc28079d80830983be587774","token_type":"bearer","expires_in":86400,"refresh_token":"6d445558db02909f8755383193bfb87648b897b6f92654e4f5d3e6ad61b0d515","scope":"user_info projects","created_at":1647013348}

    # ######################################## 获得用户仓库信息 ########################################
    # Api文档： https://gitee.com/api/v5/swagger#/getV5UserRepos
    tryTime = 10
    while(tryTime > 0):
        tryTime = tryTime - 1
        try:
            r = requests.get('https://gitee.com/api/v5/user/repos', params = {
                "access_token": access_token,
                "visibility": "all",
                "sort": "full_name",
                "page": 1,
                "per_page": 100,
            }, proxies = giteeProxies, timeout = timeout)
            break
        except Exception as err:
            print(err)
            print("出错啦，正在重试，还剩{}次机会".format(tryTime))
            time.sleep(1)
            continue

    # print(r.text)
    print()
    print("################################ 成功获取到您的仓库信息 ################################")
    giteeRepos = {}
    for repo in r.json():
        print(repo['human_name'])
        print(repo['html_url'])
        print(repo['full_name'])
        print()
        # giteeRepos.append()
        giteeRepos[repo['full_name']] = {
            'human_name': repo['human_name'],
            'html_url': repo['html_url'],
            'ssh_url': repo['ssh_url'],
            'full_name': repo['full_name'],
            # 'path': repo['path'], # 仓库的路径  如 /only4/appHelper 的 appHelper
            'name': repo['name'], # 仓库名称  如 仓库同步助手
            # 'public': repo['public'], # 是否公开
            'private': repo['private'], # 是否私有
            # 'internal': repo['internal'], # 是否内部仓库
            # 'empty_repo': repo['empty_repo'], # 是否为空仓库
            'pushed_at': repo['pushed_at'], # 最后提交时间
        }
    print("[info] Gitee仓库读取完成")
    return [r.json(), giteeRepos]