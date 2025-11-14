# SmartSwitch Integration

SmartAsync provides a plugin for [SmartSwitch](https://github.com/genropy/smartswitch) that enables bidirectional sync/async support for SmartSwitch handlers.

## Overview

The `SmartasyncPlugin` automatically wraps async SmartSwitch handlers with `@smartasync`, allowing them to be called from both synchronous and asynchronous contexts without explicit `await` handling.

## Installation

Both packages need to be installed:

```bash
pip install smartasync smartswitch
```

## Basic Usage

```python
from smartswitch import Switcher
from smartasync import SmartasyncPlugin

class APIHandler:
    api = Switcher().plug(SmartasyncPlugin())

    @api
    async def fetch_user(self, user_id: int):
        # Your async implementation
        async with httpx.AsyncClient() as client:
            response = await client.get(f"/users/{user_id}")
            return response.json()

handler = APIHandler()

# Works in sync context - no await needed!
user = APIHandler.api("fetch_user")(handler, user_id=123)

# Works in async context - use await
async def async_usage():
    user = await APIHandler.api("fetch_user")(handler, user_id=123)
```

## How It Works

The plugin operates in two phases:

1. **on_decore**: When a handler is decorated, the plugin checks if it's an async function
2. **wrap_handler**: During execution, async handlers are wrapped with `@smartasync` for bidirectional support

### Automatic Detection

The plugin automatically:
- ✅ Wraps `async def` handlers with smartasync
- ✅ Leaves sync handlers unchanged
- ✅ Prevents double-wrapping (if already decorated with `@smartasync`)

## Use Cases

### Dynamic API Dispatching

```python
from smartswitch import Switcher
from smartasync import SmartasyncPlugin

class StorageManager:
    def __init__(self):
        self.api = Switcher(prefix='storage_')
        self.api.plug(SmartasyncPlugin())

    @property
    def node(self):
        @self.api
        async def _node(self, path: str):
            # Async I/O operations
            async with aiofiles.open(path) as f:
                return await f.read()
        return _node

    @property
    def list(self):
        @self.api
        async def _list(self, directory: str):
            # List directory async
            return await async_listdir(directory)
        return _list

# Sync usage
storage = StorageManager()
content = storage.node(storage, path="/data/file.txt")

# Async usage
async def process():
    content = await storage.node(storage, path="/data/file.txt")
```

### Plugin Systems

Perfect for plugin architectures where plugins may be sync or async:

```python
class PluginManager:
    plugins = Switcher().plug(SmartasyncPlugin())

    @plugins
    async def on_startup(self):
        await self.initialize_async_resources()

    @plugins
    def on_event(self, event):
        self.handle_sync_event(event)

# Both work regardless of context
manager.plugins("on_startup")(plugin_instance)
manager.plugins("on_event")(plugin_instance, event)
```

## Configuration

The plugin is instantiated with default settings:

```python
# Default usage
api.plug(SmartasyncPlugin())

# With custom name (optional)
api.plug(SmartasyncPlugin(name="custom_smartasync"))
```

## Requirements

- **SmartSwitch**: v0.6.0+ (with `MethodEntry` support)
- **SmartAsync**: v0.3.0+
- **Python**: 3.10+

## Compatibility

The plugin:
- ✅ Thread-safe
- ✅ Works with all SmartSwitch features (nested switches, runtime data, etc.)
- ✅ Compatible with other plugins (logging, pydantic, etc.)
- ✅ Supports plugin priority ordering

## Performance

The plugin adds minimal overhead:
- Detection happens once during decoration
- Wrapping uses the efficient `@smartasync` decorator
- No runtime penalties for sync-only or async-only code paths

## See Also

- [SmartSwitch Documentation](https://smartswitch.readthedocs.io)
- [SmartAsync Basics](../user-guide/basic.md)
- [How SmartAsync Works](../how-it-works/index.md)
