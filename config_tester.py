#!/usr/bin/env python3
"""
کانفیگ یاب حرفه‌ای - Config Tester
سیستم تست سرعت و پینگ کانفیگ‌ها
"""

import asyncio
import aiohttp
import socket
import time
import subprocess
import platform
import threading
from typing import List, Dict, Optional, Tuple, Callable
from dataclasses import dataclass
from datetime import datetime
import logging

from config_core import ConfigResult

logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """نتیجه تست یک کانفیگ"""
    config_id: int
    ping: Optional[float] = None
    download_speed: Optional[float] = None
    upload_speed: Optional[float] = None
    success_rate: float = 0.0
    response_time: Optional[float] = None
    status: str = "untested"
    error_message: Optional[str] = None
    test_time: datetime = None
    
    def __post_init__(self):
        if self.test_time is None:
            self.test_time = datetime.now()

class PingTester:
    """کلاس برای تست پینگ"""
    
    @staticmethod
    async def ping_host(host: str, timeout: float = 5.0, count: int = 4) -> Optional[float]:
        """تست پینگ به یک هاست"""
        try:
            # تشخیص سیستم عامل
            system = platform.system().lower()
            
            if system == "windows":
                cmd = ["ping", "-n", str(count), "-w", str(int(timeout * 1000)), host]
            else:
                cmd = ["ping", "-c", str(count), "-W", str(int(timeout)), host]
            
            # اجرای دستور ping
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=timeout + 5
            )
            
            if process.returncode != 0:
                logger.warning(f"Ping failed for {host}: {stderr.decode()}")
                return None
            
            output = stdout.decode()
            
            # استخراج زمان پینگ
            if system == "windows":
                # برای ویندوز: Average = 25ms یا time=25ms
                import re
                avg_match = re.search(r'Average = (\d+)ms', output)
                if avg_match:
                    return float(avg_match.group(1))
                
                time_matches = re.findall(r'time[<=](\d+)ms', output)
                if time_matches:
                    return sum(float(t) for t in time_matches) / len(time_matches)
            else:
                # برای لینوکس/مک
                import re
                avg_match = re.search(r'avg/[^/]+/[^/]+/[^/]+ = [^/]+/([^/]+)/', output)
                if avg_match:
                    return float(avg_match.group(1))
            
            return None
            
        except Exception as e:
            logger.error(f"Error pinging {host}: {e}")
            return None
    
    @staticmethod
    async def tcp_ping(host: str, port: int, timeout: float = 5.0) -> Optional[float]:
        """تست اتصال TCP (برای زمانی که ICMP ping کار نمی‌کند)"""
        try:
            start_time = time.time()
            
            # ایجاد socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            
            try:
                # تلاش برای اتصال
                result = sock.connect_ex((host, port))
                end_time = time.time()
                
                if result == 0:
                    # اتصال موفق
                    return (end_time - start_time) * 1000  # تبدیل به میلی‌ثانیه
                else:
                    return None
            finally:
                sock.close()
                
        except Exception as e:
            logger.error(f"TCP ping error for {host}:{port}: {e}")
            return None

class SpeedTester:
    """کلاس برای تست سرعت اینترنت"""
    
    def __init__(self):
        self.test_urls = [
            "http://speedtest.ftp.otenet.gr/files/test1Mb.db",
            "http://speedtest.ftp.otenet.gr/files/test10Mb.db",
            "http://ipv4.download.thinkbroadband.com/1MB.zip",
            "http://ipv4.download.thinkbroadband.com/5MB.zip"
        ]
    
    async def test_download_speed(self, proxy_url: Optional[str] = None, timeout: float = 10.0) -> Optional[float]:
        """تست سرعت دانلود"""
        try:
            # ایجاد connector با پراکسی در صورت نیاز
            connector = None
            if proxy_url:
                connector = aiohttp.ProxyConnector.from_url(proxy_url)
            
            async with aiohttp.ClientSession(
                connector=connector,
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as session:
                
                # انتخاب فایل تست (شروع با فایل کوچک)
                test_url = self.test_urls[0]  # 1MB file
                
                start_time = time.time()
                downloaded_bytes = 0
                
                async with session.get(test_url) as response:
                    if response.status != 200:
                        return None
                    
                    async for chunk in response.content.iter_chunked(8192):
                        downloaded_bytes += len(chunk)
                        
                        # اگر بیش از timeout گذشت، متوقف کن
                        if time.time() - start_time > timeout:
                            break
                
                end_time = time.time()
                duration = end_time - start_time
                
                if duration > 0:
                    # محاسبه سرعت به کیلوبایت در ثانیه
                    speed_kbps = (downloaded_bytes / 1024) / duration
                    return speed_kbps
                
                return None
                
        except Exception as e:
            logger.error(f"Download speed test error: {e}")
            return None
    
    async def test_http_response(self, url: str, proxy_url: Optional[str] = None, timeout: float = 10.0) -> Optional[float]:
        """تست زمان پاسخ HTTP"""
        try:
            connector = None
            if proxy_url:
                connector = aiohttp.ProxyConnector.from_url(proxy_url)
            
            async with aiohttp.ClientSession(
                connector=connector,
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as session:
                
                start_time = time.time()
                
                async with session.get(url) as response:
                    # فقط header ها را بخوان
                    await response.read(1)
                    end_time = time.time()
                    
                    return (end_time - start_time) * 1000  # میلی‌ثانیه
                    
        except Exception as e:
            logger.error(f"HTTP response test error: {e}")
            return None

class ConfigTester:
    """کلاس اصلی برای تست کانفیگ‌ها"""
    
    def __init__(self, max_concurrent: int = 10):
        self.ping_tester = PingTester()
        self.speed_tester = SpeedTester()
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
        # URLs برای تست اتصال
        self.test_urls = [
            "https://www.google.com",
            "https://www.cloudflare.com",
            "https://8.8.8.8"
        ]
    
    async def test_single_config(
        self, 
        config: ConfigResult, 
        progress_callback: Optional[Callable] = None
    ) -> TestResult:
        """تست یک کانفیگ منفرد"""
        
        async with self.semaphore:
            result = TestResult(config_id=config.id)
            
            try:
                if progress_callback:
                    await progress_callback(config.id, "شروع تست...")
                
                # مرحله 1: تست پینگ
                if progress_callback:
                    await progress_callback(config.id, "تست پینگ...")
                
                ping_result = await self.ping_tester.ping_host(config.server, timeout=5.0)
                
                if ping_result is None:
                    # اگر ICMP ping کار نکرد، TCP ping امتحان کن
                    ping_result = await self.ping_tester.tcp_ping(config.server, config.port, timeout=5.0)
                
                result.ping = ping_result
                
                if ping_result is None:
                    result.status = "dead"
                    result.error_message = "عدم پاسخ به ping"
                    return result
                
                # مرحله 2: تست زمان پاسخ HTTP
                if progress_callback:
                    await progress_callback(config.id, "تست اتصال...")
                
                response_times = []
                for test_url in self.test_urls[:2]:  # فقط 2 تا برای سرعت
                    response_time = await self.speed_tester.test_http_response(
                        test_url, 
                        timeout=5.0
                    )
                    if response_time:
                        response_times.append(response_time)
                
                if response_times:
                    result.response_time = sum(response_times) / len(response_times)
                    result.success_rate = len(response_times) / len(self.test_urls[:2])
                else:
                    result.response_time = None
                    result.success_rate = 0.0
                
                # تعیین وضعیت بر اساس نتایج
                if result.success_rate == 0:
                    result.status = "dead"
                elif ping_result > 1000 or (result.response_time and result.response_time > 3000):
                    result.status = "slow"
                else:
                    result.status = "active"
                
                if progress_callback:
                    await progress_callback(config.id, f"تست تمام شد - {result.status}")
                
            except Exception as e:
                result.status = "dead"
                result.error_message = str(e)
                logger.error(f"Error testing config {config.id}: {e}")
                
                if progress_callback:
                    await progress_callback(config.id, f"خطا: {str(e)}")
            
            return result
    
    async def test_multiple_configs(
        self, 
        configs: List[ConfigResult], 
        progress_callback: Optional[Callable] = None
    ) -> List[TestResult]:
        """تست چندین کانفیگ به صورت همزمان"""
        
        if not configs:
            return []
        
        logger.info(f"شروع تست {len(configs)} کانفیگ...")
        
        # ایجاد task ها
        tasks = []
        for config in configs:
            task = asyncio.create_task(
                self.test_single_config(config, progress_callback)
            )
            tasks.append(task)
        
        # اجرای همزمان و جمع‌آوری نتایج
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # فیلتر کردن نتایج موفق
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, TestResult):
                valid_results.append(result)
            else:
                logger.error(f"Error in config test {i}: {result}")
                # ایجاد نتیجه خطا
                error_result = TestResult(
                    config_id=configs[i].id,
                    status="dead",
                    error_message=str(result)
                )
                valid_results.append(error_result)
        
        logger.info(f"تست {len(valid_results)} کانفیگ تمام شد")
        return valid_results
    
    def update_configs_with_results(
        self, 
        configs: List[ConfigResult], 
        test_results: List[TestResult]
    ) -> List[ConfigResult]:
        """بروزرسانی کانفیگ‌ها با نتایج تست"""
        
        # ایجاد dictionary برای دسترسی سریع
        results_dict = {result.config_id: result for result in test_results}
        
        updated_configs = []
        for config in configs:
            if config.id in results_dict:
                result = results_dict[config.id]
                config.status = result.status
                config.ping = result.ping
                config.download_speed = result.download_speed
                config.last_tested = result.test_time
            
            updated_configs.append(config)
        
        return updated_configs

# مثال استفاده
async def test_configs_example():
    """مثال تست کانفیگ‌ها"""
    from config_core import ConfigProcessor
    
    # دریافت کانفیگ‌ها
    processor = ConfigProcessor()
    configs = await processor.process_all_sources()
    
    # محدود کردن به 10 کانفیگ اول برای تست
    test_configs = configs[:10]
    
    # تابع callback برای نمایش پیشرفت
    async def progress_callback(config_id: int, message: str):
        print(f"🔄 کانفیگ {config_id}: {message}")
    
    # تست کانفیگ‌ها
    tester = ConfigTester(max_concurrent=5)
    test_results = await tester.test_multiple_configs(test_configs, progress_callback)
    
    # نمایش نتایج
    print("\n📊 نتایج تست:")
    for result in test_results:
        status_emoji = {
            "active": "✅",
            "slow": "⚠️",
            "dead": "❌",
            "untested": "❓"
        }.get(result.status, "❓")
        
        print(f"{status_emoji} کانفیگ {result.config_id}: {result.status}")
        if result.ping:
            print(f"   📡 پینگ: {result.ping:.0f}ms")
        if result.response_time:
            print(f"   🌐 زمان پاسخ: {result.response_time:.0f}ms")
        if result.error_message:
            print(f"   ❗ خطا: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(test_configs_example())
