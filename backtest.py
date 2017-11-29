import pandas as pd
from fbprophet import Prophet
import matplotlib.pyplot as plt

"""
Loading our daily history Silver price data
"""
df = pd.read_csv("XAGUSDHistoricalData.csv", index_col=False)
df.columns = ["ds", "y", "Open","High","Low","Change %"]
df['ds'] = pd.to_datetime(df['ds'])


def predict(month, df, units):
	print("------ Month " + str(month) + " ------")
	timefrom = '2017-' + str(month) + '-1'
	timeto = '2017-' + str(month + 1) + '-1'
	df=df[df['ds'] < timeto] #this the dataframe for our real values, we are taking for the month we are predicting also to compare later on

	m = Prophet(daily_seasonality=True)
	m.fit(df[df['ds'] <= timefrom]) #fit without knowing the month we want to predict
	future = m.make_future_dataframe(periods=30)
	forecast = m.predict(future) #predict periods=30 that is a month ahead

	plt.rcParams["figure.figsize"] = (20,10)
	dfResult = pd.DataFrame({'Timeline': df['ds'], 'Real':df['y'], 'Trend':forecast['trend'],
							 'Prediction':forecast['yhat'], 'Prediction Lower':forecast['yhat_lower'],
							 'Prediction Upper':forecast['yhat_upper']})

	"""
	We are plotting the predictions and saving to png in the results folder. You can check them out!
	"""
	dfResult = dfResult[dfResult['Timeline'] > timefrom] #show result for the month
	dfplot = dfResult.plot(x='Timeline')
	dfplot.get_figure().savefig('results/'+timefrom+'_to_'+timeto+'.png', dpi=90, bbox_inches='tight')


	prices = df[(df['ds'] > timefrom) & (df['ds'] < timeto)]
	prices = prices.sort_values('ds')


	currentPrice = prices['y'].iloc[0]
	target = currentPrice + (dfResult['Prediction'].iloc[-1] - dfResult['Prediction'].iloc[0]) #let's say we take a position on this

	"""
	Loading 
	Minute data from http://www.histdata.com/download-free-forex-historical-data/?/excel/1-minute-bar-quotes/XAGUSD
	"""
	hist = pd.read_excel("histdata/HISTDATA_COM_XLSX_XAGUSD_M12017"+'%0*d' % (2, month)+"/DAT_XLSX_XAGUSD_M1_2017"
						 +'%0*d' % (2, month)+".xlsx", usecols=[0, 1])
	hist.columns = ['date', 'price']
	hist['date'] = pd.to_datetime(hist['date'])
	hist = hist[(hist['date'] > timefrom) & (hist['date'] < timeto)]

	"""
	TODO: display the position we are taking on the plots
	"""
	print("Current Price: "+str(currentPrice) + " at "+str(prices['ds'].iloc[0]))
	print ( ("Short position: " if target<currentPrice else "Long position: ") + str(target))

	"""
	The simulation
	Going through minute data to see if are reaching our take profit value!
	We are closing our position regardless of loss if we are not reaching our take profit
	This is very risky in real situations, please put stop losses and use wise money management
	"""
	for row in hist.iterrows():
		if(target < currentPrice): #short
			if(row[1].price < target):
				print ("Short take profit at "+str(row[1].date)+", "+str(row[1].price))
				return abs(currentPrice-target)*units
		elif(row[1].price > target): #long
			print("Long take profit at " + str(row[1].date) + ", " + str(row[1].price))
			return abs(currentPrice - target) * units
	loss = abs(target-currentPrice)*units*-1
	print("Closing position: loss: "+str(loss)+ " at " + str(row[1].date))
	return loss

trades = []
account = 2500
for i in range(1,11):
	result = float(predict(i,df,100))
	trades.append(result)
	account = account + result
	if(account < 2000): #A Really bad of money management, put stop losses when taking positions if you want to try in a real
		print ("Too many losses.")
		break
print(trades)
print("Total profit: "+str(sum(trades)))
print("Final account: "+str(account))
print("% Growth: "+ str((account-2500)/2500*100))