import asyncio
import aiohttp
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.news import NewsArticle, Base
from nlp.processor import EnhancedNewsProcessor
from crawler.news_fetcher import AsyncNewsFetcher
from config import Config
import datetime


class AsyncNewsMonitoringSystem:
    def __init__(self):
        # 初始化数据库
        self.engine = create_engine(Config.DATABASE_URL)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

        # 初始化组件
        self.processor = EnhancedNewsProcessor()
        self.news_fetcher = AsyncNewsFetcher()

        # 初始化调度器
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(
            self.run_monitoring_cycle,
            'interval',
            minutes=Config.CRAWL_INTERVAL_MINUTES
        )

    async def run_monitoring_cycle(self):
        """运行监控周期"""
        print(f"{datetime.datetime.now()} - 开始监控周期...")

        try:
            # 获取新闻
            news_items = await self.news_fetcher.fetch_news()
            print(f"获取到 {len(news_items)} 条新闻")

            # 处理新闻
            processed_items = []
            for item in news_items:
                processed = await self.processor.process_news_async(item)
                processed_items.append(processed)

                # 保存到数据库
                await self.save_to_database(processed)

                # 更新上下文
                self.processor.update_context(processed)

                # 检查是否为黑天鹅事件
                if processed['is_black_swan']:
                    await self.alert_black_swan(processed)

            print(f"处理完成，发现 {sum(1 for item in processed_items if item['is_black_swan'])} 条黑天鹅事件")

        except Exception as e:
            print(f"监控周期执行失败: {e}")

    async def save_to_database(self, news_data: Dict):
        """保存到数据库"""
        session = self.Session()
        try:
            article = NewsArticle(
                title=news_data['title'],
                content=news_data['content'][:5000],  # 限制内容长度
                url=news_data['url'],
                source=news_data['source'],
                published_at=news_data.get('published_at'),
                sentiment_score=news_data['gpt_analysis'].get('sentiment', 0),
                black_swan_score=news_data['final_black_swan_score'],
                is_black_swan=1 if news_data['is_black_swan'] else 0,
                categories=','.join(news_data['gpt_analysis'].get('impact_areas', [])),
                risk_level=news_data['gpt_analysis'].get('risk_level', 'unknown')
            )

            session.add(article)
            session.commit()

        except Exception as e:
            session.rollback()
            print(f"保存到数据库失败: {e}")
        finally:
            session.close()

    async def alert_black_swan(self, news_data: Dict):
        """黑天鹅事件警报"""
        print(f"🚨🚨🚨 黑天鹅事件警报 🚨🚨🚨")
        print(f"标题: {news_data['title']}")
        print(f"评分: {news_data['final_black_swan_score']:.3f}")
        print(f"置信度: {news_data['gpt_analysis'].get('confidence_score', 0):.3f}")
        print(f"风险等级: {news_data['gpt_analysis'].get('risk_level', 'unknown')}")
        print(f"理由: {news_data['gpt_analysis'].get('reasoning', '')[:200]}...")
        print(f"链接: {news_data['url']}")
        print("-" * 80)

        # 这里可以集成邮件、Slack、Webhook等警报方式
        # await self.send_slack_alert(news_data)
        # await self.send_email_alert(news_data)

    def start(self):
        """启动系统"""
        self.scheduler.start()
        print("异步新闻监控系统已启动...")

        # 立即运行一次
        asyncio.create_task(self.run_monitoring_cycle())

        try:
            # 保持事件循环运行
            loop = asyncio.get_event_loop()
            loop.run_forever()
        except KeyboardInterrupt:
            self.scheduler.shutdown()
            print("系统已停止")


if __name__ == "__main__":
    system = AsyncNewsMonitoringSystem()
    system.start()