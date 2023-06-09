import logging

# 配置日志记录器
logging.basicConfig(level=logging.DEBUG,  # 设置日志级别为DEBUG
                    format='%(asctime)s [%(levelname)s] %(message)s',  # 设置日志格式
                    datefmt='%Y-%m-%d %H:%M:%S')  # 设置日期格式

def logprint(message, level="info"):
    """
    打印日志信息
    :param message: 日志信息内容
    :param level: 日志级别 ("debug", "info", "warning", "error", "critical")
    """
    if level.lower() == "debug":
        logging.debug(message)
    elif level.lower() == "info":
        logging.info(message)
    elif level.lower() == "warning":
        logging.warning(message)
    elif level.lower() == "error":
        logging.error(message)
    elif level.lower() == "critical":
        logging.critical(message)
    else:
        logging.info(message)
