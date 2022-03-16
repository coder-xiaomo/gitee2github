import signal

def defineWorkingDirCleanFunction(saveJSONFunction):
    """
    定义Ctrl+C退出时 工作目录清理函数
    """
    def cleanWhenExit(signum, frame):
        print()
        print('程序正在清理工作目录，准备退出...')
        os.rmdir(WorkingDir)
        print('完成！')
        print()
        for countdown in range(3, 0, -1):
            print('\r' + "{} 秒后退出{}".format(countdown, '.' * (4 - countdown)), end='')
            time.sleep(1)
        exit()
    # 注册信号处理函数
    signal.signal(signal.SIGINT, cleanWhenExit)
    signal.signal(signal.SIGTERM, cleanWhenExit)
    print("[info] 工作目录清理函数准备完成")