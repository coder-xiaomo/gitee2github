import webbrowser
import requests
import time

def githubOauth(GitHubClientID, GitHubClientSecret, githubProxies, timeout):
    print("################################ GitHub 授权 ################################")
    input("按回车开始进行GitHub账号授权，注意如果账号Organization中的仓库也需要同步，那么您点击Authorize绿色按钮前需要点击Organization access部分对应组织的Grant按钮：")

    # ######################################## 获取GitHub用户的 access_token ########################################
    # Api文档：
    # https://docs.github.com/cn/developers/apps/building-oauth-apps/authorizing-oauth-apps
    # https://docs.github.com/cn/developers/apps/building-oauth-apps/scopes-for-oauth-apps
    # 认证地址
    oauth_url = 'https://github.com/login/oauth/authorize?client_id={ClientID}&redirect_uri={redirect_uri}&response_type=code&scope=user repo' \
        .format(ClientID=GitHubClientID, redirect_uri='https://www.only4.work/appHelper/github_show_code_param.php')

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
            r = requests.post('https://github.com/login/oauth/access_token', headers = {
                'Accept': 'application/json'
            }, params = {
                "code": code,
                "client_id": GitHubClientID,
                "redirect_uri": "https://www.only4.work/appHelper/github_show_code_param.php",
                "client_secret": GitHubClientSecret,
            }, proxies = githubProxies, timeout = timeout)
            break
        except Exception as err:
            print(err)
            print("出错啦，正在重试，还剩{}次机会".format(tryTime))
            time.sleep(1)
            continue

    print("[info] GitHub账号授权完成")

    # print(r.text)
    access_token = r.json()['access_token']
    print("您的access_token为：" + access_token)
    # {"access_token":"ghu_NgIJEFtrQz4FtTqfewVaHlR9Xnb30R26oMwM","expires_in":28800,"refresh_token":"ghr_mu8iw6A33ae1AoIo3hMFVX7VssbPmGIlfSKyc2CTQIPootRSMnr48c3WVevQpYfwLL9MaQ0vWvTR","refresh_token_expires_in":15897600,"token_type":"bearer","scope":""}

    # ######################################## 获得用户仓库信息 ########################################
    tryTime = 10
    while(tryTime > 0):
        tryTime = tryTime - 1
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
        except Exception as err:
            print(err)
            print("出错啦，正在重试，还剩{}次机会".format(tryTime))
            time.sleep(1)
            continue

    # print(r.text)
    print()
    print("################################ 成功获取到您的仓库信息 ################################")
    githubRepos = {}
    for repo in r.json():
        print(repo['full_name'])
        print(repo['html_url'])
        # githubRepos.append()
        githubRepos[repo['full_name']] = {
            # 'human_name': repo['human_name'],
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
        print()
    print("[info] GitHub仓库读取完成")
    return [r.json(), githubRepos]
