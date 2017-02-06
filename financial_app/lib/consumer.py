import json
from utils import RpcType
from yahoo_services import YahooFinance, YahooYql


class Consumer:
    def __init__(self, message):
        data = message[5:].split("=")
        if message.startswith("/YQL"):
            selects = data[0].split(',')
            mlist = data[1].split(',')
            self.args = {
                'select': selects,
                'filter': [('symbol', 'IN', mlist)]
            }
            self.mtype = RpcType.DAYS_RANGE
        else:
            selects = data[0].split(',')
            self.args = {
                'select': selects,
                'symbol': data[1]
            }
            self.mtype = RpcType.STOCK

    def run(self):
        if self.mtype == RpcType.DAYS_RANGE:
            self.obj = YahooYql()
        else:
            self.obj = YahooFinance()
        self.obj.set_query(self.args)
        self.response = self.obj.run()

    def get_message(self):
        data = json.loads(str(self.response))
        if 'message' in data:
            data = data['message']
        if self.mtype == RpcType.STOCK:
            if 'price' in data:
                return 'APPL (apple INC) quote is $' + data['price'] + ' per share'
        else:
            if 'DaysLow' in data and 'DaysHigh' in data:
                return 'APPL (apple INC) Days Low quote is $' + data['DaysLow'] + " and Days High quote is $" + data['DaysHigh'] + " "

        return "No enough arguments"
