import os
import logging
from logging import StreamHandler

class FilepathLogHandler(StreamHandler):
    """
    自定义日志处理器，增加文件路径信息。
    将日志的文件路径（绝对路径）加入到日志记录中，增强日志的可追踪性。
    """

    def format(self, record):
        """
        格式化日志记录，添加文件的绝对路径信息。

        :param record: 日志记录对象
        :return: 格式化后的日志消息字符串
        """
        # 获取并添加绝对文件路径到日志记录中
        record.filepath = os.path.abspath(record.pathname)
        # 调用父类的 format 方法获取基础格式化信息
        message = super().format(record)
        # 返回带有文件路径信息的格式化日志
        return f"[{record.filepath}]\n{message}"

def setup_logger(name):
    """
    设置自定义 Logger，使用自定义的 FilepathLogHandler 处理器，输出包含文件路径的日志。

    :param name: Logger 的名称
    :return: 配置完成的 Logger 对象
    """
    # 获取 Logger 对象
    logger = logging.getLogger(name)

    # 如果 Logger 没有设置处理器，则进行配置
    if not logger.hasHandlers():
        logger.setLevel(logging.DEBUG)  # 设置日志级别为 DEBUG

        # 创建并设置自定义处理器
        handler = FilepathLogHandler()
        # 定义日志输出格式，包含时间、级别、文件路径、行号等信息
        formatter = logging.Formatter(fmt='\n-----开始-----\n%(asctime)s\n%(levelname)-8s\n[%(filepath)s:%(lineno)d]\n%(message)s\n-----结束-----\n\n')
        handler.setFormatter(formatter)

        # 确保处理器未重复添加到 Logger 中
        if handler not in logger.handlers:
            logger.addHandler(handler)
    
    return logger

# 使用自定义 Logger
logger = setup_logger(__name__)

# # 测试日志打印
# def test_logging():
#     logger.info("这是一个信息日志。")
#     logger.error("这是一个错误日志。")

# test_logging()
