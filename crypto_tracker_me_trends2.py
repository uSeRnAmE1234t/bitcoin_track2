import requests
import time
from datetime import datetime 


import requests

def get_bitcoin_price():
    """Fetch the latest Bitcoin price from Binance API."""
    url = "https://api.binance.us/api/v3/ticker/price"
    params = {"symbol": "BTCUSDT"}
    
    try:
        # Send the request to the API
        response = requests.get(url, params=params)
        
        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            
            # Print the response data for debugging purposes
            print("Response data:", data)
            
            # Check if 'price' key exists in the response data
            if 'price' in data:
                price = float(data['price'])  # Convert price to float for comparison
                return price
            else:
                print("Error: 'price' key not found in the response data.")
                return None
        else:
            print(f"Error: Failed to fetch data, status code {response.status_code}")
            return None
    
    except Exception as e:
        print(f"Error occurred: {e}")
        return None


def update_wallet(wallet, percentage_change, buy, sell, keep, leave, smallDecrease):
    """
    Update the wallet based on the percentage change of Bitcoin price.
    Deduct 0.1% transaction fee only for 'buy' or 'sell'.
    """
    if sell or smallDecrease:
        percentage_change = -percentage_change

    if buy:
        new_wallet = wallet
    else:
        wallet_change = (wallet * percentage_change) / 100
        new_wallet = wallet + wallet_change

    if buy or sell:
        transaction_fee = wallet * 0.001  # 0.1% transaction fee
        new_wallet -= transaction_fee
        print(f"ITF")
   
    return new_wallet

if __name__ == "__main__":
    price_history = []
    track = [] #store the decisions made
    max_history = 7
    max_track = 7
    wallet = 1000  # Starting wallet balance
    investment = 0
    sellAfterDecrease = 1
    buyAfterIncrease = 1.5
    ld_count = 0
    li_count = 0
    
    isMine = False  # Boolean to track if Bitcoin is owned
    isIncreasing = False # Boolean to track if Bitcoin is increasing 
    isDecreasing = False # Boolean to track if Bitcoin is increasing 
    first_run = True  # To track if it's the first price fetch
    sell = False
    leave = False
    buy = False
    keep = False
    smallDecrease = False
    leaveIncrease = False
    leaveDecrease = False
    increaseForU = 250
    decreaseForU = 250


    print(f"Initial wallet balance: ${wallet}")

    while True:
        current_time = datetime.now()
        timestamp = current_time.strftime("%H:%M:%S")
        print("Timestamp:", timestamp)
        new_price = get_bitcoin_price()
        print(f"Bitcoin price: ${new_price}")
        

        # Keep history of prices, removing the oldest if over the limit
        if len(price_history) >= max_history:
            price_history.pop(0)
        price_history.append(new_price)
        #keep track of decisins and prices for a 7 decisons at a time 
        print("Len", len(track))
        if len(track) >= max_track:
            track.pop(0)
        print("Len", len(track))

        if first_run:  # On the first run, analyse market for a good buy time
            isMine = False
            print("finding the best time to enter")
            track.append("fbte")
            first_run = False
        else:
            #works out the chnage in price and converts it into percentage
            last_price = price_history[-2]
            price_change = new_price - last_price
            print(f"Price change ", price_change)
            percentage_change = abs((new_price - last_price) / last_price) * 100
            rounded_percentage_change = round(percentage_change, 2)
            # Track increases and decreases
            if price_change > 0:
                isIncreasing = True
                isDecreasing = False
                #used for comparison
                investment_change = (investment * percentage_change) / 100
                investment = investment + investment_change
            if price_change < 0:
                isDecreasing = True
                isIncreasing = False
                #used for comparioson
                investment_change = (investment * percentage_change) / 100
                investment = investment - investment_change

        # if i own bitcoin:
        if isMine: 
            if isIncreasing:
                # don't do anything
                keep = True
                track.append(("ki", percentage_change, new_price))
                print(f"keep: INcreased by {percentage_change:.2f}%")
                wallet = update_wallet(wallet, percentage_change, buy, sell, keep, leave, smallDecrease)
                print(f"Wallet increase after keep: {wallet:.2f}")
                keep = False
                isIncreasing = False

            elif isDecreasing:
                # depends by how much: if it's immediate over chosen sellAfterDecrease% OR accumulated sellAfterDecrease%, sell
                if percentage_change >= sellAfterDecrease:
                    keep = False
                    sell = True
                    isMine = False
                    track.append(("s", percentage_change))
                    print(f"sell: DEcreased by {percentage_change:.2f}%")
                    wallet = update_wallet(wallet, percentage_change, buy, sell, keep, leave, smallDecrease)
                    print(f"wallet decrease after sell: {wallet:.2f}")
                    sell = False
                    isDecreasing = False
                else:
                    #keep a small decrease
                    keep = True
                    isMine = True
                    smallDecrease = True
                    track.append(("kd", percentage_change, new_price))
                    print(f"keep sd: DEcreased by {percentage_change:.2f}%")
                    wallet = update_wallet(wallet, percentage_change, buy, sell, keep, leave, smallDecrease)
                    print(f"wallet small decrease after keep sd: {wallet:.2f}")
                    keep = False
                    smallDecrease = False
                    isDecreasing = False
                    print("len track ", len(track))
                    print("NOw analyse track:")
                    if len(track) >= 3:
                        # checking cumulative decrease
                        if track[-1][0] == 'kd' and track[-2][0] == 'kd' and track[-3][0] == 'kd': 
                            print(track[-1][0], track[-2][0], track[-3][0] )
                            cumulative_decrease = abs(track[-1][1]) + abs(track[-2][1]) + abs(track[-3][1])
                            print("Checking cumulative decrease ", cumulative_decrease)
                            if cumulative_decrease >= sellAfterDecrease:
                                keep = False
                                sell = True
                                isMine = False
                                track.append(("s", percentage_change))
                                print(f"sell: DEcreased by {percentage_change:.2f}%")
                                wallet = update_wallet(wallet, percentage_change, buy, sell, keep, leave, smallDecrease)
                                print(f"wallet decrease after sell: {wallet:.2f}")
                                sell = False
                        #sell before anticipated drop:
                        if (track[-1][0] == "kd") and (track[-2][0] == "ki" or track[-2][0] == "kd") and (track[-3][0] == "ki" or track[-3][0] == "kd"):
                            print(track[-3][0], track[-2][0], track[-1][0] )
                            print("Checking for upside down U")
                            if ((track[-3][2] - track[-1][2]) > decreaseForU): #buy if there is a invrease on the other side of the U - working with 5 min intervals
                                keep = False
                                sell = True
                                isMine = False
                                track.append(("s", percentage_change))
                                print(f"sell before anticipated drop: DEcreased by {percentage_change:.2f}%")
                                wallet = update_wallet(wallet, percentage_change, buy, sell, keep, leave, smallDecrease)
                                print(f"wallet decrease after sell: {wallet:.2f}")
                                sell = False
                                isDecreasing = False

        elif not isMine:
        # if i dont own bitcoin
            if isIncreasing:
                #time to buy
                #this will buy after a big  spike
                if percentage_change > buyAfterIncrease and track[-1][0] == "li":
                        print(percentage_change, buyAfterIncrease)
                        leaveIncrease = False
                        buy = True
                        isMine = True
                        track.append(("b", percentage_change))
                        print(f"buy after pc change spike") 
                        wallet = update_wallet(wallet, 0, buy, sell, keep, leave, smallDecrease)
                        print(f"wallet after buy: {wallet:.2f}")
                        buy = False
                        isIncreasing = False
                if percentage_change < buyAfterIncrease and track[-1][0] != "b":
                    # else this will take note of a slight increase
                        print(percentage_change, buyAfterIncrease)
                        leave = True
                        track.append(("li", percentage_change, new_price))
                        print(f"wallet remains same bec i dont own bitcoin (i) {wallet:.2f}")
                        leave = False
                if len(track) >= 3:
                    #this will check if there is a gradual increase
                    if track[-1][0] in ["ld","li"] and track[-2][0] in ["ld", "li"]:
                        leaveIncrease = True
                        track.append(("li", percentage_change, new_price))
                        if track[-1][0] == "li" and track[-2][0] == "li":
                            print("t1 ",track[-1][0], "t2 ",track[-2][0])
                            gradual_increase = track[-2][1] + track[-1][1]
                            print("Checking for gradual increase")
                            if percentage_change > buyAfterIncrease or gradual_increase > buyAfterIncrease:
                                buy = True
                                isMine = True
                                track.append(("b", percentage_change))
                                print(f"buy after li") 
                                wallet = update_wallet(wallet, 0, buy, sell, keep, leave, smallDecrease) #set percentage_change to 0 bec your wallet does NOT when the % chnage
                                print(f"wallet after buy: {wallet:.2f}")
                                buy = False
                                isIncreasing = False
                                leaveIncrease = False
                        gradual_increase = 0
                    #buy before antcipated spike
                    if (track[-1][0] == "li") and (track[-2][0] == "li" or track[-2][0] == "ld") and (track[-3][0] == "li" or track[-3][0] =="ld"):
                        if (track[-1][2] - track[-3][2] > increaseForU): #buy if there is a invrease on the other side of the U 
                            print("Checking for U")
                            buy = True
                            isMine = True
                            track.append(("b", percentage_change))
                            print(f"buy after predicted increase change spike") 
                            wallet = update_wallet(wallet, 0, buy, sell, keep, leave, smallDecrease)
                            print(f"wallet after buy: {wallet:.2f}")
                            buy = False
                            isIncreasing = False

            elif isDecreasing:
                leaveDecrease = True
                track.append(("ld", percentage_change, new_price))
                print(f"wallet remains same bec i dont own bitcoin {wallet:.2f}")
                leaveDecrease = False
                isDecreasing = False

     # analyse(percentage_change, isMine, isIncreasing, isDecreasing, buy, sell, keep, leave)
        # wallet = update_wallet(wallet, percentage_change)
        print(f"FINAL WALLET: {wallet:.2f}")
        print(f"FINAL INVESTMENt: ", investment)
        print("Track: ", track)
        if len(track) >= max_track:
            track.pop(0)
        #time.sleep(180)

