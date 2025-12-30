from src.sync_service import SyncService

if __name__ == "__main__":
    try:
        sync_service = SyncService()
        sync_result = sync_service.sync_movies()

        print(f"\n🎉 电影同步已完成!")
        print(f"📊 同步统计:")
        print(f"   总处理电影数: {sync_result['total']}")
        print(f"   新增电影数: {sync_result['added']}")
        print(f"   更新电影数: {sync_result['updated']}")
        print(f"   失败电影数: {sync_result['failed']}")

    except Exception as e:
        print(f"\n❌ 同步过程中发生错误: {e}")
        print("请检查配置和网络连接后重试")
        raise
