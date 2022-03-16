import configparser

def readConfigFile(configFilePath):
    # 可以不考虑配置文件不存在的情况

    #  实例化configParser对象
    config = configparser.ConfigParser()
    # -read读取ini文件
    config.read(configFilePath, encoding='UTF-8') # GB18030
    # -sections得到所有的section，并以列表的形式返回
    # configSections = config.sections()
    return config
    print("[info] 配置文件读取完成")