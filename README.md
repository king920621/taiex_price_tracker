---
# taiex_price_tracker

## 這是一個盡可能減少權限需求的追蹤台指期的機器人(測試中)
~~學弟妹的作業~~
### 初始設定:

將此專案GIT下來

```bash
git clone https://github.com/king920621/taiex_price_tracker.git
```

後使用docker將其build起來

```bash
docker build -t taiex-bot .
```

(依據清況選擇是否使用sudo)

```bash
sudo docker build -t taiex-bot .
```

建立container (將  “你的_實際_Discord_Bot_Token” 更換為你的Discord_Bot_Token)

```bash
docker run -d \
  --name taiex-bot-container \
  --restart unless-stopped \
  -e DISCORD_BOT_TOKEN=你的_實際_Discord_Bot_Token \
  --dns 8.8.8.8 \
  taiex-bot
```

(依據清況選擇是否使用sudo)


~~我的BNB地址，歡迎抖內~~
0x5e37d4aa235c87755f1ac7edee1addd1f9689604