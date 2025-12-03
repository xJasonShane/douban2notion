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
        
        # 定义所有可用的数据库属性模板
        self.all_properties = {
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
            # 根据配置的字段动态生成属性
            properties = {}
            for field in config.selected_fields:
                if field in self.all_properties:
                    properties[field] = self.all_properties[field]
            
            # 创建数据库
            database = self.notion.databases.create(
                parent={"type": "page_id", "page_id": parent_page_id},
                title=[{"type": "text", "text": {"content": database_name}}],
                properties=properties
            )
            
            # 设置画廊视图
            self.set_gallery_view(database["id"])
            
            return database["id"]
            
        except Exception as e:
            print(f"创建Notion数据库失败: {e}")
            raise
    
    def set_gallery_view(self, database_id: str):
        """
        设置Notion数据库的画廊视图
        
        Args:
            database_id: 数据库ID
        """
        try:
            # 获取数据库的当前视图
            database = self.notion.databases.retrieve(database_id=database_id)
            
            # 创建新的画廊视图
            gallery_view = self.notion.request(
                path="databases/{}/views".format(database_id),
                method="POST",
                body={
                    "parent": {"type": "database_id", "database_id": database_id},
                    "title": [{"type": "text", "text": {"content": "画廊视图"}}],
                    "type": "gallery",
                    "gallery": {
                        "properties": [],
                        "cover": {
                            "type": "property",
                            "property": "海报"
                        },
                        "page_size": 30
                    }
                }
            )
            
            # 将画廊视图设置为默认视图
            # 注意：Notion API 目前不支持直接设置默认视图
            # 可以考虑删除其他视图，只保留画廊视图
            # 或者让用户手动设置默认视图
            
        except Exception as e:
            print(f"设置画廊视图失败: {e}")
            # 非致命错误，继续执行
            pass
    
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
                # 使用正确的API调用方式
                response = self.notion.request(
                    path="databases/{}/query".format(self.database_id),
                    method="POST",
                    body={
                        "filter": filter,
                        "start_cursor": start_cursor
                    }
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
            properties = {}
            
            # 根据配置的字段动态生成属性
            if "电影名称" in config.selected_fields:
                properties["电影名称"] = {
                    "title": [
                        {
                            "text": {
                                "content": movie.title
                            }
                        }
                    ]
                }
            
            if "原始名称" in config.selected_fields:
                properties["原始名称"] = {
                    "rich_text": [
                        {
                            "text": {
                                "content": movie.original_title
                            }
                        }
                    ]
                }
            
            if "豆瓣ID" in config.selected_fields:
                properties["豆瓣ID"] = {
                    "rich_text": [
                        {
                            "text": {
                                "content": movie.id
                            }
                        }
                    ]
                }
            
            if "状态" in config.selected_fields:
                properties["状态"] = {
                    "select": {
                        "name": status_mapping.get(movie.status, "已看")
                    }
                }
            
            if "评分" in config.selected_fields:
                properties["评分"] = {
                    "number": movie.rating
                }
            
            if "上映年份" in config.selected_fields:
                properties["上映年份"] = {
                    "number": int(movie.year) if movie.year.isdigit() else None
                }
            
            if "类型" in config.selected_fields:
                properties["类型"] = {
                    "multi_select": [
                        {"name": genre}
                        for genre in movie.genres
                    ]
                }
            
            if "导演" in config.selected_fields:
                properties["导演"] = {
                    "rich_text": [
                        {
                            "text": {
                                "content": ", ".join(movie.directors)
                            }
                        }
                    ]
                }
            
            if "演员" in config.selected_fields:
                properties["演员"] = {
                    "rich_text": [
                        {
                            "text": {
                                "content": ", ".join(movie.casts)
                            }
                        }
                    ]
                }
            
            if "地区" in config.selected_fields:
                properties["地区"] = {
                    "multi_select": [
                        {"name": region}
                        for region in movie.regions
                    ]
                }
            
            if "时长" in config.selected_fields:
                properties["时长"] = {
                    "number": int(movie.duration) if isinstance(movie.duration, (int, str)) and str(movie.duration).isdigit() else None
                }
            
            if "豆瓣链接" in config.selected_fields:
                properties["豆瓣链接"] = {
                    "url": movie.url
                }
            
            if "简介" in config.selected_fields:
                properties["简介"] = {
                    "rich_text": [
                        {
                            "text": {
                                "content": movie.summary
                            }
                        }
                    ]
                }
            
            # 处理可选属性
            if "上映日期" in config.selected_fields and movie.release_date:
                properties["上映日期"] = {
                    "date": {
                        "start": movie.release_date
                    }
                }
            
            if "用户评论" in config.selected_fields and movie.comment:
                properties["用户评论"] = {
                    "rich_text": [
                        {
                            "text": {
                                "content": movie.comment
                            }
                        }
                    ]
                }
            
            if "评分日期" in config.selected_fields and movie.rating_date:
                properties["评分日期"] = {
                    "date": {
                        "start": movie.rating_date
                    }
                }
            
            if "海报" in config.selected_fields and movie.poster_url:
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
            # 转换状态为中文
            status_mapping = {
                "watched": "已看",
                "wish": "想看",
                "do": "在看"
            }
            
            # 构建页面属性
            properties = {}
            
            # 根据配置的字段动态生成属性
            if "电影名称" in config.selected_fields:
                properties["电影名称"] = {
                    "title": [
                        {
                            "text": {
                                "content": movie.title
                            }
                        }
                    ]
                }
            
            if "原始名称" in config.selected_fields:
                properties["原始名称"] = {
                    "rich_text": [
                        {
                            "text": {
                                "content": movie.original_title
                            }
                        }
                    ]
                }
            
            if "豆瓣ID" in config.selected_fields:
                properties["豆瓣ID"] = {
                    "rich_text": [
                        {
                            "text": {
                                "content": movie.id
                            }
                        }
                    ]
                }
            
            if "状态" in config.selected_fields:
                properties["状态"] = {
                    "select": {
                        "name": status_mapping.get(movie.status, "已看")
                    }
                }
            
            if "评分" in config.selected_fields:
                properties["评分"] = {
                    "number": movie.rating
                }
            
            if "上映年份" in config.selected_fields:
                properties["上映年份"] = {
                    "number": int(movie.year) if movie.year.isdigit() else None
                }
            
            if "类型" in config.selected_fields:
                properties["类型"] = {
                    "multi_select": [
                        {"name": genre}
                        for genre in movie.genres
                    ]
                }
            
            if "导演" in config.selected_fields:
                properties["导演"] = {
                    "rich_text": [
                        {
                            "text": {
                                "content": ", ".join(movie.directors)
                            }
                        }
                    ]
                }
            
            if "演员" in config.selected_fields:
                properties["演员"] = {
                    "rich_text": [
                        {
                            "text": {
                                "content": ", ".join(movie.casts)
                            }
                        }
                    ]
                }
            
            if "地区" in config.selected_fields:
                properties["地区"] = {
                    "multi_select": [
                        {"name": region}
                        for region in movie.regions
                    ]
                }
            
            if "时长" in config.selected_fields:
                properties["时长"] = {
                    "number": int(movie.duration) if isinstance(movie.duration, (int, str)) and str(movie.duration).isdigit() else None
                }
            
            if "豆瓣链接" in config.selected_fields:
                properties["豆瓣链接"] = {
                    "url": movie.url
                }
            
            if "简介" in config.selected_fields:
                properties["简介"] = {
                    "rich_text": [
                        {
                            "text": {
                                "content": movie.summary
                            }
                        }
                    ]
                }
            
            # 处理可选属性
            if "上映日期" in config.selected_fields and movie.release_date:
                properties["上映日期"] = {
                    "date": {
                        "start": movie.release_date
                    }
                }
            
            if "用户评论" in config.selected_fields and movie.comment:
                properties["用户评论"] = {
                    "rich_text": [
                        {
                            "text": {
                                "content": movie.comment
                            }
                        }
                    ]
                }
            
            if "评分日期" in config.selected_fields and movie.rating_date:
                properties["评分日期"] = {
                    "date": {
                        "start": movie.rating_date
                    }
                }
            
            if "海报" in config.selected_fields and movie.poster_url:
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
            
            # 更新页面
            page = self.notion.pages.update(
                page_id=page_id,
                properties=properties
            )
            
            return page
            
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
