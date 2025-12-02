from typing import List, Optional

class DoubanMovie:
    """豆瓣电影数据模型"""
    
    def __init__(self, 
                 id: str, 
                 title: str, 
                 original_title: str, 
                 year: str, 
                 rating: float, 
                 genres: List[str], 
                 directors: List[str], 
                 casts: List[str], 
                 regions: List[str], 
                 release_date: str, 
                 duration: int, 
                 url: str, 
                 poster_url: str, 
                 summary: str, 
                 comment: Optional[str] = None, 
                 rating_date: Optional[str] = None, 
                 status: str = "watched"):
        """
        初始化豆瓣电影对象
        
        Args:
            id: 豆瓣电影ID
            title: 电影名称
            original_title: 原始名称
            year: 上映年份
            rating: 评分
            genres: 类型列表
            directors: 导演列表
            casts: 演员列表
            regions: 地区列表
            release_date: 上映日期
            duration: 时长(分钟)
            url: 豆瓣链接
            poster_url: 海报链接
            summary: 简介
            comment: 用户评论(可选)
            rating_date: 评分日期(可选)
            status: 状态(已看/想看/在看)
        """
        self.id = id
        self.title = title
        self.original_title = original_title
        self.year = year
        self.rating = rating
        self.genres = genres
        self.directors = directors
        self.casts = casts
        self.regions = regions
        self.release_date = release_date
        self.duration = duration
        self.url = url
        self.poster_url = poster_url
        self.summary = summary
        self.comment = comment
        self.rating_date = rating_date
        self.status = status
    
    def __repr__(self):
        """返回电影对象的字符串表示"""
        return f"DoubanMovie(id={self.id}, title={self.title}, year={self.year}, rating={self.rating})"
    
    def to_dict(self):
        """将电影对象转换为字典"""
        return {
            "id": self.id,
            "title": self.title,
            "original_title": self.original_title,
            "year": self.year,
            "rating": self.rating,
            "genres": self.genres,
            "directors": self.directors,
            "casts": self.casts,
            "regions": self.regions,
            "release_date": self.release_date,
            "duration": self.duration,
            "url": self.url,
            "poster_url": self.poster_url,
            "summary": self.summary,
            "comment": self.comment,
            "rating_date": self.rating_date,
            "status": self.status
        }
