

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/rahul-netizen/steam_scrapper/HEAD?labpath=Steam_scrapper_Tutorial.ipynb)

You can run and experiment with the code using free online resources, try executing this notebook by click the "launch" button above.

Or by going to this [link](https://mybinder.org/v2/gh/rahul-netizen/steam_scrapper/HEAD?labpath=Steam_scrapper_Tutorial.ipynb)


# Steam Web Scrapper
![img](https://cdn.cloudflare.steamstatic.com/store/home/store_home_share.jpg)

> In this project I did following things:

- Used *selenium* to run the browser to open the steam website
- Navigated to topsellers page, scrapped game titles for info like name,price,date of game title using *beautiful soup*
- Using *requests* to get page for each tiltle then scrapped info like review,rating,description,tags,publisher,developer of game
- Saved all the data to a *csv* file
- Loading it back using *pandas*
- Sent the csv file using *SMTP*
- Added version control using *git*
- Created a *github action* to automate whole workflow from opening browser, scrapping info, saving csv then sending it to email on scheduled time


> To use this repo
- Fork this repo and add these repository secrets to recieve send/recieve emails using these same named keys, refer [this](https://medium.datadriveninvestor.com/accessing-github-secrets-in-python-d3e758d8089b) on how to add repository secrets

![Imgur](https://i.imgur.com/dETq8cz.png)

- To run locally,make a virtual environment (recommanded) then acitivate the env 
- Clone the repo, navigate to it
- Using terminal/cmd run command `pip install -r requirements.txt` 
- Then `python scrapper.py`
- Either way you can always go ahead and use the jupyter notebook which is very good way to experiment with the code.
