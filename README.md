# From HTTP to telegram bot
Send message to telegram bot via http GET request.
Based on CherryPy. Tested on HEROKU

1. Register new bot or take your current token
2. Startup your web server or register account on Heroku 
3. Set on server the local variables NAME and TOKEN

For example on Heroku:
http://[bot name].herokuapp.com/bot/?chat_id=[chat id]&message=[text message]
