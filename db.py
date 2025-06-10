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


    # 신문사별 당선작 링크 가져오기

    class GetPrize:
        def __init__(self):
            self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"}

        def donga(self):
            prizes = []
            for year in range(1998, 2026):
                url = f"https://sinchoon.donga.com/List?m=year&c={year}"
                print(url)
                req = requests.get(url, headers=self.headers)
                soup = BeautifulSoup(req.content, 'html.parser')
                prize_wrap = soup.find('div', class_='prize_wrap')
                uls = prize_wrap.find_all('ul')
                for ul in uls:
                    lis = ul.find_all('li')
                    for li in lis:
                        ctgry = li.find(class_='category')
                        title = li.find(class_='title')
                        writer = li.find(class_='name')
                        url = title.find('a').attrs['href']

                        if "당선작 없음" in title.get_text() or "당선 취소" in title.get_text():
                            continue

                        data = {"category" : ctgry.get_text() if ctgry != None else "카테고리 불명",
                             "url" : url if url != None else "링크 불명",
                             "title" : title.get_text() if title != None else "제목 불명",
                             "writer" : writer.get_text() if writer != None else "작자 미상",
                             "press" : "동아일보"
                            }

                        res = requests.get(url, headers=self.headers)
                        bs = BeautifulSoup(res.content, 'html.parser')
                        contents = bs.find_all('ul', class_='tab_content')

                        for li2, kind in zip(contents, ["content", "review", "thoughts"]):
                            context = li2.find(class_="view_box")
                            for br in context.find_all('br'):
                                br.replace_with('\n')
                            data[kind] = context.get_text()

                        prizes.append(data)
            return prizes

        def chosun(self): # Chonsun Ilbo website is dynamically rendered, requiring Selenium for scraping
            first = True

            for year in range(2015, 2026):


            for year in range(1998, 2026):
                if first:
                    url = f"https://www.chosun.com/nsearch/?query=%5B{year}%20%EC%8B%A0%EC%B6%98%EB%AC%B8%EC%98%88%5D&page=1"
                    req = requests.get(url, headers=self.headers)
                    soup = BeautifulSoup(req.content, 'html.parser')
                    ul = soup.find('ul', class_='pageNumbers')
                    lis = ul.find_all('li')
                    al = len(lis) + 1
                    first = False

                if not 'al' in locals():
                    al = 2

                for page in range(1, al):
                    url = f"https://www.chosun.com/nsearch/?query=%5B{year}%20%EC%8B%A0%EC%B6%98%EB%AC%B8%EC%98%88%5D&page={page}"
                    req = requests.get(url, headers=self.headers)
                    soup = BeautifulSoup(req.content, 'html.parser')
                    article_list = soup.find('div', class_='story-card-wrapper')
                    for article in article_list:
                        tmp = article.find_all('div', recursive=False)
                        a_ele = tmp[:1]
                        a_url = a_ele.find('a')['href']

                        req1 = requests.get(a_url, headers=self.headers)
                        tree = html.fromstring(req1.content)
                        soup1 = BeautifulSoup(req1.content, 'html.parser')
                        title = soup1.find('h1', class_='article-header__headline')
                        cate = tree.xpath('//*[@id="fusion-app"]/div[1]/div[2]/div/div/div[2]/p/span/text()')
                        cate = cate.replace('당선작', '').strip('')
                        writer = tree.xpath('//*[@id="fusion-app"]/div[1]/div[2]/div/section/article/div[1]/div/span/text()')

                        ##







    class FireBase:
        def __init__(self):
            cred = credentials.Certificate("key.json")
            firebase_admin.initialize_app(cred)
            self.db = firestore.client()

        def add_from_list(self, data):
            for datum in data:
                if "/" in datum["title"]:
                    datum["title"] = datum["title"].replace("/", "\\")
                self.db.collection('prizes').document(datum["title"]).set(datum)

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




