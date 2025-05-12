import discord
import yfinance as yf
import asyncio
import os
from dotenv import load_dotenv # 建議使用 dotenv 來管理敏感資訊

# --- 配置 ---
# 建議將 TOKEN 放在 .env 文件中
load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN') # 從環境變量獲取 Bot Token
# 注意：公開 Bot 不需要 GUILD_ID，因為它要在所有伺服器中工作
TAIEX_SYMBOL = '^TWII' # 台灣加權指數在 yfinance 中的代號
UPDATE_INTERVAL_SECONDS = 60 # 每隔多少秒更新一次 (建議至少 60 秒或以上)

# --- Discord 客戶端設置 ---
# 需要啟用某些 Intents，對於公開 Bot，通常需要這些 Intents
intents = discord.Intents.default()
intents.presences = True # 啟用狀態 Intent (更新狀態需要)
intents.members = True   # 啟用成員 Intent (獲取 guild.me 可能需要，雖然不是強制)
# 如果 Bot 會加入大量伺服器，可能需要 shard 設置，但對於中小型 Bot 暫時不考慮

client = discord.Client(intents=intents)

# --- 獲取股價數據的函數 ---
def fetch_taiex_data():
    """從 yfinance 獲取台灣加權指數的最新數據"""
    try:
        ticker = yf.Ticker(TAIEX_SYMBOL)
        # 嘗試獲取分鐘級數據，可能更接近實時
        data = ticker.history(period="1d", interval="1m")

        if data.empty:
             # 如果分鐘級數據為空，嘗試獲取日線數據
             data = ticker.history(period="2d")

        if not data.empty:
            latest_price = data['Close'].iloc[-1]

            # 計算漲跌和漲跌幅，需要前一天的收盤價
            past_data = ticker.history(period="2d")
            if len(past_data) >= 2:
                 previous_close = past_data['Close'].iloc[-2]
                 change = latest_price - previous_close
                 percentage_change = (change / previous_close) * 100 if previous_close != 0 else 0
            else:
                 change = None
                 percentage_change = None
                 print("Warning: Not enough historical data to calculate change.")

            return latest_price, change, percentage_change
        else:
            print("yfinance returned empty data.")
            return None, None, None
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None, None, None

# --- 定期更新 Bot 狀態和暱稱的任務 ---
async def update_taiex_info():
    """定期獲取股價數據並更新 Bot 的狀態和它所在的所有伺服器中的暱稱"""
    await client.wait_until_ready()
    print("Public update task started.")

    while not client.is_closed():
        print("Fetching TAIEX data...")
        price, change, percentage_change = fetch_taiex_data()

        if price is not None:
            # 格式化顯示資訊 (這些資訊是全局的，所有伺服器都一樣)
            nickname_str = f"TAIEX: {price:,.2f}"

            if change is not None and percentage_change is not None:
                 change_sign = "+" if change >= 0 else ""
                 status_str = f"{change_sign}{change:,.2f} ({change_sign}{percentage_change:.2f}%)"
            else:
                 status_str = "無法計算漲跌" # 如果無法計算漲跌則顯示此信息

            print(f"Fetched data: Nick='{nickname_str}', Status='{status_str}'")

            # --- 更新 Bot 的全局狀態/活動 ---
            try:
                activity = discord.Activity(type=discord.ActivityType.watching, name=status_str)
                await client.change_presence(activity=activity)
                print("Global status updated successfully.")
            except Exception as e:
                 print(f"Error updating global status: {e}")

            # --- 遍歷 Bot 所在的所有伺服器並更新暱稱 ---
            print(f"Attempting to update nickname on {len(client.guilds)} guilds...")
            for guild in client.guilds:
                try:
                    # guild.me 是 Bot 在該伺服器中的成員對象
                    # 嘗試更改 Bot 在這個伺服器中的暱稱
                    await guild.me.edit(nick=nickname_str)
                    print(f"Successfully updated nickname in guild: {guild.name} ({guild.id})")
                except discord.Forbidden:
                    # 如果 Bot 沒有必要的權限 (現在是 'Change Nickname')，這裡會拋出 Forbidden 異常
                    # 舊的 'Manage Nicknames' 權限通常也包含更改自己的暱稱
                    print(f"Permission denied to update nickname in guild: {guild.name} ({guild.id}). Requires 'Change Nickname' permission for the bot.")
                except Exception as e:
                    # 處理其他可能的錯誤
                    print(f"Error updating nickname in guild {guild.name} ({guild.id}): {e}")

        else:
            print("Failed to fetch data, skipping update this interval.")
            # 可選：在抓取失敗時設置一個特殊的全局狀態
            # try:
            #     activity = discord.Activity(type=discord.ActivityType.watching, name="TAIEX: Data Error")
            #     await client.change_presence(activity=activity)
            # except Exception as e:
            #      print(f"Error setting error status: {e}")

        # 等待指定的時間間隔
        await asyncio.sleep(UPDATE_INTERVAL_SECONDS)

# --- Bot 事件：當 Bot 啟動並連線成功時 ---
@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    print(f'Logged in as: {client.user.name} - {client.user.id}')
    print(f'Bot is in {len(client.guilds)} guilds.')
    print('------')

    # 在 Bot 連線成功後，創建並啟動後台更新任務
    client.loop.create_task(update_taiex_info())

# --- 運行 Bot ---
if TOKEN is None:
    print("Error: Please set DISCORD_BOT_TOKEN environment variable or check your .env file.")
else:
    client.run(TOKEN)