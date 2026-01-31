import logging


logger = logging.getLogger(__name__)

streamH = logging.StreamHandler()
fileH = logging.FileHandler("tracking.log")


logger.setLevel(logging.DEBUG)
streamH.setLevel(logging.INFO)
fileH.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s: %(name)s: %(levelname)s:  %(message)s")

streamH.setFormatter(formatter)
fileH.setFormatter(formatter)

if not logger.hasHandlers():
    logger.addHandler(streamH)
    logger.addHandler(fileH)

logger.info("Logger started!")
