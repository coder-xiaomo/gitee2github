import copy

def repoMatching(repo1, repo2):
    # 对字典进行深拷贝
    repo1 = copy.deepcopy(repo1)
    repo2 = copy.deepcopy(repo2)

    # 配对字典
    matchList = {
        'match': [],
        'mismatch': {
            'repo1': [],
            'repo2': [],
        },
    }

    # 定义映射决策
    from .common import readJSON, fileExists
    if fileExists("mapping.json"):
        mapping = readJSON("mapping.json")
        orgNameMap = mapping.get('orgNameMap')
        repoNameMap = mapping.get('repoNameMap')
        fullNameMap = mapping.get('fullNameMap')
    else:
        mapping = None # 不需要映射
    def mapRepoName(fullName):
        if mapping == None:
            return fullName
        elif fullName in fullNameMap.keys():
            return fullNameMap.get(fullName)
        else:
            [orgName, repoName] = fullName.split('/')
            if orgName in orgNameMap.keys():
                orgName = orgNameMap.get(orgName)
            if repoName in repoNameMap.keys():
                repoName = repoNameMap.get(repoName)
            return orgName + "/" + repoName
    # # 测试
    # print(mapRepoName("only4/thisisarepo"))
    # print(mapRepoName("only-4/this-is-a-repo"))
    # print(mapRepoName("only4/this-is-a-repo"))
    # print(mapRepoName("only-4/thisisarepo"))
    # print(mapRepoName("only4/repo1"))
    # exit()

    # def judgeRepoEqual(name1, name2):
    #     if mapping == None: # 没有配置映射
    #         return name1 == name2
    #     else:
    #         for i in fullNameMap: # 比较 full_name 映射 比如 org1/repo1 -> org2/repo2
    #             if name1 == i[0]:
    #                 if name2 == i[1]:
    #                     return True # 如果 name1 和 name2 在 full_name 映射中，则匹配
    #                 else:
    #                     return False # 如果 name1 在 full_name 映射中，但是 name2 不在，则不匹配

    #         # 接下来同时比较 org repo 映射，将 org1 repo1进行映射，如果 name2 与 （name1+映射）相等，则匹配
    #         [org1, repo1] = name1.split('/')
    #         [org2, repo2] = name2.split('/')
    #         for i in orgNameMap: # 将 org1 进行映射    备注：如果不存在映射，则相当于始终没有进这个for循环中的if条件
    #             if org1 == i[0]:
    #                 org1 = i[1]
    #                 break
    #         if org1 != org2: # 如果 org1 和 org2 不相等，则一定不匹配
    #             return False

    #         # org1 与 org2 映射后相等，现在比较 repo1 和 repo2
    #         for i in repoNameMap: # 将 repo1 进行映射    备注：如果不存在映射，则相当于始终没有进这个for循环中的if条件
    #             if repo1 == i[0]:
    #                 repo1 = i[1]
    #                 break
    #         if org1 != org2: # 如果 org1 和 org2 不相等，则一定不匹配
    #             return False
    #         return True
    # # 测试
    # print(judgeRepoEqual("only4/thisisarepo", "only-4/this-is-a-repo")) # True
    # print(judgeRepoEqual("only4/thisisarepo", "only4/this-is-a-repo")) # False
    # print(judgeRepoEqual("only4/thisisarepo", "only-4/thisisarepo")) # True
    # print(judgeRepoEqual("only4/thisisarepo", "only4/thisisarepo")) # False
    # print(judgeRepoEqual("only4/repo1", "only5/repo2")) # True
    # exit()
    for repo1FullName in repo1.keys(): # 遍历repo1仓库名
        # print(repo1FullName)
        repo1FullName_map = mapRepoName(repo1FullName)
        if(repo1FullName_map in repo2.keys()): # 如果在repo2中，则说明匹配成功
            matchList.get('match').append({
                'from': repo1[repo1FullName],
                'to': repo2[repo1FullName_map],
            })
            del repo2[repo1FullName_map]
        else:
            matchList.get('mismatch')['repo1'].append(repo1[repo1FullName])

    matchList.get('mismatch')['repo2'] = list(repo2.values())
    return matchList

def printMatchintInfo(matchList, repo1Name = "repo1", repo2Name = "repo2"):
    print("################## 以下仓库不会同步 ################## ")
    print("{repo1Name} 有但是 {repo2Name} 没有的仓库".format(repo1Name = repo1Name, repo2Name = repo2Name))
    for i in matchList.get('mismatch').get('repo1'):
        print('    ' + i['html_url'])
    print()
    print("{repo2Name} 有但是 {repo1Name} 没有的仓库".format(repo1Name = repo1Name, repo2Name = repo2Name))
    for i in matchList.get('mismatch').get('repo2'):
        print('    ' + i['html_url'])
    print()
    print("################## 以下仓库会被同步 ################## ")
    print("{repo1Name} 与 {repo2Name} 匹配相同的仓库".format(repo1Name = repo1Name, repo2Name = repo2Name))
    for i in matchList.get('match'):
        print('    ' + i.get("from").get("full_name").ljust(30,' ') + " -> " + i.get("to").get("full_name"))
    print()
