import logging
import sys
from typing import Dict, List

def config_logging(file_name: str, console_level: int=logging.INFO, file_level: int=logging.DEBUG):
    old_factory = logging.getLogRecordFactory()

    levelname_trans = {
            "DEBUG": "DBG",
            "INFO": "INF",
            "WARNING": "WAR",
            "CRITICAL": "ERR"
        }
    
    def new_factory(name, level, fn, lno, msg, args, exc_info, func=None, sinfo=None, **kwargs)->logging.LogRecord:
        record = old_factory(name, level, fn, lno, msg, args, exc_info, func, sinfo, **kwargs)
        if record.levelname in levelname_trans:
            record.shortlevelname = levelname_trans[record.levelname]
        else:
            record.shortlevelname = (record.levelname.upper() + "UNK")[:3]
        return record

    logging.setLogRecordFactory(new_factory)
    
    file_handler = logging.FileHandler(file_name, mode='a', encoding="utf8")
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s [%(shortlevelname)s] %(module)s.%(lineno)d %(name)s:\t%(message)s'
        ))
    file_handler.setLevel(file_level)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(
        '[%(asctime)s %(shortlevelname)s] %(message)s',
        datefmt="%Y/%m/%d %H:%M:%S"
        ))
    console_handler.setLevel(console_level)

    logging.basicConfig(
        level=min(console_level, file_level),
        handlers=[file_handler, console_handler],
        )


def print_const_configs():
    import config as _cfg

    logger = logging.getLogger(__name__)

    def dfs_print_config(prefix: List[str], d: dict):
        for k, v in d.items():
            if not isinstance(k, str) or not k.isupper():
                continue
            
            keylist = prefix + [k]
            key = '.'.join(keylist)
            
            if isinstance(v, int) or isinstance(v, float) or isinstance(v, bool):
                logger.info(f"{key}={v}")
                continue

            if isinstance(v, str):
                logger.info(f'{key}="{v}"')
                continue

            if isinstance(v, dict):
                dfs_print_config(keylist, v)
                continue

    dfs_print_config([], _cfg.__dict__)


if __name__ == '__main__':
    config_logging("test.log", logging.WARNING, logging.DEBUG)
    logging.debug("debug")
    logging.info("info")
    logging.warning("warning")
    logging.critical("critical")

    logger = logging.getLogger(__name__)
    logger.debug("debug")
    logger.info("info")
    logger.warning("warning")
    logger.critical("critical")
