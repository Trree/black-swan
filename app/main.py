import asyncio
import datetime
from typing import List, Dict

from config import config
from logging_config import logger
from scheduler.task_scheduler import task_scheduler
from services.news_crawler_service import crawler_service
from nlp.processor import EnhancedNewsProcessor
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class NewsMonitorApp:
    def __init__(self):
        # 初始化数据库
        self.engine = create_engine(config.DATABASE_URL)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

        # 初始化处理器
        self.processor = EnhancedNewsProcessor()

        # 注册定时任务
        self._register_tasks()

    def _register_tasks(self):
        """注册所有定时任务"""
        # 主要抓取任务 - 每30分钟
        task_scheduler.add_interval_job(
            self.main_crawl_task,
            config.CRAWL_INTERVAL_MINUTES,
            'main_crawl_task'
        )

        # 快速检查任务 - 每5分钟（只在工作时间）
        task_scheduler.add_daily_time_range_job(
            self.quick_check_task,
            config.WORKING_HOURS['start'],
            config.WORKING_HOURS['end'],
            config.QUICK_CHECK_INTERVAL_MINUTES,
            'quick_check_task'
        )

        # 每日清理任务 - 凌晨2点
        task_scheduler.add_cron_job(
            self.daily_cleanup_task,
            '0 2 * * *',
            'daily_cleanup_task'
        )

        # 状态报告任务 - 每小时
        task_scheduler.add_interval_job(
            self.status_report_task,
            60,
            'status_report_task'
        )

    async def main_crawl_task(self):
        """主要抓取任务"""
        logger.info("开始执行主要抓取任务...")

        try:
            # 抓取新闻
            news_items = await crawler_service.crawl_all_sources()
            logger.info(f"抓取到 {len(news_items)} 条新闻")

            # 处理新闻
            processed_count = 0
            black_swan_count = 0

            for item in news_items:
                try:
                    processed = await self.processor.process_news_async(item)
                    await self._save_news_item(processed)

                    processed_count += 1
                    if processed['is_black_swan']:
                        black_swan_count += 1
                        await self._alert_black_swan(processed)

                except Exception as e:
                    logger.error(f"处理新闻失败: {e}")

            logger.info(f"处理完成: {processed_count} 条新闻, {black_swan_count} 条黑天鹅事件")

        except Exception as e:
            logger.error(f"主要抓取任务执行失败: {e}")

    async def quick_check_task(self):
        """快速检查任务"""
        logger.debug("执行快速检查任务...")
        # 可以实现增量检查或者重点源检查
        # 这里可以只检查高优先级的新闻源

    async def daily_cleanup_task(self):
        """每日清理任务"""
        logger.info("执行每日清理任务...")
        # 清理旧数据、优化数据库等

    async def status_report_task(self):
        """状态报告任务"""
        # 生成系统状态报告
        session = self.Session()
        try:
            total_news = session.query(NewsArticle).count()
            black_swan_news = session.query(NewsArticle).filter_by(is_black_swan=1).count()

            logger.info(f"系统状态 - 总新闻: {total_news}, 黑天鹅事件: {black_swan_news}")

        except Exception as e:
            logger.error(f"状态报告生成失败: {e}")
        finally:
            session.close()

    async def _save_news_item(self, news_data: Dict):
        """保存新闻到数据库"""
        session = self.Session()
        try:
            article = NewsArticle(
                title=news_data['title'],
                content=news_data['content'][:5000],
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
            logger.debug(f"保存新闻: {news_data['title'][:50]}...")

        except Exception as e:
            session.rollback()
            logger.error(f"保存新闻到数据库失败: {e}")
        finally:
            session.close()

    async def _alert_black_swan(self, news_data: Dict):
        """黑天鹅事件警报"""
        logger.warning(f"🚨 黑天鹅事件警报 🚨")
        logger.warning(f"标题: {news_data['title']}")
        logger.warning(f"评分: {news_data['final_black_swan_score']:.3f}")
        logger.warning(f"链接: {news_data['url']}")

        # 这里可以集成各种警报方式
        # await self._send_email_alert(news_data)
        # await self._send_slack_alert(news_data)

    def run(self):
        """运行应用"""
        logger.info("新闻监控应用启动中...")
        logger.info(f"数据库: {config.DATABASE_URL}")
        logger.info(f"抓取间隔: {config.CRAWL_INTERVAL_MINUTES} 分钟")
        logger.info(f"新闻源数量: {len(config.NEWS_SOURCES)}")

        # 启动调度器
        task_scheduler.start()


# 应用启动
if __name__ == "__main__":
    # 创建事件循环
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        app = NewsMonitorApp()
        app.run()
    except KeyboardInterrupt:
        logger.info("应用被用户中断")
    except Exception as e:
        logger.error(f"应用启动失败: {e}")
    finally:
        # 清理资源
        loop.run_until_complete(crawler_service.close_session())
        loop.close()