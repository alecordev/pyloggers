# Logging Examples

## Simplest logger

```python
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s] - %(message)s', # optional
                    filename='filename.log') # optional
```

## Simple multiprocessing logger

```python
import os
import logging


logging.basicConfig(
    # stream=sys.stdout,
    filename=f"load_testing_amp-{os.getpid()}.log",  # each process in a pool must have its own
    level=logging.DEBUG,
    format="[%(asctime)s] - PID: %(process)d - TID: %(thread)d - %(levelname)s - %(message)s",
)
```

## Simple logger setup

```python
def setup_logger():
    """ Setups the logging functionality used throughout the execution. """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(asctime)s] - %(levelname)s - %(message)s')
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


logger = setup_logger()
```

## Changing a logger from another module

```python
from impala.dbapi import connect
logging.getLogger('impala.hiveserver2').setLevel(logging.INFO)
```

```python
requests.packages.urllib3.disable_warnings()
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
```

## dictConfig

```python
# https://docs.python.org/2/library/logging.config.html
# https://docs.python.org/3.6/library/logging.config.html

import logging
import logging.config
import datetime

DEFAULT_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': { 
        'standard': { 
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'complete': {
            'format': '%(asctime)s - PID: %(process)d - PNAME: %(processName)s' \
                      ' - TID: %(thread)d - TNAME: %(threadName)s' \
                      ' - %(levelname)s - %(filename)s - %(message)s',
        },
    },
    'handlers': { 
        'default': { 
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
        'file': { 
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.FileHandler',
            'filename': datetime.datetime.now().strftime('%Y%m%d.log'),
        },
        'rewrite': { 
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.FileHandler',
            'filename': datetime.datetime.now().strftime('%Y%m%d2.log'),
            'mode': 'w',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default', 'file', 'rewrite'],
            'level': 'INFO',
            'propagate': True
        },
        'another.module': {
            'level': 'DEBUG',
        },
    }
}

logging.config.dictConfig(DEFAULT_LOGGING)
logging.info('Example')
```

## Resources

- [Logging Docs](https://docs.python.org/3/library/logging.html)
- [Logging Official Cookbook](https://docs.python.org/3/howto/logging-cookbook.html)