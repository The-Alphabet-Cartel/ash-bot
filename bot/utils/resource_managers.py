"""
Resource Management with Proper Context Managers
"""

import asyncio
import aiohttp
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional, Dict, Any
import weakref

logger = logging.getLogger(__name__)

class SessionManager:
    """Manages aiohttp sessions with proper cleanup"""
    
    def __init__(self):
        self._sessions: Dict[str, aiohttp.ClientSession] = {}
        self._cleanup_refs = weakref.WeakSet()
    
    @asynccontextmanager
    async def get_session(self, name: str = "default", **session_kwargs) -> AsyncGenerator[aiohttp.ClientSession, None]:
        """Get or create a named session with automatic cleanup"""
        
        session = None
        created_new = False
        
        try:
            # Get existing session or create new one
            if name not in self._sessions or self._sessions[name].closed:
                connector = aiohttp.TCPConnector(
                    limit=10,
                    ttl_dns_cache=300,
                    use_dns_cache=True,
                    enable_cleanup_closed=True,
                    **session_kwargs.pop('connector_kwargs', {})
                )
                
                session = aiohttp.ClientSession(
                    connector=connector,
                    timeout=aiohttp.ClientTimeout(total=30),
                    **session_kwargs
                )
                
                self._sessions[name] = session
                self._cleanup_refs.add(session)
                created_new = True
                
                logger.debug(f"Created new aiohttp session: {name}")
            else:
                session = self._sessions[name]
            
            yield session
            
        except Exception as e:
            logger.error(f"Error in session {name}: {e}")
            # Close session on error if we created it
            if created_new and session and not session.closed:
                await session.close()
                self._sessions.pop(name, None)
            raise
        finally:
            # Sessions are kept alive for reuse, but will be cleaned up on shutdown
            pass
    
    async def close_session(self, name: str):
        """Explicitly close a named session"""
        if name in self._sessions:
            session = self._sessions.pop(name)
            if not session.closed:
                await session.close()
                logger.debug(f"Closed session: {name}")
    
    async def close_all(self):
        """Close all managed sessions"""
        logger.info("Closing all HTTP sessions...")
        
        for name, session in list(self._sessions.items()):
            if not session.closed:
                try:
                    await session.close()
                    logger.debug(f"Closed session: {name}")
                except Exception as e:
                    logger.debug(f"Error closing session {name}: {e}")
        
        self._sessions.clear()
        
        # Wait a bit for connections to close
        await asyncio.sleep(0.1)
        logger.info("All HTTP sessions closed")

# Global session manager instance
session_manager = SessionManager()

class ResourceCleanupMixin:
    """Mixin class for proper resource cleanup"""
    
    def __init__(self):
        self._cleanup_tasks = set()
        self._cleanup_callbacks = []
    
    def register_cleanup(self, callback):
        """Register a cleanup callback"""
        self._cleanup_callbacks.append(callback)
    
    def create_background_task(self, coro, *, name: str = None):
        """Create a background task with automatic cleanup tracking"""
        task = asyncio.create_task(coro, name=name)
        self._cleanup_tasks.add(task)
        task.add_done_callback(self._cleanup_tasks.discard)
        return task
    
    async def cleanup_resources(self):
        """Clean up all resources"""
        logger.info(f"Cleaning up resources for {self.__class__.__name__}")
        
        # Cancel background tasks
        if self._cleanup_tasks:
            logger.info(f"Cancelling {len(self._cleanup_tasks)} background tasks")
            for task in self._cleanup_tasks:
                task.cancel()
            
            # Wait for tasks to be cancelled
            if self._cleanup_tasks:
                try:
                    await asyncio.wait(self._cleanup_tasks, timeout=5.0)
                except asyncio.TimeoutError:
                    logger.warning("Some tasks did not cancel within timeout")
        
        # Run cleanup callbacks
        for callback in self._cleanup_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback()
                else:
                    callback()
            except Exception as e:
                logger.error(f"Error in cleanup callback: {e}")
        
        logger.info(f"Resource cleanup completed for {self.__class__.__name__}")

@asynccontextmanager
async def managed_claude_session(api_key: str):
    """Context manager for Claude API sessions"""
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': api_key,
        'anthropic-version': '2023-06-01'
    }
    
    async with session_manager.get_session("claude", headers=headers) as session:
        yield session

@asynccontextmanager  
async def managed_nlp_session(base_url: str):
    """Context manager for NLP service sessions"""
    headers = {
        'Content-Type': 'application/json',
    }
    
    async with session_manager.get_session("nlp", headers=headers) as session:
        # Verify connection
        try:
            async with session.get(f"{base_url}/health", timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status != 200:
                    logger.warning(f"NLP service health check failed: {response.status}")
        except Exception as e:
            logger.warning(f"NLP service connection test failed: {e}")
        
        yield session

class GracefulShutdown:
    """Handles graceful shutdown of all resources"""
    
    def __init__(self):
        self._shutdown_callbacks = []
        self._is_shutting_down = False
    
    def register_shutdown_handler(self, callback):
        """Register a shutdown callback"""
        self._shutdown_callbacks.append(callback)
    
    async def shutdown(self):
        """Perform graceful shutdown"""
        if self._is_shutting_down:
            return
        
        self._is_shutting_down = True
        logger.info("🛑 Starting graceful shutdown...")
        
        # Run shutdown callbacks
        for i, callback in enumerate(self._shutdown_callbacks):
            try:
                callback_name = getattr(callback, '__name__', f'callback_{i}')
                logger.info(f"Running shutdown handler: {callback_name}")
                
                if asyncio.iscoroutinefunction(callback):
                    await callback()
                else:
                    callback()
                    
            except Exception as e:
                logger.error(f"Error in shutdown callback {i}: {e}")
        
        # Close all HTTP sessions
        await session_manager.close_all()
        
        # Wait for final cleanup
        await asyncio.sleep(0.1)
        
        logger.info("✅ Graceful shutdown completed")

# Global shutdown handler
graceful_shutdown = GracefulShutdown()

class RetryMixin:
    """Mixin for implementing exponential backoff retry logic"""
    
    async def retry_with_backoff(self, operation, max_retries: int = 3, 
                                base_delay: float = 1.0, max_delay: float = 60.0,
                                exceptions: tuple = (Exception,)):
        """Execute operation with exponential backoff retry"""
        
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                return await operation()
            except exceptions as e:
                last_exception = e
                
                if attempt == max_retries:
                    break
                
                delay = min(base_delay * (2 ** attempt), max_delay)
                logger.warning(f"Operation failed (attempt {attempt + 1}/{max_retries + 1}), "
                             f"retrying in {delay:.1f}s: {e}")
                
                await asyncio.sleep(delay)
        
        raise last_exception