import csv
import time
import gspread
import os
import memory_profiler

from enchant.checker import SpellChecker
from bs4 import BeautifulSoup
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from selenium.common.exceptions import JavascriptException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException

from utils import custom_logger, paste_csv_to_wks

m1 = memory_profiler.memory_usage()
t1 = datetime.now()

CURRENT_DIR = '/home/ubuntu/facebookscraper'
#CURRENT_DIR = '.'
WINDOW_SIZE = "1024,2080"
URL = "https://www.facebook.com/pg/candycrushsaga/posts/"
SCROLL_PAUSE_TIME = 3
EXCEPTION_SLEEP_TIME = 2
NUMBER_OF_POSTS = 2

current_time = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
filename = f'{CURRENT_DIR}/logs/scraped_{current_time}.log'

logger = custom_logger(filename)

logger.info(f'Logfile name {filename}')

# Chrome browser options - Version 79.0.3945.88 (Official Build) (64-bit)
chrome_options = Options()
# chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")

chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--mute-audio")
chrome_options.add_argument("--headless")

driver = webdriver.Chrome(
    executable_path="/usr/bin/chromedriver", options=chrome_options)

# Heroku deployment driver
# driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=chrome_options)

driver.set_page_load_timeout(500)

logger.info("Opening page..")
driver.get(URL)
time.sleep(10)
try:
    logger.info("Waiting for page to load...")
    time.sleep(10)
    el = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "u_0_bx")))
except TimeoutException as err:
    logger.info("Something went wrong trying again")
    driver.quit()
    exit()

logger.info("Page loaded!")
time.sleep(3)

see_more = driver.find_elements_by_xpath(
    '//*[@id="www_pages_reaction_see_more_unitwww_pages_posts"]/div/a')
actions = ActionChains(driver)
actions.move_to_element(see_more[0]).perform()
time.sleep(SCROLL_PAUSE_TIME)

not_now = driver.find_element_by_xpath('//*[@id="expanding_cta_close_button"]')
not_now.click()

time.sleep(5)

new_see_more = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
    (By.XPATH, '//*[@id="www_pages_reaction_see_more_unitwww_pages_posts"]/div/a')))

time.sleep(3)

page = 1

logger.info(f"Currently at page {page}")

while True:
    n = None
    try:
        see_more_ = driver.find_elements_by_xpath(
            '//*[@id="www_pages_reaction_see_more_unitwww_pages_posts"]/div/a')
        ActionChains(driver).move_to_element(see_more_[0]).perform()
        time.sleep(SCROLL_PAUSE_TIME)
        n = False
    except JavascriptException:
        logger.info("Caught the JavascriptException exception! Sleeping")
        time.sleep(EXCEPTION_SLEEP_TIME)
        logger.info("Resuming...")
    except StaleElementReferenceException:
        logger.info(
            "Caught the StaleElementReferenceException exception! Sleeping")
        time.sleep(EXCEPTION_SLEEP_TIME)
        logger.info("Resuming...")
    except NoSuchElementException:
        logger.info("Reached the bottom of the page")
        break
    except TimeoutException as err:
        logger.error("Time out exception! Sleeping")
        time.sleep(EXCEPTION_SLEEP_TIME)
        logger.info("Resuming...")
        n = True

    all_posts_count = len(driver.find_elements_by_xpath(
        "//a[@data-testid='UFI2ViewOptionsSelector/link']"))
    logger.info(f"All post count {all_posts_count}")

    if all_posts_count >= NUMBER_OF_POSTS:
        break
    if n:
        logger.info(f"Waiting on page {page}")
    else:
        page += 1
        logger.info(f"Moving to page {page}")


try:
    driver.execute_script(
        'document.querySelectorAll("div._5hn6#u_0_bx").remove();')
    driver.execute_script(
        "document.querySelector('#content>div>div>div._1qkq._1ql0>div._1pfm').style.height = '0';")
    driver.execute_script(
        "document.querySelector('#content>div>div>div._1qkq._1ql0>div._1pfm').style.display = 'none';")
except:
    logger.error("Did not find the login pop up at the bottom of the page")
    pass


all_posts = driver.find_elements_by_xpath(
    "//a[@data-testid='UFI2ViewOptionsSelector/link']")
total_number_of_posts = len(all_posts)
all_posts_to_be_parsed = None
logger.info(f"Total number of posts {total_number_of_posts}")

if total_number_of_posts >= NUMBER_OF_POSTS:
    all_posts_to_be_parsed = all_posts[:NUMBER_OF_POSTS]
else:
    all_posts_to_be_parsed = all_posts

logger.info(f"Post to be parsed {len(all_posts_to_be_parsed)}")

for (index, post) in enumerate(all_posts_to_be_parsed):
    logger.info(f"Clicking on post {index + 1}")

    if(index == 17):
        time.sleep(2)

    ActionChains(driver).move_to_element(post).perform()
    driver.execute_script("scrollBy(0,500);")
    post.click()
    driver.find_element_by_xpath(
        '//div[@data-testid="UFI2ViewOptionsSelector/menuRoot"]/div/ul/li[last()]').click()
    time.sleep(2)

all_comment_blocks = driver.find_elements_by_xpath(
    "//div[@data-testid='UFI2CommentsList/root_depth_0']")
total_number_of_comment_blocks = len(all_comment_blocks)
logger.info(f"Total number of comment blocks {total_number_of_comment_blocks}")

comment_block = None

if total_number_of_posts >= NUMBER_OF_POSTS:
    comment_block = all_comment_blocks[:NUMBER_OF_POSTS]
else:
    comment_block = all_comment_blocks

facebook_c = driver.find_element_by_xpath(
    '//div[@aria-label="Facebook"]/div/following-sibling::*')


try:
    driver.execute_script(
        "document.getElementById('u_0_bx').remove();")
except Exception as err:
    logger.error("Did not find the element")
    logger.error(err)
    pass


for (i, block) in enumerate(comment_block):
    logger.info(f"Clicking on comment block {i + 1}")
    while True:
        try:
            ActionChains(driver).move_to_element(block).perform()
            more_comments = block.find_elements_by_css_selector(
                '[class^="_4swz _7a93"]')

            if not more_comments:
                break

            more_comments_link = more_comments[0]
            ActionChains(driver).move_to_element(more_comments_link).perform()
            driver.execute_script("scrollBy(0,500);")
            more_comments_link.click()
            time.sleep(0.05)
        except NoSuchElementException as err:
            logger.info("Clicked all more comments")
            break
        except StaleElementReferenceException as err:
            logger.error(err)
            pass


for (i, block) in enumerate(comment_block):
    logger.info(f"Clicking on replies on comment block {i + 1}")
    while True:
        try:
            ActionChains(driver).move_to_element(block).perform()
            replies = block.find_elements_by_css_selector(
                '[class^="_4sso _4ssp"]')
            loading_replies = block.find_elements_by_css_selector(
                '[class^="_4sxg img _55ym _55yn _55yo"]')

            if not replies:
                break

            replies_link = None
            replies_len = len(replies)
            loading_replies_len = len(loading_replies)

            if not loading_replies:
                logger.info(f"Replies : {replies_len}")
                replies_link = replies[0]
            elif replies_len > loading_replies_len:
                logger.info(f"Loading : {loading_replies_len}")
                logger.info(f"Replies : {replies_len}")
                click_index = replies_len - loading_replies_len
                replies_link = replies[-click_index]
            else:
                logger.info(f"Loading : {loading_replies_len}")
                logger.info(f"Replies : {replies_len}")
                break

            try:
                ActionChains(driver).move_to_element(replies_link).perform()
                replies_link.click()
                ActionChains(driver).move_to_element(facebook_c).perform()
                time.sleep(0.05)
            except ElementClickInterceptedException as err:
                logger.error("Element covered and not clickable")
                time.sleep(EXCEPTION_SLEEP_TIME)
                driver.execute_script("scrollBy(0,500);")
                ActionChains(driver).move_to_element(replies_link).perform()
                replies_link.click()
                ActionChains(driver).move_to_element(facebook_c).perform()

        except NoSuchElementException as err:
            logger.info("Clicked all replies")
            break

all_comments = driver.find_elements_by_class_name("_72vr")
logger.info(f"Total number of comments scrapped: {len(all_comments)}")

soup = BeautifulSoup(driver.page_source, 'html.parser')

# ==============================================================
# Post data
post_block = "._5pcr.userContentWrapper"  # class name
# class name get the abbr and use the data-utime attribute
post_title_with_time = "._6a._5u5j._6b"
post_link = "//div[@class='_6a _5u5j _6b']/div/span/span/a"
post_text = "._5pbx.userContent._3576"  # class name
post_reactions = "UFI2ReactionsCount/sentenceWithSocialContext"  # data-testid span
post_share = "UFI2SharesCount/root"  # data-testid

# Comments data
comment_block = "UFI2CommentsList/root_depth_0"  # data-testid div
parent_comment = "UFI2Comment/root_depth_0"  # data-testid div
reply_comment = "UFI2Comment/root_depth_1"  # data-testid div

comment_body = "UFI2Comment/body"  # data-testid div
comment_user_name = "_6qw4"  # class name in a span
comment_text = "._3l3x"  # class name in a span inside a span
comment_reaction = "UFI2CommentTopReactions/tooltip"  # data-testid span
comment_creation_time = "livetimestamp"

post_block_html = soup.select(post_block)
post_block_html_to_parsed = post_block_html[:NUMBER_OF_POSTS]

driver.quit()

csv_written_time = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
filepath = f'{CURRENT_DIR}/csv/scraped_{csv_written_time}.csv'


def is_in_english(quote):
    d = SpellChecker("en_US")
    d.set_text(quote)
    errors = [err.word for err in d]
    return False if ((len(errors) > 5) or len(quote.split()) < 1) else True


with open(filepath, 'w', encoding='utf-8') as csv_file:
    fileWriter = csv.writer(csv_file, dialect='excel')
    logger.info(f"Writing data to {filepath}")

    for (i, post_block_h) in enumerate(post_block_html_to_parsed):
        post_title_with_time_h = post_block_h.select(post_title_with_time)
        post_link_h = post_title_with_time_h[0].select(
            'div span span.fsm.fwn.fcg a')[0].attrs
        link_h = post_link_h.get('href', '')
        post_author = post_title_with_time_h[0].select('h5 a')[0].text
        post_text_h = post_block_h.select(post_text)[0].text
        post_text_with_link = f'{post_text_h}, post link: https://www.facebook.com{link_h}'
        time_attr = post_title_with_time_h[0].select("abbr")[0].attrs
        time = datetime.fromtimestamp(int(time_attr['data-utime']))
        post_reactions_h = post_block_h.findAll(
            "span", {"data-testid": post_reactions})[0].text
        line = [post_author, post_text_with_link, time, post_reactions_h]
        fileWriter.writerow(line)

        comment_block_h = post_block_h.findAll(
            "div", {"data-testid": comment_block})
        all_parent_comments = comment_block_h[0].findAll(
            "div", {"data-testid": parent_comment})
        all_child_comments = comment_block_h[0].findAll(
            "div", {"data-testid": reply_comment})
        all_comments = all_parent_comments + all_child_comments

        for (j, comment) in enumerate(all_comments):
            username = comment.select("._6qw4")[0].text

            comment_text_h = comment.select(comment_text)
            text = None
            if not comment_text_h:
                text = "IMAGE/GIF"
            else:
                text = comment_text_h[0].text

            # TODO Check if the text is in english
            if not is_in_english(text):
                logger.info(f"'{text}' is not english")
                continue

            comment_creation_time_h = comment.findAll(
                "abbr", {"class": [comment_creation_time]})[0].attrs
            time = datetime.fromtimestamp(
                int(comment_creation_time_h['data-utime']))
            comment_reaction_h = comment.find(
                "span", attrs={'data-testid': comment_reaction})

            reaction = None

            if comment_reaction_h is not None:
                reaction = comment_reaction_h.text
            else:
                reaction = 0

            row = [username, text, time, reaction]
            fileWriter.writerow(row)

        fileWriter.writerow(["", "", "", ""])


logger.info('Writing complete!')

logger.info('Writing to "Facebook scraping" googlesheets')

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    f'{CURRENT_DIR}/client_secret.json', scope)

gc = gspread.authorize(credentials)
wks = gc.open("Facebook scraping")
paste_csv_to_wks(filepath, wks, 'A2', logger)

logger.info('Writing to googlesheets complete!')

t2 = datetime.now()
m2 = memory_profiler.memory_usage()

time_diff = t2 - t1
mem_diff = m2[0] - m1[0]
logger.info(
    f"It took {time_diff} Secs and {mem_diff} Mb to execute this method")
