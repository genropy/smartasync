"""Test SmartasyncPlugin for SmartSwitch integration."""

import asyncio

import pytest
from smartswitch import Switcher

from smartasync import SmartasyncPlugin, smartasync


class TestBasicPlugin:
    """Test basic plugin functionality with SmartSwitch."""

    def test_plugin_wraps_async_method(self):
        """Test that plugin wraps async methods with smartasync."""

        class Handler:
            def __init__(self):
                self.api = Switcher().plug(SmartasyncPlugin())

            @property
            def async_method(self):
                @self.api
                async def _handler(self):
                    await asyncio.sleep(0.01)
                    return "result"
                return _handler

        handler = Handler()
        method = handler.async_method

        # Should work in sync context (smartasync applied)
        result = method(handler)
        assert result == "result"

    def test_plugin_passes_through_sync_method(self):
        """Test that plugin doesn't wrap sync methods."""

        class Handler:
            def __init__(self):
                self.api = Switcher().plug(SmartasyncPlugin())

            @property
            def sync_method(self):
                @self.api
                def _handler(self):
                    return "sync_result"
                return _handler

        handler = Handler()
        method = handler.sync_method

        # Should work normally (not wrapped)
        result = method(handler)
        assert result == "sync_result"

        # Should not have smartasync marker
        assert not hasattr(method, "_smartasync_reset_cache")

    def test_plugin_prevents_double_wrapping(self):
        """Test that already-wrapped methods aren't wrapped twice."""

        class Handler:
            def __init__(self):
                self.api = Switcher().plug(SmartasyncPlugin())

            @property
            def pre_wrapped_method(self):
                @self.api
                @smartasync
                async def _handler(self):
                    await asyncio.sleep(0.01)
                    return "result"
                return _handler

        handler = Handler()
        method = handler.pre_wrapped_method

        # Should still have only one level of wrapping
        assert hasattr(method, "_smartasync_reset_cache")

        # Should work in sync context
        result = method(handler)
        assert result == "result"


class TestStorageManagerPattern:
    """Test the storage manager pattern from the issue."""

    def test_storage_manager_sync_context(self):
        """Test storage manager in sync context."""

        class StorageManager:
            def __init__(self):
                self.api = Switcher(prefix='storage_').plug(SmartasyncPlugin())
                self.data = []

            @property
            def node(self):
                @self.api
                async def _node(self, path: str):
                    """Async handler for node access."""
                    await asyncio.sleep(0.01)
                    self.data.append(path)
                    return f"node:{path}"
                return _node

        manager = StorageManager()
        node_method = manager.node

        # Should work in sync context
        result = node_method(manager, "file.txt")
        assert result == "node:file.txt"
        assert "file.txt" in manager.data

    @pytest.mark.asyncio
    async def test_storage_manager_async_context(self):
        """Test storage manager in async context."""

        class StorageManager:
            def __init__(self):
                self.api = Switcher(prefix='storage_').plug(SmartasyncPlugin())
                self.data = []

            @property
            def node(self):
                @self.api
                async def _node(self, path: str):
                    """Async handler for node access."""
                    await asyncio.sleep(0.01)
                    self.data.append(path)
                    return f"node:{path}"
                return _node

        manager = StorageManager()
        node_method = manager.node

        # Should work in async context with await
        result = await node_method(manager, "async_file.txt")
        assert result == "node:async_file.txt"
        assert "async_file.txt" in manager.data


class TestMultipleMethods:
    """Test plugin with multiple methods."""

    def test_multiple_async_methods(self):
        """Test plugin with multiple async methods registered."""

        class MultiHandler:
            def __init__(self):
                self.api = Switcher().plug(SmartasyncPlugin())

            @property
            def handler_one(self):
                @self.api
                async def _handler_one(self):
                    await asyncio.sleep(0.01)
                    return "one"
                return _handler_one

            @property
            def handler_two(self):
                @self.api
                async def _handler_two(self):
                    await asyncio.sleep(0.01)
                    return "two"
                return _handler_two

            @property
            def handler_three(self):
                @self.api
                def _handler_three(self):
                    return "three"
                return _handler_three

        handler = MultiHandler()

        # All should work in sync context
        assert handler.handler_one(handler) == "one"
        assert handler.handler_two(handler) == "two"
        assert handler.handler_three(handler) == "three"


class TestMethodWithArguments:
    """Test plugin with methods that take arguments."""

    def test_method_with_arguments(self):
        """Test plugin with method that takes arguments."""

        class Calculator:
            def __init__(self):
                self.api = Switcher().plug(SmartasyncPlugin())

            @property
            def add(self):
                @self.api
                async def _add(self, a: int, b: int) -> int:
                    await asyncio.sleep(0.01)
                    return a + b
                return _add

        calc = Calculator()
        add_method = calc.add

        # Should work with arguments
        result = add_method(calc, 10, 20)
        assert result == 30

    def test_method_with_kwargs(self):
        """Test plugin with method that uses keyword arguments."""

        class Formatter:
            def __init__(self):
                self.api = Switcher().plug(SmartasyncPlugin())

            @property
            def format_text(self):
                @self.api
                async def _format_text(self, text: str, upper: bool = False) -> str:
                    await asyncio.sleep(0.01)
                    return text.upper() if upper else text.lower()
                return _format_text

        formatter = Formatter()
        format_method = formatter.format_text

        # Should work with kwargs
        assert format_method(formatter, "Hello") == "hello"
        assert format_method(formatter, "Hello", upper=True) == "HELLO"


class TestPluginProtocol:
    """Test that plugin implements the correct protocol."""

    def test_plugin_wrap_signature(self):
        """Test that plugin.wrap() has correct signature."""
        plugin = SmartasyncPlugin()
        switcher = Switcher()

        class TestClass:
            async def test_method(self):
                return "test"

        # Should accept func and switcher arguments
        wrapped = plugin.wrap(TestClass.test_method, switcher)

        # Should return wrapped function
        assert callable(wrapped)
        assert hasattr(wrapped, "_smartasync_reset_cache")

    def test_plugin_preserves_metadata(self):
        """Test that plugin preserves method metadata."""

        class DocHandler:
            def __init__(self):
                self.api = Switcher().plug(SmartasyncPlugin())

            @property
            def documented_method(self):
                @self.api
                async def _documented(self):
                    """This is a documented method."""
                    return "result"
                return _documented

        handler = DocHandler()
        method = handler.documented_method

        # smartasync preserves __doc__ via functools.wraps
        assert "documented method" in method.__doc__
