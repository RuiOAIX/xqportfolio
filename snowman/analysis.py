"""
"""
import re
import json
import copy

from .headers import default_headers
from .urls import urls
from .session import Session

class Analysis(object):

    def __init__(self, symbol, session = None):
        self.symbol = symbol
        self.s = session if session else Session()
        self.benefit_origin = None
        self.benefit_simple = None
        self.max_draw_origin = None
        self.max_draw_simple = None
        self.turnover_origin = None
        self.turnover_simple = None
        self.liquidity_origin = None
        self.liquidity_simple = None
        self.volatility_origin = None
        self.volatility_simple = None
        self.top_stocks_origin = None
        self.top_stocks_simple = None

    def _update(self, _url, **kwargs):
        self.s.touch()
        resp = self.s.get(_url(self.symbol, **kwargs))
        try:
            data = json.loads(resp.text)
        except json.decoder.JSONDecodeError:
            raise Exception('Json loads error: {}'.format(resp.text[:50]))
        return data

    def benefit(self, origin = False, update = False):
        if update or self.benefit_origin is None:
            self.benefit_origin = self._update(urls.analysis_benefit)
            self.benefit_simple = None
        if origin:
            return self.benefit_origin
        if self.benefit_simple is None:
            self.benefit_simple = [(int(re.sub('-', '', month['date'])), month['value']) for month in self.benefit_origin[0]['profit_list']]
        return self.benefit_simple


    def max_draw(self, origin = False, update = False):
        if update or self.max_draw_origin is None:
            self.max_draw_origin = self._update(urls.analysis_max_draw)
            self.max_draw_simple = None
        if origin:
            return self.max_draw_origin
        if self.max_draw_simple is None:
            self.max_draw_simple = {}
            self.max_draw_simple['begin_date'] = self.max_draw_origin['begin_date']
            self.max_draw_simple['end_date'] = self.max_draw_origin['end_date']
            self.max_draw_simple['value'] = self.max_draw_origin['max_draw']
            return self.max_draw_simple
        return self.max_draw_simple

    def turnover(self, origin = False, update = False):
        if update or self.turnover_origin is None:
            self.turnover_origin = self._update(urls.analysis_turnover)
            self.turnover_simple = None
        if origin:
            return self.turnover_origin
        if self.turnover_simple is None:
            self.turnover_simple = self.turnover_origin['values'][0]['value']
        return self.turnover_simple

    def liquidity(self, origin = False, update = False):
        if update or self.liquidity_origin is None:
            self.liquidity_origin = self._update(urls.analysis_liquidity)
            self.liquidity_simple = None
        if origin:
            return self.liquidity_origin
        if self.liquidity_simple is None:
            self.liquidity_simple = self.liquidity_origin['values'][0]['value']
        return self.liquidity_simple

    def volatility(self, origin = False, update = False):
        if update or self.volatility_origin is None:
            self.volatility_origin = self._update(urls.analysis_volatility)
            self.volatility_simple = None
        if origin:
            return self.volatility_origin
        if self.volatility_simple is None:
            self.volatility_simple = self.volatility_origin['volatility_rate']
        return self.volatility_simple

    def top_stocks(self, page = 1, count = 5, origin = False, update = False):
        if update or self.top_stocks_origin is None:
            self.top_stocks_origin = self._update(urls.analysis_top_stocks, page = page, count = count)
            self.top_stocks_simple = None
        if origin:
            return self.top_stocks_origin
        if self.top_stocks_simple is None:
            self.top_stocks_simple = [{
                'symbol': st['stock_symbol'], 
                'name': st['stock_name'], 
                'benefit': st['stock_benefit'], 
                'holding_duration': st['holding_duration']} 
                                      for st in self.top_stocks_origin['stock_list']]
        return self.top_stocks_simple

    def all(self):
        return {'benefit': self.benefit(),
                'turnover': self.turnover(),
                'liquidity': self.liquidity(),
                'volatility': self.volatility(),
                'max_draw': self.max_draw(),
                'top_stocks': self.top_stocks(),
                }

