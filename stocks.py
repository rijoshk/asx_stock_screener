import requests
import pandas as pd
from yahoo_fin import stock_info as yf
from stockstats import StockDataFrame
from warnings import catch_warnings, simplefilter
from datetime import datetime, timedelta

colours = {
            "darkGreen": "00008000", 
            "green": "0000FF00", 
            "greenDark": "5cb800", 
            "lightRed": "00FF6600",
            "red": "00FF0000",
            "cyan": "00FFFF",
            "orange": "FFA500",
            "darkOrange": "FF8C00" 
           }

class StockHandler:

    def get_asx_stock_list(self, url):
        r = requests.get(url, allow_redirects=True)
        open('data/stocks.csv', 'wb').write(r.content)

    def format_collection(self):
        df = pd.read_csv('data/stocks.csv', 
                skiprows=[0,2],                 
                index_col=["asx_code", "company_name", "sector"],
                names=('company_name', 'asx_code', 'sector'))
        
        df.sort_values(by=['sector', 'asx_code'], inplace=True, ascending=True)
        df.to_csv('data/stocks.csv') 

class Stock:
    def __init__(self, stock):
        self.stock = stock
        self.price = 0.0
        self.rsi = 0.0   
        self.rsi_sign = ''
        self.macd = 0.0   
        self.signal = 0.0   
        self.hist = 0.0
        self.macd_sign = ''

    # returns all daily price information about the stock
    def getData(self, start_date, end_date):
        return yf.get_data(self.stock, start_date = start_date, end_date = end_date)    
    
    def getPrice(self):
        return yf.get_live_price(self.stock)    
    
    # set rsi_12 to false for rsi 6 day calculation, defaults to 12 day calculation
    def getRSI(self, n = 600, rsi_14 = True):
        # returns the current rsi indicator of the stock (uses the past 200 business days for calculation)
        with catch_warnings():
            # suppresses default warning from pandas
            simplefilter('ignore')
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days = n)
            stock_data = self.getData(start_date, end_date)
            if rsi_14:
                rsi = StockDataFrame(stock_data).get('rsi_14')[-1]
            else:
                rsi = StockDataFrame(stock_data).get('rsi_6')[-1]
        return rsi

    def getMACD(self, n = 300):
        # returns the current macd indicator of the stock (uses the past 300 business days for calculation)
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days = n)
        stock_data = self.getData(start_date, end_date)
        macd = StockDataFrame(stock_data).get('macd')[-1]
        return macd

    def getSignal(self, n = 300):
        # returns the current macd indicator of the stock (uses the past 300 business days for calculation)
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days = n)
        stock_data = self.getData(start_date, end_date)
        macds = StockDataFrame(stock_data).get('macds')[-1]
        return macds
    
class Screener:

    def __init__(self, stock):
        # self.manager = stock_manager
        self.stock = stock

    def getStockStats(self):
        # checks the indicators on all the stocks in the stockmanager object, and sends an email if any of them have changed.
        stock = self.stock

        self.stock.price = self.stock.getPrice()

        rsi = float(self.stock.getRSI())
        self.stock.rsi = rsi

        if rsi <= 30:
            self.stock.rsi_sign = colours["greenDark"]
        elif rsi <= 40 and rsi > 30:
            self.stock.rsi_sign = colours["green"]
        elif rsi >= 60 and rsi < 70:
            self.stock.rsi_sign = colours["lightRed"]
        elif rsi >= 70:
            self.stock.rsi_sign = colours["red"]

        macd = self.stock.getMACD()
        signal = self.stock.getSignal()
        hist = macd - signal

        if(macd < 0 and signal < 0):
            if hist <= 0:
                if hist <= 0 and hist >= -0.05:
                    self.stock.macd_sign = colours["green"]
            else:
                if hist >= 0 and hist >= 0.05:
                    self.stock.macd_sign = colours["greenDark"]
        elif(macd > 0 and signal > 0):   
            if hist >= 0:
                if hist >= 0 and hist <= 0.05:
                    self.stock.macd_sign = colours["orange"]
            else:
                if hist <= 0 and hist >= -0.05:
                    self.stock.macd_sign = colours["darkOrange"]
        
        self.stock.macd = macd
        self.stock.signal = signal 
        self.stock.hist = hist 

        return self.stock    