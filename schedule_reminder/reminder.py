# from apscheduler.schedulers.asyncio import AsyncIOScheduler
# import pytz
# from database.databse import praying_repo
# from datetime import datetime
# import logging
#
# logging.basicConfig(level=logging.INFO)
#
# scheduler = AsyncIOScheduler()
# #
# # def schedule_reminder(user_id, prayer_times):
# #     """Schedules prayer reminders for a user."""
# #     user_timezone = "Asia/Tashkent"  # Replace with actual DB timezone retrieval
# #     timezone = pytz.timezone(user_timezone)
# #
# #     for prayer, time in prayer_times.items():
# #         if prayer in ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]:
# #             hour, minute = map(int, time.split(':'))
# #             hour = 13
# #             minute = 22
# #
# #             logging.info(f"Scheduling {prayer} for User {user_id} at {hour}:{minute}")
# #
# #             scheduler.add_job(
# #                 send_reminder,
# #                 'cron',
# #                 hour=hour,
# #                 minute=minute,
# #                 timezone=timezone,
# #                 args=[user_id, prayer, bot]
# #             )
# #
# #     if not scheduler.running:  # Start scheduler if not already running
# #         logging.info("Starting APScheduler...")
# #         scheduler.start()
# #
# # async def send_reminder(user_id, prayer, bot):
# #     """Send prayer reminder message."""
# #     logging.info(f"Sending reminder to User {user_id} for {prayer}")
# #     await bot.send_message(user_id, f"📢 {prayer} namoz vaqti keldi! 🕌 (Время {prayer} наступило!)")
