from notion_client import Client
from typing import List, Optional, Dict, Any
from .models import DoubanMovie
from .config import config

class NotionAPI:
    """Notion API调用类，用于管理Notion数据库和同步数据"""
    
    def __init__(self):
        """初始化Notion API客户端"""
        self.notion = Client(auth=config.notion_api_key)
        self.database_id = config.notion_database_id
        
    def create_database(self, parent_page_id: str, database_name: str = "豆瓣电影") -> str:
        """
        创建Notion数据库
        
        Args:
            parent_page_id: 父页面ID
            database_name: 数据库名称
            
        Returns:
            数据库ID
        """
        try:
            # 定义数据库属性
            properties = {
                "电影名称": {
                    "title": {}
                },
                "原始名称": {
                    "rich_text": {}
                },
                "豆瓣ID": {
                    "rich_text": {}
                },
                "状态": {
                    "select": {
                        "options": [
                            {"name": "已看", "color": "green"},
                            {"name": "想看", "color": "blue"},
                            {"name": "在看", "color": "yellow"}
                        ]
                    }
                },
                "评分": {
                    "number": {
                        "format": "number"
                    }
                },
                "上映年份": {
                    "number": {
                        "format": "number"
                    }
                },
                "类型": {
                    "multi_select": {
                        "options": []
                    }
                },
                "导演": {
                    "rich_text": {}
                },
                "演员": {
                    "rich_text": {}
                },
                "地区": {
                    "multi_select": {
                        "options": []
                    }
                },
                "上映日期": {
                    "date": {}
                },
                "时长": {
                    "number": {
                        "format": "number"
                    }
                },
                "豆瓣链接": {
                    "url": {}
                },
                "海报": {
                    "files": {}
                },
                "简介": {
                    "rich_text": {}
                },
                "用户评论": {
                    "rich_text": {}
                },
                "评分日期": {
                    "date": {}
                }
            }
            
            # 创建数据库
            database = self.notion.databases.create(
                parent={"type": "page_id", "page_id": parent_page_id},
                title=[{"type": "text", "text": {"content": database_name}}],
                properties=properties
            )
            
            return database["id"]
            
        except Exception as e:
            print(f"创建Notion数据库失败: {e}")
            raise
    
    def query_database(self, filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        查询Notion数据库
        
        Args:
            filter: 查询过滤器
            
        Returns:
            查询结果列表
        """
        try:
            results = []
            start_cursor = None
            
            # 处理分页
            while True:
                response = self.notion.databases.query(
                    database_id=self.database_id,
                    filter=filter,
                    start_cursor=start_cursor
                )
                
                results.extend(response.get("results", []))
                
                if not response.get("has_more"):
                    break
                
                start_cursor = response.get("next_cursor")
            
            return results
            
        except Exception as e:
            print(f"查询Notion数据库失败: {e}")
            raise
    
    def add_movie_to_database(self, movie: DoubanMovie) -> Dict[str, Any]:
        """
        将电影添加到Notion数据库
        
        Args:
            movie: 豆瓣电影对象
            
        Returns:
            添加结果
        """
        try:
            # 转换状态为中文
            status_mapping = {
                "watched": "已看",
                "wish": "想看",
                "do": "在看"
            }
            
            # 构建页面属性
            properties = {
                "电影名称": {
                    "title": [
                        {
                            "text": {
                                "content": movie.title
                            }
                        }
                    ]
                },
                "原始名称": {
                    "rich_text": [
                        {
                            "text": {
                                "content": movie.original_title
                            }
                        }
                    ]
                },
                "豆瓣ID": {
                    "rich_text": [
                        {
                            "text": {
                                "content": movie.id
                            }
                        }
                    ]
                },
                "状态": {
                    "select": {
                        "name": status_mapping.get(movie.status, "已看")
                    }
                },
                "评分": {
                    "number": movie.rating
                },
                "上映年份": {
                    "number": int(movie.year) if movie.year.isdigit() else None
                },
                "类型": {
                    "multi_select": [
                        {"name": genre}
                        for genre in movie.genres
                    ]
                },
                "导演": {
                    "rich_text": [
                        {
                            "text": {
                                "content": ", ".join(movie.directors)
                            }
                        }
                    ]
                },
                "演员": {
                    "rich_text": [
                        {
                            "text": {
                                "content": ", ".join(movie.casts)
                            }
                        }
                    ]
                },
                "地区": {
                    "multi_select": [
                        {"name": region}
                        for region in movie.regions
                    ]
                },
                "时长": {
                    "number": int(movie.duration) if isinstance(movie.duration, (int, str)) and str(movie.duration).isdigit() else None
                },
                "豆瓣链接": {
                    "url": movie.url
                },
                "简介": {
                    "rich_text": [
                        {
                            "text": {
                                "content": movie.summary
                            }
                        }
                    ]
                }
            }
            
            # 处理可选属性
            if movie.release_date:
                properties["上映日期"] = {
                    "date": {
                        "start": movie.release_date
                    }
                }
            
            if movie.comment:
                properties["用户评论"] = {
                    "rich_text": [
                        {
                            "text": {
                                "content": movie.comment
                            }
                        }
                    ]
                }
            
            if movie.rating_date:
                properties["评分日期"] = {
                    "date": {
                        "start": movie.rating_date
                    }
                }
            
            if movie.poster_url:
                properties["海报"] = {
                    "files": [
                        {
                            "type": "external",
                            "name": f"{movie.title}海报",
                            "external": {
                                "url": movie.poster_url
                            }
                        }
                    ]
                }
            
            # 创建页面
            page = self.notion.pages.create(
                parent={"type": "database_id", "database_id": self.database_id},
                properties=properties
            )
            
            return page
            
        except Exception as e:
            print(f"添加电影到Notion数据库失败: {e}")
            raise
    
    def update_movie_in_database(self, page_id: str, movie: DoubanMovie) -> Dict[str, Any]:
        """
        更新Notion数据库中的电影
        
        Args:
            page_id: 页面ID
            movie: 豆瓣电影对象
            
        Returns:
            更新结果
        """
        try:
            # 复用添加逻辑的属性构建
            add_result = self.add_movie_to_database(movie)
            return add_result
            
        except Exception as e:
            print(f"更新电影到Notion数据库失败: {e}")
            raise
    
    def get_movie_by_douban_id(self, douban_id: str) -> Optional[Dict[str, Any]]:
        """
        根据豆瓣ID查询电影
        
        Args:
            douban_id: 豆瓣电影ID
            
        Returns:
            查询结果或None
        """
        try:
            filter = {
                "property": "豆瓣ID",
                "rich_text": {
                    "equals": douban_id
                }
            }
            
            results = self.query_database(filter)
            return results[0] if results else None
            
        except Exception as e:
            print(f"根据豆瓣ID查询电影失败: {e}")
            return None
