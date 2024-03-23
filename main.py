import math

import pandas as pd
import matplotlib.pyplot as plt

# Wczytanie danych z pliku CSV
data = pd.read_csv('0o77_uk_d.csv')

data_closed = data['Zamkniecie']


def ema(days=12, day_start=0, data_c=data_closed):

    alpha = 2.0 / (days + 1)
    numerator = 0
    denominator = 0
    if(days+day_start >= len(data_c)):
        days = len(data_c)-day_start
    for i in range(days):
        numerator += data_c[len(data_c) - (i+1) - day_start] * (1.0 - alpha) ** i
        denominator += (1.0 - alpha) ** i
    return numerator / denominator


def macd_eq(data_input, array,a=12,b=26):
    if a != b:
        for i in range(len(data_input)):
            array.append(ema(a, i) - ema(b, i))
    else:
        for i in range(len(data_input)):
            array.append(ema(a, i, data_input))


macd = []
macd_eq(data_closed, macd)
signal = []
macd_eq(macd, signal, 9, 9)

signal = signal[::-1]

def buy_shares(shares, funds, share_price):
    temp_shares = math.floor(funds/share_price)
    temp_funds = temp_shares*share_price
    funds-=temp_funds
    shares += temp_shares
    return shares, funds,temp_funds


def sell_shares(shares,funds,share_price):
    temp_funds = shares*share_price
    funds+=temp_funds
    shares = 0
    return shares, funds, temp_funds


def macd_analysis(pointS, pointB,a_shares,a_funds,t_value,data, transactions):
    for i in range(len(macd) - 1):
        if macd[i] > signal[i] and macd[i + 1] < signal[i + 1]:
            pointS.append(i)
            a_shares, a_funds, t_value = sell_shares(a_shares, a_funds,data['Zamkniecie'][i])
            transactions.append([data['Data'][i], "Sell", data['Zamkniecie'][i], t_value, a_funds, a_shares])

        elif macd[i] < signal[i] and macd[i + 1] > signal[i + 1]:
            a_shares, a_funds, t_value = buy_shares(a_shares, a_funds,data['Zamkniecie'][i])
            transactions.append([data['Data'][i], "Buy", data['Zamkniecie'][i], t_value, a_funds, a_shares])
            pointB.append(i)
    a_shares, a_funds, t_value = sell_shares(a_shares, a_funds,data['Zamkniecie'][len(data) - 1])
    transactions.append([data['Data'][len(data) - 1], "Sell", data['Zamkniecie'][len(data) - 1], t_value, a_funds,a_shares])
    return a_shares, a_funds, t_value

# Wykres 1: Notowania analizowanego instrumentu finansowego
plt.figure(figsize=(12, 6))
plt.plot(data['Data'], data['Zamkniecie'], label='Zamkniecie')
plt.title('Notowania analizowanego instrumentu finansowego')
plt.xlabel('Data')
plt.ylabel('Cena Zamknięcia')
plt.legend()
# plt.xticks(rotation=45)
plt.grid(True)
plt.show()


#Wykres 2: MASD+SIGNAL

plt.figure(figsize=(12, 6),facecolor='lightgrey')
plt.plot(data['Data'], macd, label='MACD Line', color='blue')
plt.plot(data['Data'], signal, label='Signal Line', color='red')
plt.title('MACD + SIGNAL')
plt.xlabel('Data')
plt.ylabel('Wartość')
plt.legend()
# Dodanie punktów kupna/sprzedaży
pointsBuy =[]
pointsSell =[]
#Rownolegle z dodaniem punktów kupjemy/spzedajemy
available_shares=1000
available_funds=0
transaction_value=0
transaction=[]
#for i in range(len(macd)-1):
#    if macd[i] > signal[i] and macd[i+1] < signal[i+1]:
#        pointsSell.append(i)
#        available_shares,available_funds,transaction_value=sell_shares(available_shares,available_funds,data['Zamkniecie'][i])
#        transaction.append([data['Data'][i], "Sell",data['Zamkniecie'][i], transaction_value,available_funds,available_shares])
#
#    elif macd[i] < signal[i] and macd[i+1] > signal[i+1]:
#        available_shares, available_funds,transaction_value = buy_shares(available_shares, available_funds, data['Zamkniecie'][i])
#        transaction.append([data['Data'][i], "Buy",data['Zamkniecie'][i], transaction_value,available_funds,available_shares])
#        pointsBuy.append(i)
#
#available_shares,available_funds,transaction_value=sell_shares(available_shares,available_funds,data['Zamkniecie'][len(data)-1])
#transaction.append([data['Data'][len(data)-1], "Sell",data['Zamkniecie'][len(data)-1], transaction_value,available_funds,available_shares])
available_shares,available_funds,transaction_value=macd_analysis(pointS=pointsSell,pointB=pointsBuy,
                                                                 a_shares=available_shares,a_funds=available_funds,
                                                                 t_value=transaction_value,data=data,
                                                                 transactions=transaction)
print("Dostepne akcje: "+str(available_shares))
print("Dostepne sriodki: "+str(available_funds))
print(transaction)

def show_buy_sell_points(origin_array, points_array, line_array, buy):
    if buy:
        for i in points_array:
            plt.scatter(origin_array[i], line_array[i], marker='^', color='g', label='Kupno', s=100)
    else:
        for i in points_array:
            plt.scatter(origin_array[i], line_array[i], marker='v', color='r', label='Sprzedaż', s=100)


show_buy_sell_points(data['Data'],pointsBuy,macd,True)
show_buy_sell_points(data['Data'],pointsSell,signal,False)
plt.show()


# Wykres 3
plt.figure(figsize=(12, 6))
plt.plot(data['Data'], data['Zamkniecie'], label='Zamkniecie')
plt.title('Tranzakcje kupna/sprzedaży')
plt.xlabel('Data')
plt.ylabel('Cena Zamknięcia')
plt.legend()
show_buy_sell_points(data['Data'],pointsBuy,data['Zamkniecie'],True)
show_buy_sell_points(data['Data'],pointsSell,data['Zamkniecie'],False)
plt.show()


profits_losses = []

for i in range(1, len(transaction)):
    if transaction[i][1] == "Sell":
        buy_transaction_value=0
        buy_price = 0
        shares_q=0
        for j in range(i-1, -1, -1):
            if transaction[j][1] == "Buy":
                buy_price = transaction[j][2]
                buy_transaction_value=transaction[j][3]
                shares_q=transaction[j][5]
                break
        if buy_price > 0:
            sell_price = transaction[i][2]
            transaction_value = transaction[i][3]
            #profit_loss = (sell_price - buy_price) * shares_q
            profit_loss=transaction_value-buy_transaction_value
            profits_losses.append([profit_loss, transaction[i][0]])

print("Liczba zyskownych transakcji:", len([pl for pl in profits_losses if pl[0] > 0]))
print("Liczba stratnych transakcji:", len([pl for pl in profits_losses if pl[0] < 0]))
print("Łączny zysk:", sum([pl[0] for pl in profits_losses if pl[0] > 0]))
print("Łączna strata:", sum([pl[0] for pl in profits_losses if pl[0]< 0]))

print("Transakcje zyskowne: ")
for pl in profits_losses:
    if pl[0]>0:
        print(pl)

print("Transakcje stratne: ")
for pl in profits_losses:
    if pl[0]<0:
        print(pl)




