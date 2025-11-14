Overview
========

**The Problem: Sync and Async Don't Mix**

Python's async/await brings powerful concurrency, but creates a fundamental incompatibility:

* **Sync code cannot call async functions** - You can't ``await`` in regular functions
* **Async code cannot call sync functions safely** - Blocking calls freeze the event loop
* **Libraries must choose one or the other** - Forcing users into specific execution contexts

This forces developers to:

* Maintain separate sync and async versions of the same code
* Rewrite entire codebases when adopting async
* Abandon useful libraries that don't match their execution context
* Build complex wrapper layers to bridge the gap

What is SmartAsync?
-------------------

**SmartAsync automatically bridges sync and async Python code.**

It's a decorator that makes functions work seamlessly in both synchronous and asynchronous contexts:

* Write your function **once** (sync or async)
* Use it **everywhere** (sync or async context)
* **Zero configuration** - just add ``@smartasync``
* **Automatic context detection** at runtime

.. code-block:: python

   from smartasync import smartasync

   # Write once - async version
   @smartasync
   async def fetch_data(url: str):
       async with httpx.AsyncClient() as client:
           response = await client.get(url)
           return response.json()

   # Use in sync context - works automatically!
   def sync_main():
       data = fetch_data("https://api.example.com/users")
       print(data)

   # Use in async context - works automatically!
   async def async_main():
       data = await fetch_data("https://api.example.com/users")
       print(data)

When is SmartAsync Useful?
---------------------------

**1. Using Async Libraries in Sync Applications**

You have a sync application but want to use modern async libraries (httpx, aiofiles, databases):

.. code-block:: python

   # Your existing sync application
   def process_users():
       for user_id in user_ids:
           # Use async httpx library seamlessly
           data = fetch_user(user_id)  # Actually calls async function
           save_to_db(data)

**2. Building Libraries with Unified APIs**

You're building a library and want users to use it in both sync and async code:

.. code-block:: python

   # Your library code - write once
   @smartasync
   async def query_database(sql: str):
       async with database.connect() as conn:
           return await conn.execute(sql)

   # Users can use it either way:
   result = query_database("SELECT * FROM users")        # Sync
   result = await query_database("SELECT * FROM users")  # Async

**3. Gradual Migration to Async**

You're migrating from sync to async but can't rewrite everything at once:

.. code-block:: python

   # Old sync code
   def process_order(order_id):
       order = get_order(order_id)  # Still sync
       payment = charge_payment(order)  # Already migrated to async
       send_email(order.email)  # Still sync

   # Migrated function works in sync context
   @smartasync
   async def charge_payment(order):
       async with stripe.Client() as client:
           return await client.charge(order.amount)

**4. Testing Async Code Synchronously**

You want to test async code without dealing with event loops in tests:

.. code-block:: python

   @smartasync
   async def fetch_user(user_id: int):
       async with httpx.AsyncClient() as client:
           response = await client.get(f"/users/{user_id}")
           return response.json()

   # Simple sync test - no event loop needed
   def test_fetch_user():
       user = fetch_user(123)
       assert user["id"] == 123
       assert "name" in user

**5. Plugin Systems**

You're building a plugin system where plugins might be sync or async:

.. code-block:: python

   from smartswitch import Switcher

   plugins = Switcher()

   # Some plugins are async
   @plugins
   @smartasync
   async def email_plugin(data):
       async with aiosmtplib.SMTP() as smtp:
           await smtp.send_message(data)

   # Some plugins are sync
   @plugins
   def log_plugin(data):
       logger.info(data)

   # Your framework calls them uniformly
   def execute_plugins(data):
       for name in plugins._handlers:
           result = plugins(name)(data)  # Works for both!

**6. Interactive Environments (Jupyter, IPython)**

You want async functions to work in interactive shells without explicit ``await``:

.. code-block:: python

   @smartasync
   async def explore_api(endpoint):
       async with httpx.AsyncClient() as client:
           return await client.get(endpoint)

   # In Jupyter/IPython - just call it
   >>> data = explore_api("/api/users")
   >>> print(data)

When NOT to Use SmartAsync
--------------------------

**Don't use SmartAsync if:**

* **Performance is critical** - There's overhead in context detection (~microseconds)
* **You're only in one context** - If you're purely async or purely sync, use native code
* **You need fine-grained control** - SmartAsync abstracts away execution details

How It Works
------------

SmartAsync detects the execution context at runtime:

**In Sync Context:**
   * Async functions run in a new event loop using ``asyncio.run()``
   * Sync functions run normally

**In Async Context:**
   * Async functions run directly with ``await``
   * Sync functions run in a thread pool (non-blocking)

**Smart Caching:**
   * Detects which wrapper to use once per context
   * Subsequent calls skip detection overhead
   * Automatic cache invalidation on context switch

Key Features
------------

* ✅ **Automatic Context Detection** - No configuration needed
* ✅ **Bidirectional** - Supports sync→async and async→sync
* ✅ **Thread-Safe** - Sync code in async context runs in thread pool
* ✅ **Zero Dependencies** - Pure Python standard library
* ✅ **Type Safe** - Full type hints support
* ✅ **Performance Optimized** - Smart caching minimizes overhead

Next Steps
----------

Ready to try SmartAsync?

* :doc:`user-guide/installation` - Install SmartAsync
* :doc:`user-guide/quickstart` - Get started in 5 minutes
* :doc:`scenarios/index` - See real-world usage patterns
* :doc:`integrations/smartswitch` - Use with SmartSwitch for powerful dispatching
