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
    
    def _get_env_var(self, var_name, default=None):
        """获取环境变量，如果不存在且没有默认值则抛出异常"""
        value = os.getenv(var_name, default)
        if value is None:
            raise EnvironmentError(f"Environment variable {var_name} is not set")
        return value

# 创建配置实例
config = Config()
