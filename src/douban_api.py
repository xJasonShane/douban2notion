import requests
from typing import List
from .models import DoubanMovie
from .config import config

class DoubanAPI:
    """豆瓣API调用类，用于获取用户电影信息"""
    
    def __init__(self):
        """初始化豆瓣API客户端"""
        self.base_url = "https://api.douban.com/v2/movie"
        self.user_id = config.douban_user_id
        self.api_key = config.douban_api_key
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    
    def get_user_movies(self, status: str = "watched", start: int = 0, count: int = 100) -> List[DoubanMovie]:
        """
        获取用户电影列表
        
        Args:
            status: 电影状态，可选值：watched(已看), wish(想看), do(在看)
            start: 起始位置
            count: 每页数量
            
        Returns:
            电影对象列表
        """
        endpoint = f"/user/{self.user_id}/collection"
        params = {
            "start": start,
            "count": count,
            "status": status,
            "apiKey": self.api_key
        }
        
        try:
            response = requests.get(
                f"{self.base_url}{endpoint}",
                params=params,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            movies = []
            
            # 处理分页
            if data.get("total") > start + count:
                # 递归获取所有数据
                movies.extend(self.get_user_movies(status, start + count, count))
            
            # 处理当前页数据
            for item in data.get("collections", []):
                movie_data = item.get("subject", {})
                rating = item.get("rating", {})
                
                # 创建电影对象
                movie = DoubanMovie(
                    id=str(movie_data.get("id")),
                    title=movie_data.get("title", ""),
                    original_title=movie_data.get("original_title", ""),
                    year=movie_data.get("year", ""),
                    rating=rating.get("value", 0.0),
                    genres=movie_data.get("genres", []),
                    directors=[d.get("name", "") for d in movie_data.get("directors", [])],
                    casts=[c.get("name", "") for c in movie_data.get("casts", [])],
                    regions=movie_data.get("countries", []),
                    release_date=movie_data.get("mainland_pubdate", ""),
                    duration=movie_data.get("durations", [0])[0] if movie_data.get("durations") else 0,
                    url=movie_data.get("alt", ""),
                    poster_url=movie_data.get("images", {}).get("large", ""),
                    summary=movie_data.get("summary", ""),
                    comment=item.get("comment", ""),
                    rating_date=item.get("created_at", ""),
                    status=status
                )
                movies.append(movie)
            
            return movies
            
        except requests.exceptions.RequestException as e:
            print(f"豆瓣API请求失败: {e}")
            return []
    
    def get_watched_movies(self) -> List[DoubanMovie]:
        """获取已看电影列表"""
        return self.get_user_movies(status="watched")
    
    def get_wish_movies(self) -> List[DoubanMovie]:
        """获取想看电影列表"""
        return self.get_user_movies(status="wish")
    
    def get_doing_movies(self) -> List[DoubanMovie]:
        """获取在看电影列表"""
        return self.get_user_movies(status="do")
