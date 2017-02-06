import urllib2
import urllib
import xmltodict
import json
from utils import Error, Response
import traceback


class YahooYql:
    '''
        Class to execute the yahoo yql query webservice
    '''

    def __init__(self, version="v1"):
        self.url = "http://query.yahooapis.com/" + version + "/public/yql"

        self.q = None
        self.format = None
        self.callback = None
        self.crossProduct = None
        self.diagnostics = None
        self.debug = None
        self.env = "store://datatables.org/alltableswithkeys"
        self.jsonCompat = None

        self.select_t = "*"
        self.from_t = "yahoo.finance.quotes"
        self.filter_t = ""


    def select_r(self, fields):
        '''
            Edit the fields to retrieve in the Yql Query
            params:
                fields - list of strings with the fields to be retrieved
        '''
        response = ''
        for i, param in enumerate(fields):
            if i == 0:
                response = param
            else:
                response += ', ' + param
        self.select_t = response

    def from_r(self, from_t):
        '''
            Edit the table to get the data from
            params:
                from_t: string with the name of the table to extract the data
        '''
        self.from_t = from_t

    def add_filter(self, field, condition, data):
        '''
            Add a filter to the query
            params:
                field - string with the name of the field to query
                condition - string with the conditional
                data - the value or values to compare. It can be a string or a list.
        '''
        statement = ""
        if condition == "IN" and isinstance(data, list):
            params = ", ".join(map(lambda y: '"' + y + '"' if isinstance(y, unicode) or isinstance(y, str) else y, data))
            statement = field + " " + condition + " " + "(" + params + ")"
        elif condition == "=":
            if isinstance(data, unicode) or isinstance(y, str):
                param = '"' + data + '"'
            statement = field + " " + condition + " " + param
        if self.filter_t:
            statement = " AND " + statement
        self.filter_t += statement

    def get_statement(self):
        statement = "SELECT " + self.select_t + " FROM " + self.from_t + " WHERE " + self.filter_t
        return statement

    def set_query(self, data):
        '''
            Set the parameters of the instance according to the values sent in the data. 
            params:
                data - dictionary where the key can be: select, from, filter. 
                    select key - value(s) must be a list
                    from key - valu must be a string
                    filter key - values must be a tuple of 3 elements (field, condition, value)
        '''
        if 'select' in data:
            self.select_r(data['select'])
        if 'from' in data:
            self.from_r(data['from'])
        if 'filter' in data:
            for (field, cond, values) in data['filter']:
                self.add_filter(field, cond, values)

    def run(self):
        '''
            Executes the yahoo yql query and returns the response of it
        '''
        try:
            response = {}
            statement = self.get_statement()
            if statement:
                response['q'] = statement
            if self.format:
                response['format'] = self.format
            if self.callback:
                response['callback'] = self.callback
            if self.crossProduct:
                response['crossProduct'] = self.crossProduct
            if self.diagnostics:
                response['diagnostics'] = self.diagnostics
            if self.debug:
                response['debug'] = self.debug
            if self.env:
                response['env'] = self.env
            if self.jsonCompat:
                response['jsonCompat'] = self.jsonCompat

            uri = urllib.urlencode(response)

            file = urllib2.urlopen(self.url + "?" + uri)
            data = file.read()
            file.close()

            tree = xmltodict.parse(data)
            data = tree['query']['results']['quote']
            return Response(data)
        except urllib2.HTTPError:
            # traceback.print_exc()
            return Error("There was an error in the request")
        except:
            # traceback.print_exc()
            return Error("General Error")


class YahooFinance:
    '''
        Class to execute the yahoo finance webservice
    '''

    def __init__(self, version="v1"):
        self.url = "http://finance.yahoo.com/webservice/" + version + "/symbols"
        self.user_agent = 'Mozilla/5.0 (Linux; Android 6.0.1; MotoG3 Build/MPI24.107-55) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.81 Mobile Safari/537.36' 

        self.symbol = "AAPL"
        self.filters = []

    def set_query(self, data):
        '''
            Set the parameters of the instance according to the values sent in the data. 
            params:
                data - dictionary where the key can be: select, symbol
                    select key - value(s) must be a list
                    symbol key - value must be a string. If more than one symbol is required, use the 
                                 string format like "AAPL,GOOGL"
        '''
        if 'select' in data:
            if isinstance(data['select'], list):
                self.filters = data['select']
            else:
                self.filters = [data['select']]
        if 'symbol' in data:
            self.symbol = data['symbol']

    def run(self):
        '''
            Executes the yahoo finance webservice and return the response of it
        '''
        req = urllib2.Request(self.url + "/" + self.symbol + '/quote', headers={'User-Agent': self.user_agent})
        data = urllib2.urlopen(req).read()

        tree = xmltodict.parse(data)
        fields = tree['list']['resources']['resource']['field']

        response = {}
        for my_dict in fields:
            for v in self.filters:
                if my_dict['@name'] == v:
                    response[v] = my_dict['#text']

        return Response(response)
