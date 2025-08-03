#!/usr/bin/env python3
"""
کانفیگ یاب حرفه‌ای - Web API Server
سرور وب برای ارائه API به Frontend
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

try:
    from aiohttp import web, WSMsgType
    from aiohttp.web_response import Response
    from aiohttp.web_request import Request
    import aiohttp_cors
except ImportError:
    print("⚠️  لطفاً ابتدا dependencies را نصب کنید:")
    print("pip install aiohttp aiohttp-cors")
    exit(1)

from config_core import ConfigProcessor, ConfigResult
from config_tester import ConfigTester, TestResult

# تنظیم logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ConfigFinderAPI:
    """کلاس اصلی API سرور"""
    
    def __init__(self, host: str = "localhost", port: int = 8080):
        self.host = host
        self.port = port
        self.app = web.Application()
        self.configs: List[ConfigResult] = []
        self.processor = ConfigProcessor()
        self.tester = ConfigTester(max_concurrent=5)
        
        # WebSocket connections برای real-time updates
        self.websockets = set()
        
        self._setup_routes()
        self._setup_cors()
    
    def _setup_cors(self):
        """تنظیم CORS برای frontend"""
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })
        
        # اضافه کردن CORS به همه route ها
        for route in list(self.app.router.routes()):
            cors.add(route)
    
    def _setup_routes(self):
        """تنظیم route های API"""
        # Static files
        self.app.router.add_static('/', Path(__file__).parent, name='static')
        
        # API endpoints
        self.app.router.add_get('/api/configs', self.get_configs)
        self.app.router.add_post('/api/configs/fetch', self.fetch_configs)
        self.app.router.add_post('/api/configs/test', self.test_configs)
        self.app.router.add_get('/api/configs/{config_id}/test', self.test_single_config)
        self.app.router.add_get('/api/stats', self.get_stats)
        
        # WebSocket endpoint
        self.app.router.add_get('/api/ws', self.websocket_handler)
        
        # Health check
        self.app.router.add_get('/api/health', self.health_check)
    
    async def health_check(self, request: Request) -> Response:
        """بررسی سلامت API"""
        return web.json_response({
            'status': 'ok',
            'timestamp': datetime.now().isoformat(),
            'configs_count': len(self.configs)
        })
    
    async def get_configs(self, request: Request) -> Response:
        """دریافت لیست کانفیگ‌ها"""
        try:
            # فیلتر بر اساس query parameters
            status_filter = request.query.get('status', 'all')
            limit = int(request.query.get('limit', 100))
            offset = int(request.query.get('offset', 0))
            
            filtered_configs = self.configs
            
            # اعمال فیلتر وضعیت
            if status_filter != 'all':
                filtered_configs = [c for c in self.configs if c.status == status_filter]
            
            # اعمال pagination
            paginated_configs = filtered_configs[offset:offset + limit]
            
            # تبدیل به dictionary
            configs_data = [config.to_dict() for config in paginated_configs]
            
            return web.json_response({
                'configs': configs_data,
                'total': len(filtered_configs),
                'offset': offset,
                'limit': limit
            })
            
        except Exception as e:
            logger.error(f"Error in get_configs: {e}")
            return web.json_response(
                {'error': str(e)}, 
                status=500
            )
    
    async def fetch_configs(self, request: Request) -> Response:
        """دریافت کانفیگ‌های جدید"""
        try:
            # دریافت پارامترها از request body
            data = await request.json() if request.has_body else {}
            source = data.get('source', 'all')
            
            logger.info(f"شروع دریافت کانفیگ‌ها از منبع: {source}")
            
            # پخش پیام آغاز به WebSocket clients
            await self._broadcast_message({
                'type': 'fetch_started',
                'source': source,
                'timestamp': datetime.now().isoformat()
            })
            
            # دریافت کانفیگ‌ها
            if source == 'all':
                self.configs = await self.processor.process_all_sources()
            else:
                # دریافت از یک منبع خاص (TODO: پیاده‌سازی آینده)
                self.configs = await self.processor.process_all_sources()
            
            logger.info(f"✅ {len(self.configs)} کانفیگ دریافت شد")
            
            # پخش پیام تکمیل
            await self._broadcast_message({
                'type': 'fetch_completed',
                'configs_count': len(self.configs),
                'timestamp': datetime.now().isoformat()
            })
            
            return web.json_response({
                'success': True,
                'configs_count': len(self.configs),
                'message': f'{len(self.configs)} کانفیگ دریافت شد'
            })
            
        except Exception as e:
            logger.error(f"Error in fetch_configs: {e}")
            await self._broadcast_message({
                'type': 'fetch_error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            
            return web.json_response(
                {'error': str(e)}, 
                status=500
            )
    
    async def test_configs(self, request: Request) -> Response:
        """تست همه کانفیگ‌ها"""
        try:
            if not self.configs:
                return web.json_response(
                    {'error': 'هیچ کانفیگی برای تست موجود نیست'}, 
                    status=400
                )
            
            logger.info(f"شروع تست {len(self.configs)} کانفیگ")
            
            # پخش پیام آغاز تست
            await self._broadcast_message({
                'type': 'test_started',
                'configs_count': len(self.configs),
                'timestamp': datetime.now().isoformat()
            })
            
            # تابع callback برای ارسال پیشرفت
            async def progress_callback(config_id: int, message: str):
                await self._broadcast_message({
                    'type': 'test_progress',
                    'config_id': config_id,
                    'message': message,
                    'timestamp': datetime.now().isoformat()
                })
            
            # محدود کردن تعداد کانفیگ‌ها برای تست (برای جلوگیری از timeout)
            test_configs = self.configs[:20]  # فقط 20 تای اول
            
            # اجرای تست‌ها
            test_results = await self.tester.test_multiple_configs(
                test_configs, 
                progress_callback
            )
            
            # بروزرسانی کانفیگ‌ها با نتایج
            self.configs = self.tester.update_configs_with_results(
                self.configs, 
                test_results
            )
            
            # محاسبه آمار
            stats = self._calculate_stats()
            
            logger.info(f"✅ تست تمام شد - {stats}")
            
            # پخش پیام تکمیل
            await self._broadcast_message({
                'type': 'test_completed',
                'stats': stats,
                'timestamp': datetime.now().isoformat()
            })
            
            return web.json_response({
                'success': True,
                'tested_count': len(test_results),
                'stats': stats,
                'message': f'{len(test_results)} کانفیگ تست شد'
            })
            
        except Exception as e:
            logger.error(f"Error in test_configs: {e}")
            await self._broadcast_message({
                'type': 'test_error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            
            return web.json_response(
                {'error': str(e)}, 
                status=500
            )
    
    async def test_single_config(self, request: Request) -> Response:
        """تست یک کانفیگ خاص"""
        try:
            config_id = int(request.match_info['config_id'])
            
            # پیدا کردن کانفیگ
            config = next((c for c in self.configs if c.id == config_id), None)
            if not config:
                return web.json_response(
                    {'error': 'کانفیگ یافت نشد'}, 
                    status=404
                )
            
            # تابع callback برای ارسال پیشرفت
            async def progress_callback(cid: int, message: str):
                await self._broadcast_message({
                    'type': 'single_test_progress',
                    'config_id': cid,
                    'message': message,
                    'timestamp': datetime.now().isoformat()
                })
            
            # اجرای تست
            test_result = await self.tester.test_single_config(config, progress_callback)
            
            # بروزرسانی کانفیگ
            config.status = test_result.status
            config.ping = test_result.ping
            config.last_tested = test_result.test_time
            
            # ارسال نتیجه
            await self._broadcast_message({
                'type': 'single_test_completed',
                'config_id': config_id,
                'result': {
                    'status': test_result.status,
                    'ping': test_result.ping,
                    'response_time': test_result.response_time,
                    'error_message': test_result.error_message
                },
                'timestamp': datetime.now().isoformat()
            })
            
            return web.json_response({
                'success': True,
                'config_id': config_id,
                'result': {
                    'status': test_result.status,
                    'ping': test_result.ping,
                    'response_time': test_result.response_time,
                    'error_message': test_result.error_message
                }
            })
            
        except Exception as e:
            logger.error(f"Error in test_single_config: {e}")
            return web.json_response(
                {'error': str(e)}, 
                status=500
            )
    
    async def get_stats(self, request: Request) -> Response:
        """دریافت آمار کانفیگ‌ها"""
        try:
            stats = self._calculate_stats()
            return web.json_response(stats)
            
        except Exception as e:
            logger.error(f"Error in get_stats: {e}")
            return web.json_response(
                {'error': str(e)}, 
                status=500
            )
    
    def _calculate_stats(self) -> Dict:
        """محاسبه آمار کانفیگ‌ها"""
        stats = {
            'total': len(self.configs),
            'active': 0,
            'slow': 0,
            'dead': 0,
            'untested': 0
        }
        
        for config in self.configs:
            if config.status in stats:
                stats[config.status] += 1
        
        return stats
    
    async def websocket_handler(self, request: Request):
        """مدیریت WebSocket connections"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        self.websockets.add(ws)
        logger.info(f"WebSocket client connected. Total: {len(self.websockets)}")
        
        try:
            # ارسال پیام خوشامدگویی
            await ws.send_str(json.dumps({
                'type': 'connected',
                'message': 'اتصال برقرار شد',
                'timestamp': datetime.now().isoformat()
            }))
            
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        # پردازش پیام‌های دریافتی از client (در آینده)
                        logger.info(f"Received WebSocket message: {data}")
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON received: {msg.data}")
                        
                elif msg.type == WSMsgType.ERROR:
                    logger.error(f'WebSocket error: {ws.exception()}')
                    break
                    
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            self.websockets.discard(ws)
            logger.info(f"WebSocket client disconnected. Total: {len(self.websockets)}")
        
        return ws
    
    async def _broadcast_message(self, message: Dict):
        """ارسال پیام به همه WebSocket clients"""
        if not self.websockets:
            return
        
        message_str = json.dumps(message, ensure_ascii=False)
        
        # ارسال به همه clients
        disconnected = set()
        for ws in self.websockets:
            try:
                await ws.send_str(message_str)
            except Exception as e:
                logger.warning(f"Failed to send message to WebSocket: {e}")
                disconnected.add(ws)
        
        # حذف اتصالات قطع شده
        self.websockets -= disconnected
    
    async def start_server(self):
        """شروع سرور"""
        logger.info(f"🚀 شروع سرور API در http://{self.host}:{self.port}")
        
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        
        logger.info(f"✅ سرور آماده است:")
        logger.info(f"   📱 وب اپلیکیشن: http://{self.host}:{self.port}/")
        logger.info(f"   🔌 API: http://{self.host}:{self.port}/api/")
        logger.info(f"   📊 آمار: http://{self.host}:{self.port}/api/stats")
        
        return runner

async def main():
    """تابع اصلی برای اجرای سرور"""
    api = ConfigFinderAPI(host="0.0.0.0", port=8080)
    runner = await api.start_server()
    
    try:
        # نگه داشتن سرور
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("🛑 متوقف کردن سرور...")
    finally:
        await runner.cleanup()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 خداحافظ!")
