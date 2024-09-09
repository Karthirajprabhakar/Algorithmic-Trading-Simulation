from AlgorithmImports import *
from QuantConnect import *
from QuantConnect.Data.Market import *
from QuantConnect.Indicators import *

from datetime import timedelta

class PensiveRedOrangeGoshawk(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2016, 1, 1) # Set the start date
        self.SetEndDate(2020, 7, 1) # Set the end date
        self.SetCash(100000) # Set the starting cash balance
        self.SetWarmUp(30)
        
        # Adding stocks to our universe
        self.stocks = ["AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "BRK.B", "GOOG", "META", "UNH", "XOM", "JNJ", "TSLA", "JPM", "PG", "V", "LLY", "MA", "HD", "MRK", "CVX", "ABBV", "PEP", "AVGO", "KO", "COST"]
        for stock in self.stocks:
            self.AddEquity(stock, Resolution.Daily)
        
        # Defining the Bollinger Bands for each stock in our universe using self.BB and assigning values to a dictionary
        self.bands = {}
        for stock in self.stocks:
            bb = self.BB(stock, 20, 2, MovingAverageType.Simple, Resolution.Daily)
            self.bands[stock] = bb
        
    def OnData(self, data):
        
        # Checking if the indicators are ready for all stocks. If some data points are missing, the code will not do anything and return
        for stock in self.stocks:
            if not self.bands[stock].IsReady:
                return
        
        # Looping through all the stocks that are in our universe
        for stock in self.stocks:
            # Checking if we have any open positions
            holdings = self.Portfolio[stock].Quantity

            # Checking if the symbol is present in the data object in case some data points are missing. Same approach as we took for indicators
            if stock not in data:
                return

            # Checking if the price is above the upper band. If it is above the upper band, that is a buy signal for us, assuming that we do not have any current holdings
            if data[stock].Close > self.bands[stock].MiddleBand.Current.Value:
                # If we don't have any open positions, enter a long position, weighting the portfolio equally
                if holdings <= 0:
                    self.SetHoldings(stock, 1.0/len(self.stocks))
                    self.Debug("BUY {0} >> {1}".format(stock, self.Time))
            # Checking if the price is below the lower band. If it is below the lower band, that signifies a downward trend, meaning a sell signal.
            elif data[stock].Close < self.bands[stock].MiddleBand.Current.Value:
                # If we have an open long position, close it
                if holdings > 0:
                    self.Liquidate(stock)
                    self.Debug("SELL {0} >> {1}".format(stock, self.Time))

