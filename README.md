# shameless_telegram_bot
Introducing Shameless Telegram Bot (Version 1.0)

The Shameless Telegram Bot is a powerful tool designed to interact with the shameless.cz website. 
Packed with a range of versatile functionalities, this bot offers a convenient and efficient way to stay up-to-date with all the latest shifts.

### Key Features:
* Automated Shift Updates:
  Stay informed with timely updates as the bot regularly fetches and delivers new shifts directly from shameless.cz.
  Say goodbye to manual checks, and let the bot do the work for you.

* Shift Catalog: 
  Browse and explore all available shifts on the website effortlessly.
  The bot provides a comprehensive list, giving you a clear overview of all available shifts.
* Customized Shift Selection:
  Tailor your search with specific criteria to find shifts that match your preferences.
  For now the following criteria are available:
  * date or interval of dates
  * working position
  * size of shifts



##### How to run web-scraper with a certain frequency?
To run the web-scraping script regularly, I utilized systemd. I created 2 files: .service and .timer
* File with .service extension defines path to executable file, python3, output for standard logs and errors
* File with .timer extension schedules the .service file every 3 minutes 24/7. Of course, you can adjust the frequency to 5, 10 or 30 minutes as per your requirements.
It is also possible to run file on specific days, but in this case, it wasn't necessary.

##### How to run bot 24/7 on ubuntu-server, even if you are disconnected?
To ensure the bot runs continuously, even when you are disconnected, I used the nohup command. This command prevents the processes or jobs from receiving the SIGHUP (Signal Hang UP) signal.
Simply run the following command to start the bot:
`nohup python3 main.py &`
This will create a process that runs independently.

                
Innovate, Create, Automate  
rastr-0  
