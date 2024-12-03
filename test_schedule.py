from datetime import datetime, timedelta



print(datetime.now().strftime('%H:%M %d %m %Y' ))

correction = timedelta(days = 2)

print((datetime.now()+correction).strftime('%H:%M %d %m %Y' ))