import os
from dotenv import load_dotenv

def setup_config():
    """交互式配置向导"""
    print("="*60)
    print("豆瓣电影同步到Notion - 配置向导")
    print("="*60)
    print()

    env_vars = {}

    print("请输入以下配置信息:")
    print("-"*60)

    env_vars["DOUBAN_USER_ID"] = input("豆瓣用户名(例如: https://movie.douban.com/people/username/ 中的username): ").strip()

    env_vars["NOTION_API_KEY"] = input("Notion集成密钥(secret_开头的字符串): ").strip()

    print("\n请选择数据库配置方式:")
    print("1. 使用现有数据库(需要数据库ID)")
    print("2. 自动创建新数据库(需要父页面ID)")
    choice = input("请输入选择(1或2): ").strip()

    if choice == "1":
        env_vars["NOTION_DATABASE_ID"] = input("Notion数据库ID(32位字符): ").strip()
        env_vars["NOTION_PARENT_PAGE_ID"] = ""
    else:
        env_vars["NOTION_DATABASE_ID"] = ""
        env_vars["NOTION_PARENT_PAGE_ID"] = input("Notion父页面ID(32位字符): ").strip()

    print("\n请选择要同步的电影状态:")
    print("1. 已看电影")
    print("2. 想看电影")
    print("3. 在看电影")
    status_choice = input("请输入选择(1/2/3, 默认1): ").strip() or "1"

    status_map = {"1": "watched", "2": "wish", "3": "do"}
    env_vars["SYNC_STATUS"] = status_map.get(status_choice, "watched")

    incremental = input("是否启用增量同步(只同步新电影)? (y/n, 默认n): ").strip().lower()
    env_vars["INCREMENTAL_SYNC"] = "true" if incremental == "y" else "false"

    print("\n" + "="*60)
    print("配置预览:")
    print("="*60)
    for key, value in env_vars.items():
        if value:
            if "API_KEY" in key or "ID" in key:
                display_value = value[:8] + "..." if len(value) > 8 else value
            else:
                display_value = value
            print(f"{key}: {display_value}")
    print("="*60)

    confirm = input("\n确认保存配置? (y/n): ").strip().lower()
    if confirm == "y":
        with open(".env", "w", encoding="utf-8") as f:
            for key, value in env_vars.items():
                if value:
                    f.write(f"{key}={value}\n")
        print("\n✅ 配置已保存到 .env 文件")
        print("\n下一步:")
        print("1. 如果选择自动创建数据库，请确保Notion集成已添加到父页面")
        print("2. 运行 'python main.py' 开始同步")
    else:
        print("\n配置已取消")

if __name__ == "__main__":
    setup_config()
