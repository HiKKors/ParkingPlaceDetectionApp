import logging
from flask import has_request_context, request

class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
        else:
            record.url = None
            record.remote_addr = None
        return super().format(record)

logging.basicConfig(
    filename='ParkingCoreService/app/parking_core_logs.log',
    filemode='a',
    format='%(asctime)s,%(msecs)03d %(name)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO
)

handler = logging.StreamHandler()
# handler.setFormatter(formatter)

parking_logger = logging.getLogger('parking_core_logger')
parking_logger.setLevel(logging.INFO)
parking_logger.addHandler(handler)
