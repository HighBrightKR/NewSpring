import requests
from parsel import Selector
from bs4 import BeautifulSoup

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

class Database:
    def __init__(self):
        cred = credentials.Certificate("key.json")
        firebase_admin.initialize_app(cred)
        self.db = firestore.client()

        self.article = {
            "khan" : ["class", "content_text"],
            "munhwa" : ["class", "view"],
            "seoul" : ["class", "viewContent"],
            "hankook" : ["class", "editor-p"],
            "segye" : ["class", "viewBox2"],
            "donga" : ["class", "view_box"],
            "maeil" : ["id", "articlebody"],
            "kw" : ["id", "articlebody"],
            "busan" : ["class", "article_content"],
            "kookje" : ["class", "news_article"],
            "jjan" : ["class", "article_txt_container"],
            "kwangju" : ["id", "joinskmbox"],
            "yeongnam" : ["class", "article-news-body"],
            "kyeongin" : ["class", "article-body"],
            "halla" : ["class", "article_txt"],
            "kn" : ["id", "content_li"],
            "gwangnam" : ["id", "content"],
            "ks" : ["id", "article-view-content-div"],
            "domin" : ["id", "article-view-content-div"],
            "finomy" : ["id", "article-view-content-div"],
            "nongmin" : ["class", "news_txt"],
            "jbk" : ["id", "article-view-content-div"],
            "ibulgyo" : ["id", "article-view-content-div"],
            "md" : ["class", "article_body"]

        }

        self.start()

    def get_achievements(self):
        url = "https://www.sinchun.co.kr/2010-2025-shinchun-archive"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }

        res = requests.get(url, headers=headers)
        txt = res.content
        sel = Selector(text=txt.decode('utf-8'))


        # h1 태그 선택
        titles = sel.xpath('//*[@id="__next"]/div/div/div[1]/div/div/div[2]/div[3]/div[4]/div[2]/div/div/div/div/div[3]').getall()
        soup = BeautifulSoup(titles[0], 'html.parser')
        result = soup.get_text(separator='\n', strip=True)
        kk = result.strip().split('\n')
        chunks = [kk[i:i + 7] for i in range(0, len(kk), 7)]
        achievements = []
        for chunk in chunks:
            achievements.append(
                {
                    "press" : chunk[0],
                    "genre" : chunk[1],
                    "url" : chunk[2],
                    "title" : chunk[3],
                    "author" : chunk[5],
                }
            )

        return achievements

    def add_content(self, chunk):
        for key in self.article:
            if key in chunk['url']:
                chunk['content'] = self.get_bytag(chunk['url'], *self.article[key])


    def get_bytag(self, url, kind, tag):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"}
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.content, 'html.parser')
        if kind == "class":
            eles = soup.find_all(class_=tag)
        else:
            eles = soup.find_all(id=tag)
        result = ""
        for ele in eles:
            result += ele.get_text(separator='\n', strip=True)
        return result

    def store_lity(self, datas):
        for data in datas:
            self.db.collection("lity").document(data['title']).set(data)

    def edit_lity(self, data):
        try:
            self.db.collection("lity").document(data['title']).update(data)
        except Exception as e:
            breakpoint("DB 수정 부분에서 오류 발생", str(e))

    def start(self):
        achievements = self.get_achievements()
        for achievement in achievements:
            self.add_content(achievement)
        self.store_lity(achievements)




