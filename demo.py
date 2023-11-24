import pandas as pd

data = pd.read_csv('BANKNIFTY-Year.csv')

data['Datetime'] = pd.to_datetime(data['Date'] + ' ' + data['Time'])
data = data.sort_values('Datetime')
data = data.set_index('Datetime')

capital = 1000000  # Starting capital (Assuming 1,000,000 INR)
stop_loss_pct = 0.005  # 0.5% stop loss
position = None
entry_price = 0
stop_loss = 0


trades = 0
win_trades = 0
loss_trades = 0
total_profit_loss = 0

for day, day_data in data.groupby(data.index.date):
    day_data = day_data.between_time('09:15', '15:30')

    if len(day_data) >= 15:
        high_15min = day_data['High'].iloc[:15].max()
        low_15min = day_data['Low'].iloc[:15].min()

        if position is None:
            if day_data['High'][15] >= high_15min:
                position = 'Buy'
                entry_price = high_15min
                stop_loss = entry_price * (1 - stop_loss_pct)
            elif day_data['Low'][15] <= low_15min:
                position = 'Sell'
                entry_price = low_15min
                stop_loss = entry_price * (1 + stop_loss_pct)

        if position == 'Buy' and day_data['Low'].min() <= stop_loss:
            total_profit_loss += stop_loss - entry_price
            loss_trades += 1
            trades += 1
            position = None

        elif position == 'Sell' and day_data['High'].max() >= stop_loss:
            total_profit_loss += entry_price - stop_loss
            loss_trades += 1
            trades += 1
            position = None

        elif position is not None and day_data.index[-1].time() >= pd.to_datetime('15:15').time():
            if position == 'Buy':
                total_profit_loss += day_data['Close'][-1] - entry_price
            else:
                total_profit_loss += entry_price - day_data['Close'][-1]
            trades += 1
            win_trades += 1
            position = None

# Calculate final P&L
if total_profit_loss < capital:
    print("Loss In Trade")
else:
    print("Profit In Trade")

final_capital = capital + total_profit_loss

print(f"Total Trades: {trades}")
print(f"Winning Trades: {win_trades}")
print(f"Losing Trades: {loss_trades}")
print(f"Total P&L: {total_profit_loss:.2f} INR")
print(f"Final Capital: {final_capital:.2f} INR")
