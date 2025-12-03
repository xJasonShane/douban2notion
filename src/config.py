import os
from dotenv import load_dotenv

class Config:
    """配置管理类，用于加载和验证环境变量"""
    
    def __init__(self):
        # 加载.env文件中的环境变量
        load_dotenv()
        
        # 豆瓣API配置
        self.douban_user_id = self._get_env_var("DOUBAN_USER_ID")
        self.douban_api_key = self._get_env_var("DOUBAN_API_KEY")
        
        # Notion API配置
        self.notion_api_key = self._get_env_var("NOTION_API_KEY")
        self.notion_database_id = self._get_env_var("NOTION_DATABASE_ID")
        
        # 同步配置
        self.sync_status = self._get_env_var("SYNC_STATUS", default="watched")
        
        # 验证同步状态值
        if self.sync_status not in ["watched", "wish", "do"]:
            raise ValueError(f"Invalid SYNC_STATUS: {self.sync_status}, must be one of: watched, wish, do")
        
        # 自定义字段配置
        # 所有可用字段
        self.available_fields = [
            "电影名称", "原始名称", "豆瓣ID", "状态", "评分", "上映年份",
            "类型", "导演", "演员", "地区", "上映日期", "时长",
            "豆瓣链接", "海报", "简介", "用户评论", "评分日期"
        ]
        
        # 获取自定义字段列表，默认为所有字段
        custom_fields = self._get_env_var("CUSTOM_FIELDS", default=",".join(self.available_fields))
        self.selected_fields = [field.strip() for field in custom_fields.split(",") if field.strip()]
        
        # 验证字段有效性
        for field in self.selected_fields:
            if field not in self.available_fields:
                raise ValueError(f"Invalid field: {field}, available fields: {', '.join(self.available_fields)}")
        
        # 确保必要字段始终被包含
        required_fields = ["电影名称", "豆瓣ID", "状态"]
        for field in required_fields:
            if field not in self.selected_fields:
                self.selected_fields.append(field)
    
    def _get_env_var(self, var_name, default=None):
        """获取环境变量，如果不存在且没有默认值则抛出异常"""
        value = os.getenv(var_name, default)
        if value is None:
            raise EnvironmentError(f"Environment variable {var_name} is not set")
        return value

# 创建配置实例
config = Config()
