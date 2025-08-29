import time
from typing import Callable, Dict, Any

from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from logging_config import logger


class NewsTaskScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler({
            'apscheduler.job_defaults.coalesce': 'true',
            'apscheduler.job_defaults.max_instances': '3'
        })
        self.jobs = {}
        self._setup_event_listeners()

    def _setup_event_listeners(self):
        """设置调度器事件监听"""
        self.scheduler.add_listener(
            self._on_job_executed,
            EVENT_JOB_EXECUTED | EVENT_JOB_ERROR
        )

    def _on_job_executed(self, event):
        """任务执行回调"""
        job_id = event.job_id
        if event.exception:
            logger.error(f"任务 {job_id} 执行失败: {event.exception}")
        else:
            logger.debug(f"任务 {job_id} 执行完成")

    def add_interval_job(self,
                         func: Callable,
                         interval_minutes: int,
                         job_id: str,
                         args: tuple = None,
                         kwargs: Dict[str, Any] = None) -> None:
        """添加间隔任务"""
        trigger = IntervalTrigger(minutes=interval_minutes)
        self.scheduler.add_job(
            func,
            trigger,
            id=job_id,
            args=args,
            kwargs=kwargs,
            replace_existing=True
        )
        logger.info(f"添加间隔任务: {job_id}, 间隔: {interval_minutes}分钟")

    def add_cron_job(self,
                     func: Callable,
                     cron_expression: str,
                     job_id: str,
                     args: tuple = None,
                     kwargs: Dict[str, Any] = None) -> None:
        """添加Cron表达式任务"""
        trigger = CronTrigger.from_crontab(cron_expression)
        self.scheduler.add_job(
            func,
            trigger,
            id=job_id,
            args=args,
            kwargs=kwargs,
            replace_existing=True
        )
        logger.info(f"添加Cron任务: {job_id}, 表达式: {cron_expression}")

    def add_daily_time_range_job(self,
                                 func: Callable,
                                 start_time: str,
                                 end_time: str,
                                 interval_minutes: int,
                                 job_id: str,
                                 args: tuple = None,
                                 kwargs: Dict[str, Any] = None) -> None:
        """添加每日时间范围内的间隔任务"""
        # 这里需要更复杂的逻辑来处理时间范围
        # 简化实现：使用Cron表达式限制运行时间
        hour_range = f"{start_time.split(':')[0]}-{end_time.split(':')[0]}"
        cron_expression = f"*/{interval_minutes} {hour_range} * * *"

        self.add_cron_job(func, cron_expression, job_id, args, kwargs)

    def start(self) -> None:
        """启动调度器"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("任务调度器已启动")

            # 保持主线程运行
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.shutdown()

    def shutdown(self) -> None:
        """关闭调度器"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("任务调度器已关闭")

    def get_job_status(self) -> Dict:
        """获取任务状态"""
        status = {}
        for job in self.scheduler.get_jobs():
            status[job.id] = {
                'next_run_time': job.next_run_time,
                'trigger': str(job.trigger)
            }
        return status


# 全局调度器实例
task_scheduler = NewsTaskScheduler()