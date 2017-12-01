"""
Logging service that receives logging messages from any Python that setups logging like:

    def init_logging():
        import logging
        import logging.handlers

        root_logger = logging.getLogger('')
        root_logger.setLevel(logging.DEBUG)
        socket_handler = logging.handlers.SocketHandler('localhost', 15680)
        root_logger.addHandler(socket_handler)

    init_logging()
"""

import os
# import sys
import time
import pickle
import logging
import logging.handlers
import logging.config
import socketserver
import struct
# import datetime


class LogRecordStreamHandler(socketserver.StreamRequestHandler):
    """Handler for a streaming logging request.

    This basically logs the record using whatever logging policy is
    configured locally.
    """

    def handle(self):
        """
        Handle multiple requests - each expected to be a 4-byte length,
        followed by the LogRecord in pickle format. Logs the record
        according to whatever policy is configured locally.
        """
        while 1:
            try:
                chunk = self.connection.recv(4)
                if len(chunk) < 4:
                    break
                slen = struct.unpack('>L', chunk)[0]
                chunk = self.connection.recv(slen)
                while len(chunk) < slen:
                    chunk = chunk + self.connection.recv(slen - len(chunk))
                obj = self.unPickle(chunk)
                record = logging.makeLogRecord(obj)
                self.handleLogRecord(record)
                time.sleep(0.0001)
            except Exception as e:
                time.sleep(0.0001)

    def unPickle(self, data):
        return pickle.loads(data)

    def handleLogRecord(self, record):
        if self.server.logname is not None:
            name = self.server.logname
        else:
            name = record.name
        logger = logging.getLogger(name)
        logger.handle(record)


class LogRecordSocketReceiver(socketserver.ThreadingTCPServer):
    """
    Simple TCP socket-based logging receiver suitable for testing.
    """

    allow_reuse_address = True

    def __init__(self,
                 host='localhost',
                 port=404,
                 handler=LogRecordStreamHandler):
        socketserver.ThreadingTCPServer.__init__(self, (host, port), handler)
        self.abort = 0
        self.timeout = 1
        self.logname = None

    def serve_until_stopped(self):
        import select
        abort = 0
        while not abort:
            rd, wr, ex = select.select([self.socket.fileno()],
                                       [], [],
                                       self.timeout)
            if rd:
                self.handle_request()
            abort = self.abort
            time.sleep(0.0001)


def main():
    log_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': '%(asctime)s %(levelname)s %(name)s %(message)s',
            },
            'detailed': {
                'format': ('[%(asctime)s] - %(levelname)s - [%(filename)s:%(funcName)s:%(lineno)d]'
                           ' - [%(process)d:%(processName)s | %(thread)d:%(threadName)s] - %(message)s'),
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'detailed',
                'level': 'INFO'
            },
            'logfile': {
                'level': 'INFO',
                'class': 'logging.FileHandler',
                'formatter': 'detailed',
                # .format(datetime.datetime.now().strftime('%Y-%m-%d')),
                'filename': 'Service.log',
                'mode': 'w'
            },
            'debuglogfile': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'detailed',
                # .format(datetime.datetime.now().strftime('%Y-%m-%d')),
                'filename': 'Service-DEBUG.log',
                'mode': 'a',
                'maxBytes': 100 * 1024 * 1024,
                'backupCount': 5,
            },
        },
        'loggers': {
            '': {
                'handlers': ['debuglogfile', 'console', 'logfile'],
                'level': 'DEBUG'
            },
        }
    }
    logging.config.dictConfig(log_config)
    tcp_server = LogRecordSocketReceiver()
    tcp_server.serve_until_stopped()


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()
