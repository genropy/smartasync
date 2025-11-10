# Basic Usage

Learn the fundamentals of SmartAsync.

## The @smartasync Decorator

Apply to any async method to make it work in both contexts:

```python
from smartasync import smartasync

class MyClass:
    @smartasync
    async def my_method(self):
        # async implementation
        await some_async_operation()
        return result
```

## Calling from Sync Context

```python
obj = MyClass()
result = obj.my_method()  # No await needed
```

SmartAsync detects no event loop and automatically runs with `asyncio.run()`.

## Calling from Async Context

```python
async def main():
    obj = MyClass()
    result = await obj.my_method()  # Normal await
```

SmartAsync detects the event loop and returns a coroutine.

## Sync Methods in Async Context

SmartAsync also handles sync methods called from async context:

```python
@smartasync
def blocking_operation(self):
    # Blocking sync code
    time.sleep(1)
    return result

async def handler():
    obj = MyClass()
    # Automatically offloaded to thread!
    result = await obj.blocking_operation()
```

This prevents blocking the event loop.

## Best Practices

1. **Use async implementations when possible** - Better performance
2. **Decorate all public methods** - Consistent API
3. **Handle errors normally** - SmartAsync is transparent to exceptions
4. **Test both contexts** - Ensure methods work in sync and async

## Next Steps

- [Usage Scenarios →](../scenarios/index.md)
- [How It Works →](../how-it-works/index.md)
- [API Reference →](../api/decorator.md)
