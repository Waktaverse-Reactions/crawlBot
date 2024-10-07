import time
import discord
from discord.ext import commands
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as bs
from selenium.webdriver.common.by import By
import asyncio

intents = discord.Intents.default()
intents.messages = True  # 메시지 이벤트 수신 허용

TOKEN = 'MTI5MDE3OTc0MzY2NDMxMjM2Mg.GDjrLg.QvwiA_Dda5miQeUtbvhlc74oan6XLsAMpzKkqI'
CHANNEL_ID = 1290237806051987486

# 유저의 게시물 링크를 저장할 리스트
posted_link = None

def login(id, pw):
  # 네이버 로그인 url
  url = 'https://nid.naver.com/nidlogin.login'

  chrome_options = Options()
  chrome_options.add_argument("--headless")  # 브라우저를 보이지 않게 실행

  browser = webdriver.Chrome(options=chrome_options)
  browser.get(url)

  browser.implicitly_wait(2)

  # 로그인
  browser.execute_script("document.getElementsByName('id')[0].value=\'" + id + "\'")
  browser.execute_script("document.getElementsByName('pw')[0].value=\'" + pw + "\'")

  browser.find_element(by=By.XPATH, value='//*[@id="log.login"]').click()
  time.sleep(1)

  return browser

def check_for_new_posts():
    global posted_link

    browser = login('waktaversereactions','wakre123!@')

    browser.get('https://cafe.naver.com/ca-fe/cafes/27842958/members/X4X7z5aOcioCbe1qI-E8UVLKwmBlKET9fovk6zfnmPY?page=1')
    
    time.sleep(2)

    soup = bs(browser.page_source, 'html.parser')
    soup = soup.find_all(class_='article-board article_profile')[0]  # 네이버 카페 구조 확인후 게시글 내용만 가저오기

    datas = soup.select("table > tbody > tr")
    for data in datas:
        article_title = data.find(class_="article")
        link = article_title.get('href')
        break
    if article_title is None:
        article_title = "null"
    else:
        article_title = article_title.get_text().strip()

        if article_title.__contains__("했어요]"):
            new_link = "https://cafe.naver.com" + link
            if new_link != posted_link:
                browser.get(new_link)
                
                time.sleep(2)

                browser.switch_to.frame('cafe_main')
                
                soup = bs(browser.page_source, 'html.parser')
                datas = soup.find_all(class_="se-image-resource")
                img = str(datas).split(" ")[3].replace("src=\"","")[:-4]
                posted_link = new_link
                return new_link, article_title, img
            else:
                return None, None, None


bot = commands.Bot(command_prefix='#',intents=intents)

async def send_to_discord(title, img, post):
    channel = bot.get_channel(CHANNEL_ID)
    embed = discord.Embed(title=title, description=f"[같이보기 링크]({post})")
    embed.set_image(url=img)

    await channel.send(embed=embed)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    while True:
        post, title, img = check_for_new_posts()
        if post != None:
            await send_to_discord(title, img, post)
        await asyncio.sleep(60*3)
bot.run(TOKEN)