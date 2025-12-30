import os
import sys
from dotenv import load_dotenv

def test_config():
    """测试配置是否正确"""
    print("="*60)
    print("配置测试")
    print("="*60)

    load_dotenv()

    required_vars = ["DOUBAN_USER_ID", "NOTION_API_KEY"]
    missing_vars = []

    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            display_value = value[:8] + "..." if len(value) > 8 else value
            print(f"✅ {var}: {display_value}")

    if missing_vars:
        print(f"\n❌ 缺少以下配置: {', '.join(missing_vars)}")
        return False

    db_id = os.getenv("NOTION_DATABASE_ID")
    parent_id = os.getenv("NOTION_PARENT_PAGE_ID")

    if not db_id and not parent_id:
        print("\n⚠️  警告: 未配置NOTION_DATABASE_ID或NOTION_PARENT_PAGE_ID")
        print("程序将尝试自动创建数据库")
    elif db_id:
        print(f"✅ NOTION_DATABASE_ID: {db_id[:8]}...")
    elif parent_id:
        print(f"✅ NOTION_PARENT_PAGE_ID: {parent_id[:8]}...")

    sync_status = os.getenv("SYNC_STATUS", "watched")
    print(f"✅ SYNC_STATUS: {sync_status}")

    incremental = os.getenv("INCREMENTAL_SYNC", "false")
    print(f"✅ INCREMENTAL_SYNC: {incremental}")

    print("\n✅ 配置测试通过!")
    return True

def test_douban_connection():
    """测试豆瓣连接"""
    print("\n" + "="*60)
    print("豆瓣连接测试")
    print("="*60)

    try:
        from src.douban_api import DoubanAPI
        from src.config import config

        api = DoubanAPI()
        print(f"✅ 豆瓣用户名: {config.douban_user_id}")

        print("正在获取已看电影列表（前5部）...")
        movies = api.get_watched_movies()[:5]

        if movies:
            print(f"✅ 成功获取 {len(movies)} 部电影")
            for movie in movies[:3]:
                print(f"   - {movie.title} ({movie.year})")
        else:
            print("⚠️  未找到电影，可能是用户名错误或没有已看电影")

        return True

    except Exception as e:
        print(f"❌ 豆瓣连接测试失败: {e}")
        return False

def test_notion_connection():
    """测试Notion连接"""
    print("\n" + "="*60)
    print("Notion连接测试")
    print("="*60)

    try:
        from src.notion_api import NotionAPI
        from src.config import config

        api = NotionAPI()

        if config.is_database_configured():
            print(f"✅ 数据库ID: {config.notion_database_id[:8]}...")
            print("正在查询数据库...")
            results = api.query_database()
            print(f"✅ 数据库中现有 {len(results)} 条记录")
        else:
            print("⚠️  未配置数据库ID，将测试创建数据库功能")
            if config.notion_parent_page_id:
                print(f"✅ 父页面ID: {config.notion_parent_page_id[:8]}...")
                print("提示: 首次运行时将自动创建数据库")

        return True

    except Exception as e:
        print(f"❌ Notion连接测试失败: {e}")
        return False

def run_all_tests():
    """运行所有测试"""
    print("\n🧪 开始运行测试...\n")

    results = {
        "配置测试": test_config(),
        "豆瓣连接测试": test_douban_connection(),
        "Notion连接测试": test_notion_connection()
    }

    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)

    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")

    all_passed = all(results.values())

    if all_passed:
        print("\n🎉 所有测试通过! 可以开始同步了")
        print("运行 'python main.py' 开始同步")
    else:
        print("\n⚠️  部分测试失败，请检查配置后重试")

    return all_passed

if __name__ == "__main__":
    run_all_tests()
