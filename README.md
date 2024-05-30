Web scraper that extracts the prices of motorcycle gear articles from 4 websites at regular intervals (daily) in csv format. 

The script runs automatically in the background following a schedule (each day at 12:00). 

Instructions: 

  @ Create a folder for the outputs to be stored in, then assign the full path of this folder to the variable PATH,  
    for example: "Desktop/Programare Extra/PyCharm Py/Web Scraping". 
  
  @ In order for it to run even after the python session (terminal or IDE) is closed, follow the instructions below: 
  
      - open the terminal and type: 
        - cd 'full path of the file, for example: "Desktop/Programare Extra/PyCharm Py/Web Scraping"' (switches to the current directory of the downloaded script) 
        - nohup python3 Backend.py & (runs program in the background, ignoring the hangup signal) 
        - ps ax | grep python (checks if the python program runs in the background; a process named 'python3 Backend.py' must show) 
      - close terminal 
  
  @ The first time being run, the program will create a new csv file for each of the 4 monitored websites, and at subsequent runtimes, it will append to it the updated prices of the articles being monitored. 
  
  @ By default, no article is being monitored, so nothing will change to the csv files unless some articles are chosen by the user to be tracked. 
    
  @ To track any of the articles, open the csv file in Excel and type "Yes" in the 'Tracked' column for that article, then save.
