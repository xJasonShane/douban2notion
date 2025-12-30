import requests
from typing import List, Optional
from bs4 import BeautifulSoup
from .models import DoubanMovie
from .config import config
import time

class DoubanAPI:
    """豆瓣爬虫类，用于获取用户电影信息"""

    def __init__(self):
        self.user_id = config.douban_user_id
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_user_movies(self, status: str = "watched", max_pages: int = 50) -> List[DoubanMovie]:
        """
        获取用户电影列表

        Args:
            status: 电影状态，可选值：watched(已看), wish(想看), do(在看)
            max_pages: 最大抓取页数

        Returns:
            电影对象列表
        """
        movies = []
        page = 0
        status_map = {
            "watched": "collect",
            "wish": "wish",
            "do": "do"
        }

        while page < max_pages:
            url = f"https://movie.douban.com/people/{self.user_id}/{status_map[status]}"
            params = {"start": page * 15}

            try:
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")

                movie_items = soup.find_all("div", class_="item")
                if not movie_items:
                    break

                for item in movie_items:
                    movie = self._parse_movie_item(item, status)
                    if movie:
                        movies.append(movie)

                page += 1
                time.sleep(2)

            except Exception as e:
                print(f"获取第{page+1}页电影失败: {e}")
                break

        return movies

    def _parse_movie_item(self, item, status: str) -> Optional[DoubanMovie]:
        """解析单个电影条目"""
        try:
            title_elem = item.find("li", class_="title")
            if not title_elem:
                return None

            title_link = title_elem.find("a")
            if not title_link:
                return None

            title = title_link.text.strip()
            url = title_link.get("href", "")
            douban_id = url.split("/")[-2] if url else ""

            info_elem = item.find("li", class_="intro")
            info_text = info_elem.text.strip() if info_elem else ""

            year = ""
            regions = []
            directors = []
            if info_text:
                parts = [p.strip() for p in info_text.split("/") if p.strip()]
                if len(parts) >= 1:
                    year = parts[0]
                if len(parts) >= 2:
                    regions = [r.strip() for r in parts[1].split(",")]
                if len(parts) >= 3:
                    directors = [d.strip() for d in parts[2].split(",")]

            rating_elem = item.find("span", class_="rating5-t")
            rating = 0.0
            if rating_elem:
                rating_class = rating_elem.get("class", [])
                for cls in rating_class:
                    if cls.startswith("rating"):
                        try:
                            rating = int(cls.replace("rating", "")) / 2.0
                        except:
                            pass

            date_elem = item.find("span", class_="date")
            rating_date = date_elem.text.strip() if date_elem else ""

            comment_elem = item.find("span", class_="comment")
            comment = comment_elem.text.strip() if comment_elem else ""

            pic_elem = item.find("a", class_="nbg")
            poster_url = ""
            if pic_elem:
                img = pic_elem.find("img")
                if img:
                    poster_url = img.get("src", "")

            movie = DoubanMovie(
                id=douban_id,
                title=title,
                original_title="",
                year=year,
                rating=rating,
                genres=[],
                directors=directors,
                casts=[],
                regions=regions,
                release_date="",
                duration=0,
                url=url,
                poster_url=poster_url,
                summary="",
                comment=comment,
                rating_date=rating_date,
                status=status
            )

            return movie

        except Exception as e:
            print(f"解析电影条目失败: {e}")
            return None

    def get_watched_movies(self) -> List[DoubanMovie]:
        """获取已看电影列表"""
        return self.get_user_movies(status="watched")

    def get_wish_movies(self) -> List[DoubanMovie]:
        """获取想看电影列表"""
        return self.get_user_movies(status="wish")

    def get_doing_movies(self) -> List[DoubanMovie]:
        """获取在看电影列表"""
        return self.get_user_movies(status="do")
