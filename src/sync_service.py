import logging
from typing import List, Dict, Any
from .douban_api import DoubanAPI
from .notion_api import NotionAPI
from .models import DoubanMovie
from .config import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

class SyncService:
    """同步服务类，用于协调豆瓣和Notion之间的数据同步"""

    def __init__(self):
        self.douban_api = DoubanAPI()
        self.notion_api = NotionAPI()
        self.sync_status = config.sync_status

    def get_douban_movies(self) -> List[DoubanMovie]:
        """根据配置的同步状态获取豆瓣电影列表"""
        logger.info(f"开始从豆瓣获取{self._get_status_text()}电影...")

        if self.sync_status == "watched":
            movies = self.douban_api.get_watched_movies()
        elif self.sync_status == "wish":
            movies = self.douban_api.get_wish_movies()
        elif self.sync_status == "do":
            movies = self.douban_api.get_doing_movies()
        else:
            raise ValueError(f"无效的同步状态: {self.sync_status}")

        logger.info(f"成功获取{len(movies)}部{self._get_status_text()}电影")
        return movies

    def sync_movies(self) -> Dict[str, Any]:
        """执行电影同步逻辑"""
        logger.info("开始执行电影同步...")

        if not config.is_database_configured():
            if not config.notion_parent_page_id:
                raise ValueError("未配置NOTION_DATABASE_ID或NOTION_PARENT_PAGE_ID")
            logger.info("自动创建Notion数据库...")
            config.notion_database_id = self.notion_api.create_database(
                config.notion_parent_page_id,
                "豆瓣电影"
            )
            logger.info(f"数据库创建成功: {config.notion_database_id}")

        douban_movies = self.get_douban_movies()

        if config.incremental_sync:
            return self._incremental_sync(douban_movies)
        else:
            return self._full_sync(douban_movies)

    def _full_sync(self, douban_movies: List[DoubanMovie]) -> Dict[str, Any]:
        """全量同步"""
        stats = {"total": len(douban_movies), "added": 0, "updated": 0, "failed": 0}

        for i, movie in enumerate(douban_movies):
            logger.info(f"正在处理第{i+1}/{len(douban_movies)}部电影: {movie.title}")

            try:
                existing_movie = self.notion_api.get_movie_by_douban_id(movie.id)

                if existing_movie:
                    self.notion_api.update_movie_in_database(existing_movie["id"], movie)
                    stats["updated"] += 1
                    logger.info(f"✅ 更新电影: {movie.title}")
                else:
                    self.notion_api.add_movie_to_database(movie)
                    stats["added"] += 1
                    logger.info(f"✅ 添加电影: {movie.title}")

            except Exception as e:
                stats["failed"] += 1
                logger.error(f"❌ 处理电影失败 {movie.title}: {e}")

        self._log_stats(stats)
        return stats

    def _incremental_sync(self, douban_movies: List[DoubanMovie]) -> Dict[str, Any]:
        """增量同步，只同步新增的电影"""
        stats = {"total": len(douban_movies), "added": 0, "updated": 0, "failed": 0}

        existing_ids = set()
        try:
            results = self.notion_api.query_database()
            for page in results:
                douban_id_prop = page.get("properties", {}).get("豆瓣ID", {})
                if douban_id_prop.get("type") == "rich_text":
                    rich_text = douban_id_prop.get("rich_text", [])
                    if rich_text:
                        existing_ids.add(rich_text[0].get("text", {}).get("content", ""))
        except Exception as e:
            logger.warning(f"获取现有电影列表失败，将执行全量同步: {e}")
            return self._full_sync(douban_movies)

        for i, movie in enumerate(douban_movies):
            if movie.id in existing_ids:
                continue

            logger.info(f"正在处理第{stats['added']+1}部新电影: {movie.title}")

            try:
                self.notion_api.add_movie_to_database(movie)
                stats["added"] += 1
                logger.info(f"✅ 添加电影: {movie.title}")

            except Exception as e:
                stats["failed"] += 1
                logger.error(f"❌ 处理电影失败 {movie.title}: {e}")

        self._log_stats(stats)
        return stats

    def _log_stats(self, stats: Dict[str, Any]):
        """记录同步统计信息"""
        logger.info("\n" + "="*50)
        logger.info("同步完成!")
        logger.info(f"总处理电影数: {stats['total']}")
        logger.info(f"新增电影数: {stats['added']}")
        logger.info(f"更新电影数: {stats['updated']}")
        logger.info(f"失败电影数: {stats['failed']}")
        logger.info("="*50)

    def _get_status_text(self) -> str:
        """获取同步状态的中文描述"""
        status_mapping = {
            "watched": "已看",
            "wish": "想看",
            "do": "在看"
        }
        return status_mapping.get(self.sync_status, "已看")
