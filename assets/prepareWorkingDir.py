import os;
import shutil;

def prepareWorkingDir(CurrentDir, WorkingDir):
    """
    准备工作目录
    """
    print("################################ 正在准备工作目录 ################################")
    print()
    print("当前目录", CurrentDir) # 获取当前文件所在目录
    print("工作目录", WorkingDir)
    # print(os.getcwd()) # 获取当前脚本运行目录

    if os.path.exists(os.path.abspath(CurrentDir + "/.git")):
        print("\033[1;37;41m[error] 请不要在Git仓库中运行本程序，否则会导致Git仓库嵌套，当前仓库代码会覆盖您的仓库！\033[0m")
        print("[error] 继续操作前请删除当前目录下的 .git 隐藏文件夹", os.path.abspath(CurrentDir + "/.git"))
        print()
        print("您可使用以下命令进行删除：")
        print("Linux系统")
        print('rm -rf "{}"'.format(os.path.abspath(CurrentDir + "/.git")))
        print("Windows系统")
        print('rd /s /q "{}"'.format(os.path.abspath(CurrentDir + "/.git")))
        print("\033[1;37;41m以上命令为强制删除命令，请再三确认无误后再进行操作！\033[0m")
        exit()

    if os.path.exists(WorkingDir):
        pass
        # # 工作目录已存在，如果非空就创建
        # if not os.listdir(WorkingDir):
        #     print("工作目录已存在且为空，无需创建")
        # else:
        #     # print('工作目录已存在且非空，请检查是否有其他程序正在使用，如果确认无其他程序在使用，请手动删除工作目录，然后重试！')
        #     # print()
        #     # print("是否删除工作目录中的文件? (Y: 删除, N: 不删除)")
        #     # userInput = ''
        #     # while userInput == '':
        #     #     userInput = input("\r>").strip().lower ()
        #     # if userInput in ['y', 'yes']:
        #     #     # os.rmdir(WorkingDir) # 只能删除空文件夹
        #     #     shutil.rmtree(WorkingDir)    #递归删除文件夹
        #     #     os.mkdir(WorkingDir)
        #     #     print("成功清空工作目录", WorkingDir)
        #     # else:
        #     #     input('按回车键退出...')
        #     #     exit()
        #     print()
        #     print('工作目录已存在且非空，是否在上次同步的基础上继续？')
        #     while True:
        #         userInput = input("y: 继续, n: 清空工作目录 (y): ").strip().lower ()
        #         if userInput in ['', 'y', 'yes']:
        #             break
        #         elif userInput in ['n', 'no']:
        #             # os.rmdir(WorkingDir) # 只能删除空文件夹
        #             shutil.rmtree(WorkingDir)    #递归删除文件夹
        #             os.mkdir(WorkingDir)
        #             print("成功清空工作目录", WorkingDir)
        #             break
        #         else:
        #             input('按回车键退出...')
        #             exit()
    else:
        # 工作目录不存在，创建该目录
        os.mkdir(WorkingDir)
        print("成功创建工作目录", WorkingDir)
    print("[info] 工作目录准备完成")


    # os.mkdir(WorkingDir)
    # os.makedirs(WorkingDir)

    # os.system("chdir")
    # print(__file__)