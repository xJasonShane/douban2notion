from notion_client import Client, APIResponseError
from typing import List, Optional, Dict, Any
from .models import DoubanMovie
from .config import config

class NotionAPI:
    """Notion API调用类，用于管理Notion数据库和同步数据"""

    def __init__(self):
        self.notion = Client(auth=config.notion_api_key)
        self.database_id = config.notion_database_id

    def create_database(self, parent_page_id: str, database_name: str = "豆瓣电影") -> str:
        """创建Notion数据库"""
        try:
            properties = self._get_properties_template()

            database = self.notion.databases.create(
                parent={"type": "page_id", "page_id": parent_page_id},
                title=[{"type": "text", "text": {"content": database_name}}],
                properties=properties
            )

            return database["id"]

        except Exception as e:
            print(f"创建Notion数据库失败: {e}")
            raise

    def _get_properties_template(self) -> Dict[str, Any]:
        """获取数据库属性模板"""
        return {
            "电影名称": {"title": {}},
            "豆瓣ID": {"rich_text": {}},
            "状态": {
                "select": {
                    "options": [
                        {"name": "已看", "color": "green"},
                        {"name": "想看", "color": "blue"},
                        {"name": "在看", "color": "yellow"}
                    ]
                }
            },
            "评分": {"number": {"format": "number"}},
            "上映年份": {"number": {"format": "number"}},
            "导演": {"rich_text": {}},
            "地区": {"multi_select": {"options": []}},
            "豆瓣链接": {"url": {}},
            "海报": {"files": {}},
            "简介": {"rich_text": {}},
            "用户评论": {"rich_text": {}},
            "评分日期": {"date": {}}
        }

    def query_database(self) -> List[Dict[str, Any]]:
        """查询Notion数据库"""
        try:
            results = []
            start_cursor = None

            while True:
                response = self.notion.databases.query(
                    database_id=self.database_id,
                    start_cursor=start_cursor
                )

                results.extend(response.get("results", []))

                if not response.get("has_more"):
                    break

                start_cursor = response.get("next_cursor")

            return results

        except APIResponseError as e:
            if e.code == "object_not_found":
                print(f"数据库不存在，请检查NOTION_DATABASE_ID配置")
            raise

    def add_movie_to_database(self, movie: DoubanMovie) -> Dict[str, Any]:
        """将电影添加到Notion数据库"""
        try:
            properties = self._build_properties(movie)

            page = self.notion.pages.create(
                parent={"type": "database_id", "database_id": self.database_id},
                properties=properties
            )

            return page

        except Exception as e:
            print(f"添加电影到Notion数据库失败: {e}")
            raise

    def update_movie_in_database(self, page_id: str, movie: DoubanMovie) -> Dict[str, Any]:
        """更新Notion数据库中的电影"""
        try:
            properties = self._build_properties(movie)

            page = self.notion.pages.update(
                page_id=page_id,
                properties=properties
            )

            return page

        except Exception as e:
            print(f"更新电影到Notion数据库失败: {e}")
            raise

    def _build_properties(self, movie: DoubanMovie) -> Dict[str, Any]:
        """构建页面属性"""
        status_mapping = {
            "watched": "已看",
            "wish": "想看",
            "do": "在看"
        }

        properties = {
            "电影名称": {
                "title": [{"text": {"content": movie.title}}]
            },
            "豆瓣ID": {
                "rich_text": [{"text": {"content": movie.id}}]
            },
            "状态": {
                "select": {"name": status_mapping.get(movie.status, "已看")}
            },
            "评分": {"number": movie.rating},
            "豆瓣链接": {"url": movie.url},
            "简介": {
                "rich_text": [{"text": {"content": movie.summary[:2000]}}]
            }
        }

        if movie.year and movie.year.isdigit():
            properties["上映年份"] = {"number": int(movie.year)}

        if movie.directors:
            properties["导演"] = {
                "rich_text": [{"text": {"content": ", ".join(movie.directors)}}]
            }

        if movie.regions:
            properties["地区"] = {
                "multi_select": [{"name": region} for region in movie.regions]
            }

        if movie.poster_url:
            properties["海报"] = {
                "files": [{
                    "type": "external",
                    "name": f"{movie.title}海报",
                    "external": {"url": movie.poster_url}
                }]
            }

        if movie.comment:
            properties["用户评论"] = {
                "rich_text": [{"text": {"content": movie.comment}}]
            }

        if movie.rating_date:
            properties["评分日期"] = {"date": {"start": movie.rating_date}}

        return properties

    def get_movie_by_douban_id(self, douban_id: str) -> Optional[Dict[str, Any]]:
        """根据豆瓣ID查询电影"""
        try:
            results = self.query_database()

            for page in results:
                douban_id_prop = page.get("properties", {}).get("豆瓣ID", {})
                if douban_id_prop.get("type") == "rich_text":
                    rich_text = douban_id_prop.get("rich_text", [])
                    if rich_text and rich_text[0].get("text", {}).get("content") == douban_id:
                        return page

            return None

        except Exception as e:
            print(f"根据豆瓣ID查询电影失败: {e}")
            return None
