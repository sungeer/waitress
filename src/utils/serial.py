import json
import uuid
import datetime
import decimal


class JsonExtendEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        elif isinstance(obj, bytes):
            return obj.decode('utf-8')
        elif isinstance(obj, uuid.UUID):
            return str(obj)
        return super().default(obj)


# json to dict
def from_json(data):
    return json.loads(data)


# dict to json
def to_json(data):
    return json.dumps(data, cls=JsonExtendEncoder, ensure_ascii=False)
