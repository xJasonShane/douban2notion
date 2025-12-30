import os
from dotenv import load_dotenv

class Config:
    """配置管理类，用于加载和验证环境变量"""

    def __init__(self):
        load_dotenv()

        self.douban_user_id = self._get_env_var("DOUBAN_USER_ID")
        self.notion_api_key = self._get_env_var("NOTION_API_KEY")
        self.notion_database_id = os.getenv("NOTION_DATABASE_ID", "")
        self.notion_parent_page_id = os.getenv("NOTION_PARENT_PAGE_ID", "")

        self.sync_status = self._get_env_var("SYNC_STATUS", default="watched")

        if self.sync_status not in ["watched", "wish", "do"]:
            raise ValueError(f"Invalid SYNC_STATUS: {self.sync_status}, must be one of: watched, wish, do")

        self.incremental_sync = os.getenv("INCREMENTAL_SYNC", "false").lower() == "true"

    def _get_env_var(self, var_name, default=None):
        """获取环境变量，如果不存在且没有默认值则抛出异常"""
        value = os.getenv(var_name, default)
        if value is None:
            raise EnvironmentError(f"Environment variable {var_name} is not set")
        return value

    def is_database_configured(self):
        """检查数据库是否已配置"""
        return bool(self.notion_database_id)

config = Config()
