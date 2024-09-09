from AlgorithmImports import *
from QuantConnect import *
from QuantConnect.Data.Market import *
from QuantConnect.Indicators import *
from datetime import timedelta

class DancingBlackFalcon(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2016, 1, 1) # Set the start date
        self.SetEndDate(2020, 7, 1) # Set the end date
        self.SetCash(100000) # Set the starting cash balance
        self.SetWarmUp(30)
        
        # Addding stocks to our universe
        self.stocks = ["AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "BRK.B", "GOOG", "META", "UNH", "XOM", "JNJ", "TSLA", "JPM", "PG", "V", "LLY", "MA", "HD", "MRK", "CVX", "ABBV", "PEP", "AVGO", "KO", "COST"]
        for stock in self.stocks:
            self.AddEquity(stock, Resolution.Daily)
        
        # Defining the Bollinger Bands indicator for each stock using self.BB, assigning values to dictionary
        self.bands = {}
        for stock in self.stocks:
            bb = self.BB(stock, 20, 2, MovingAverageType.Simple, Resolution.Daily)
            self.bands[stock] = bb
            
        # Defining the MACD indicator for each stock using self.MACD, assigning values to dictionary
        self.macds = {}
        for stock in self.stocks:
            macd = self.MACD(stock, 12, 26, 9, MovingAverageType.Simple, Resolution.Daily)
            self.macds[stock] = macd
        
    def OnData(self, data):
        
        # Checking if the indicators are ready for all stocks. If any of the two indicators have missing values, return
        for stock in self.stocks:
            if not self.bands[stock].IsReady or not self.macds[stock].IsReady:
                return
        
        # Looping through all the stocks that are in our universe
        for stock in self.stocks:
            # Checking if we have any open positions
            holdings = self.Portfolio[stock].Quantity

            # Checking if the symbol is present in the data object. Same approach as for indicators.
            if stock not in data:
                return

            # Now, we want both indicators to be favorable. Only then we will execute a trade.
            # Checking if the price is above the upper band
            if data[stock].Close > self.bands[stock].MiddleBand.Current.Value:
                # If we don't have any open positions and the MACD is bullish, enter a long position
                if holdings <= 0 and self.macds[stock].Current.Value > 0:
                    self.SetHoldings(stock, 1.0/len(self.stocks))
                    self.Debug("BUY {0} >> {1}".format(stock, self.Time))
            # Checking if the price is below the lower band
            elif data[stock].Close < self.bands[stock].MiddleBand.Current.Value:
                # If we have an open long position and the MACD is bearish, close it
                if holdings > 0 and self.macds[stock].Current.Value < 0:
                    self.Liquidate(stock)
                    self.Debug("SELL {0} >> {1}".format(stock, self.Time))

