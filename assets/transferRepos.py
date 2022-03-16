import os

def transferRepos(matchList, WorkingDir, fromRepoProtocol = 'https', toRepoProtocol = 'https'):
    # print(matchList)
    # 切换路径
    targetPath = os.path.abspath(WorkingDir)
    os.chdir(targetPath)
    if(os.path.abspath(os.getcwd()) != targetPath): # 展开为绝对路径，然后进行比较
        print("[error] 切换路径失败")
        print("当前路径", os.path.abspath(os.getcwd()))
        print("想要切换到的路径", targetPath)
        input("按回车键退出...")
        exit()

    commands = []
    commands.append("@echo off") # echo off
    # commands.append("cls") # 清屏
    # commands.append('')
    for repo in matchList:
        # 查看当前目录
        # commands.append('echo 当前目录')
        # commands.append('chdir')
        # 克隆仓库
        localRepoFolder = repo['from']['full_name'].split('/')[-1] + ".git"
        if not os.path.exists(WorkingDir + "/" + localRepoFolder):
            print(WorkingDir + "/" + localRepoFolder)
            repo_url = repo['from']['html_url']
            if toRepoProtocol != 'https':
                repo_url = repo['from']['ssh_url']
            # commands.append('echo 克隆仓库')
            commands.append("git clone --mirror {repo_url}".format(repo_url = repo_url))
        # 切换到仓库目录
        # commands.append('echo 切换到仓库目录')
        commands.append("cd {folder_name}".format(folder_name = localRepoFolder))
        # 更新本地仓库
        # 不可以使用 git fetch --all  如果仓库中有hidden ref，则推送时会报错
        # commands.append('echo 更新本地仓库')
        commands.append("git remote update")
        # 本地存储库GC （没有必要）
        # commands.append("git gc")
        # 同步仓库
        repo_url = repo['to']['html_url']
        if toRepoProtocol != 'https':
            repo_url = repo['to']['ssh_url']
        # commands.append('echo 推送仓库到远程（{repo_url}）'.format(repo_url = repo_url))
        commands.append("git push --mirror {repo_url}".format(repo_url = repo_url))
        # 切换回上一级目录
        # commands.append('echo 回到工作目录')
        commands.append("cd ../")
        # commands.append('echo 当前仓库克隆完成，等待用户确认，按任意键进行下一步操作 & pause')
        # commands.append("pause")
        # 空行
        commands.append('')
    commands.append('echo 命令执行完成')
    commands.append("pause")

    print("本项目还处于测试阶段，出于安全考虑，我们采用生成命令文件的方式对仓库进行操作，以免",
          "由于脚本错误造成数据丢失。我们强烈建议您在继续前先手动备份您的仓库，以免丢失代码。",
          "由于代码错误或您自己失误造成的代码仓库丢失，项目开发者不承担责任。在执行脚本前，请",
          "务必确认您知晓该行命令的执行结果，切勿盲目执行您不知道的命令！", sep = "\n")
    print("\033[1;37;41m继续前请务全量必备份仓库！\033[0m")
    print("\033[1;37;41m继续前请务全量必备份仓库！\033[0m")
    print("\033[1;37;41m继续前请务全量必备份仓库！\033[0m")
    print("继续操作代表您已阅读上述内容，程序将在工作目录下生成一个批处理脚本")
    if input("按<回车>键继续，或输入run直接执行(不推荐): ") == "run":
        for commandForExecute in commands:
            print("[正在执行]", commandForExecute)
            os.system(commandForExecute)
    else:
        commandTxtPath = os.path.abspath(WorkingDir + "/commands.bat")
        f=open(commandTxtPath, "w")
        f.write('\n'.join(commands))
        f.close()
        print("命令文件生成完毕，请查看：", commandTxtPath)

    # for command in commands:
    #     print(command)
    #     os.system(command)

    # :: 创建文件夹
    # mkdir D:\gitTransTempDir

    # :: 如果之前有没删除的话就删除
    # rd /s /q ./chrome-extension.git

    # rd /s /q D:\gitTransTempDir