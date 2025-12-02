from typing import List, Dict, Any
from .douban_api import DoubanAPI
from .notion_api import NotionAPI
from .models import DoubanMovie
from .config import config

class SyncService:
    """同步服务类，用于协调豆瓣和Notion之间的数据同步"""
    
    def __init__(self):
        """初始化同步服务"""
        self.douban_api = DoubanAPI()
        self.notion_api = NotionAPI()
        self.sync_status = config.sync_status
    
    def get_douban_movies(self) -> List[DoubanMovie]:
        """
        根据配置的同步状态获取豆瓣电影列表
        
        Returns:
            电影对象列表
        """
        print(f"开始从豆瓣获取{self._get_status_text()}电影...")
        
        if self.sync_status == "watched":
            movies = self.douban_api.get_watched_movies()
        elif self.sync_status == "wish":
            movies = self.douban_api.get_wish_movies()
        elif self.sync_status == "do":
            movies = self.douban_api.get_doing_movies()
        else:
            raise ValueError(f"无效的同步状态: {self.sync_status}")
        
        print(f"成功获取{len(movies)}部{self._get_status_text()}电影")
        return movies
    
    def sync_movies(self) -> Dict[str, Any]:
        """
        执行电影同步逻辑
        
        Returns:
            同步结果统计
        """
        print("开始执行电影同步...")
        
        # 获取豆瓣电影列表
        douban_movies = self.get_douban_movies()
        
        # 初始化统计数据
        stats = {
            "total": len(douban_movies),
            "added": 0,
            "updated": 0,
            "failed": 0
        }
        
        # 执行同步
        for i, movie in enumerate(douban_movies):
            print(f"正在处理第{i+1}/{len(douban_movies)}部电影: {movie.title}")
            
            try:
                # 检查电影是否已存在于Notion数据库
                existing_movie = self.notion_api.get_movie_by_douban_id(movie.id)
                
                if existing_movie:
                    # 更新现有电影
                    self.notion_api.update_movie_in_database(existing_movie["id"], movie)
                    stats["updated"] += 1
                    print(f"✅ 更新电影: {movie.title}")
                else:
                    # 添加新电影
                    self.notion_api.add_movie_to_database(movie)
                    stats["added"] += 1
                    print(f"✅ 添加电影: {movie.title}")
                    
            except Exception as e:
                stats["failed"] += 1
                print(f"❌ 处理电影失败 {movie.title}: {e}")
        
        # 打印同步结果
        print("\n" + "="*50)
        print("同步完成!")
        print(f"总处理电影数: {stats['total']}")
        print(f"新增电影数: {stats['added']}")
        print(f"更新电影数: {stats['updated']}")
        print(f"失败电影数: {stats['failed']}")
        print("="*50)
        
        return stats
    
    def _get_status_text(self) -> str:
        """
        获取同步状态的中文描述
        
        Returns:
            中文状态描述
        """
        status_mapping = {
            "watched": "已看",
            "wish": "想看",
            "do": "在看"
        }
        return status_mapping.get(self.sync_status, "已看")
