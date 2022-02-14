import mimetypes
import smtplib
import time
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options


def get_page(url):
    response = requests.get(url)
    if response.ok:
        doc = BeautifulSoup(response.text)
    else:
        print('Page Loading Failed!')

    return doc


def parse_game_titles(title):
    '''
    Funtion to parse a tags to get Name,date,price
    '''
    try:
        title_name = title.find('span', class_='title').text.strip()

        print('Parsing Game title: {}'.format(title_name))

        title_date = title.find(
            'div', class_='col search_released responsive_secondrow').text.strip().split(',')
        title_date = title_date[0] + title_date[-1]

        # find price without discount
        title_price = title.find(
            'div', class_='col search_price responsive_secondrow')
        if not title_price:
            # find price latest price with discount
            title_price = title.find(
                'div', class_='col search_price discounted responsive_secondrow')
        title_price = title_price.text.split('₹')[-1].strip()

    except:
        title_name, title_date, title_price = 'NA', 'NA', 'NA'

    return {
        'title_name': '"' + str(title_name) + '"',
        'realease_date': '"' + str(title_date) + '"',
        'price': '"' + str(title_price) + '"'
    }


def clean_review_tags(tag_element, char):  # to parse revies and game tags
    tag_element = list(map(lambda x: x.strip(), tag_element.text.split(char)))
    tag_element = [tag for tag in tag_element if tag]
    return tag_element


def parse_game_href(href):

    doc = get_page(href)
    print('Parsing Game titles\'s \'href:\'{} '.format(doc.title.text))

    try:
        title_descp = doc.find(
            'div', class_='game_description_snippet').text.strip()

        title_review = doc.find('div', 'summary column')
        title_review = clean_review_tags(title_review, '\n')

        if len(title_review) != 1:
            title_review, title_rating = title_review[:2]
        else:
            title_rating = 0

        developer = doc.find('div', class_='dev_row')
        developer = developer.text.strip().split()[1]

        publisher = doc.find('div', class_='dev_row').find_next_sibling()
        publisher = publisher.text.strip().split()[1]

        title_tags = doc.find('div', class_='glance_tags popular_tags')
        title_tags = clean_review_tags(title_tags, '\t')
        title_tags = ','.join(title_tags)

    except:
        title_descp, title_review, title_rating, developer, publisher, title_tags = [
            'NA']*6

    return {
        'description': '"' + str(title_descp) + '"',
        'title_review': '"' + str(title_review) + '"',
        'title_rating': '"' + str(title_rating) + '"',
        'developer': '"' + str(developer) + '"',
        'publisher': '"' + str(publisher) + '"',
        'game_tags': '"' + str(title_tags) + '"'
    }


def scroll_page(driver):
    SCROLL_PAUSE_TIME = 0.5

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    # scroll for 20 seconds
    time_end = time.time() + 20
    while True and time.time() < time_end:
        # Scroll down to bottom
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def start_driver():
    # initializing the chrome driver
    print('Starting chrome web driver')

    # options = webdriver.ChromeOptions()
    # driver = webdriver.Chrome(
    #     executable_path='./chromedriver.exe', options=options)

    print(os.listdir('.'))

    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    #chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome('/chromedriver',options=chrome_options)

    driver.get('https://store.steampowered.com/')  # opening browswer

    driver.maximize_window()  # maximize to view top sellers options
    # select and click top sellers option
    driver.find_element_by_xpath(
        '/html/body/div[1]/div[7]/div[5]/div[1]/div[1]/div/div[1]/div[8]/a[1]').click()

    scroll_page(driver)
    html_text = driver.page_source  # get scrolled page contents

    return html_text


def get_titles(html_text):
    print('Getting Game titles')
    doc = BeautifulSoup(html_text)
    titles_a_tags = doc.find(
        'div', attrs={'id': 'search_resultsRows'}).find_all('a')
    return titles_a_tags


def write_to_csv(info, path='./steam_data.csv'):
    with open(path, 'w') as f:
        if(len(info) == 0):
            print('Nothing to write!')
            return
        headers = list(info[0].keys())
        f.write(','.join(headers)+'\n')

        for item in info:
            values = []
            for header in headers:
                values.append(str(item.get(header, '')))
            f.write(','.join(values)+'\n')


def send_email():
    print('Sending email..')

    emailfrom = 'unyankopon@gmail.com'
    emailto = "unyankopon@gmail.com"
    fileToSend = "steam_data.csv"
    username = "unyankopon"
    password = ""

    msg = MIMEMultipart()
    msg["From"] = emailfrom
    msg["To"] = emailto
    msg["Subject"] = "Top 100 Topsellers from Steam"

    ctype, encoding = mimetypes.guess_type(fileToSend)
    if ctype is None or encoding is not None:
        ctype = "application/octet-stream"

    maintype, subtype = ctype.split("/", 1)

    fp = open(fileToSend)
    # Note: we should handle calculating the charset
    attachment = MIMEText(fp.read(), _subtype=subtype)
    fp.close()
    encoders.encode_base64(attachment)

    attachment.add_header("Content-Disposition",
                          "attachment", filename=fileToSend)
    msg.attach(attachment)

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(username, password)
        server.sendmail(emailfrom, emailto, msg.as_string())
        server.quit()
        print('Email Sent!')
    except:
        print('Sending Email Failed!')


def scrape_steam_page(num):
    html_text = start_driver()
    titles = get_titles(html_text)
    parsed_titles = [parse_game_titles(title) for title in titles[:num]]
    parsed_game_href = [parse_game_href(tag['href']) for tag in titles[:num]]
    game_info = [title | title_info for title, title_info in zip(
        parsed_titles, parsed_game_href)]  # merge the dictionaries
    write_to_csv(game_info)

    return game_info


if __name__ == '__main__':
    num_titles = 50
    game_info = scrape_steam_page(num_titles)
    # print(game_info[:5])
    send_email
