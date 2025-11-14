SmartAsync Documentation
========================

   *Sync or async: this WAS the question*

**Bidirectional sync/async bridge for Python**

SmartAsync provides automatic context detection to seamlessly bridge synchronous and asynchronous Python code. Write your code once, use it everywhere.

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   user-guide/installation
   user-guide/quickstart
   user-guide/basic

.. toctree::
   :maxdepth: 2
   :caption: How It Works

   how-it-works/index
   how-it-works/sync-to-async
   how-it-works/async-to-sync

.. toctree::
   :maxdepth: 2
   :caption: Usage Scenarios

   scenarios/index
   scenarios/01-sync-app-async-libs
   scenarios/02-async-app-sync-libs
   scenarios/03-testing-async-code
   scenarios/04-unified-library-api
   scenarios/05-gradual-migration
   scenarios/06-plugin-systems
   scenarios/07-mixed-framework
   scenarios/08-web-scraping
   scenarios/09-interactive-environments

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/decorator

.. toctree::
   :maxdepth: 2
   :caption: Integrations

   integrations/smartswitch

.. toctree::
   :maxdepth: 2
   :caption: Advanced Topics

   advanced/technical-overview
   advanced/comparison
   advanced/performance

Key Features
------------

* **Automatic Context Detection** - Detects sync vs async execution context at runtime
* **Bidirectional** - Supports both sync→async and async→sync
* **Zero Configuration** - Just apply the ``@smartasync`` decorator
* **Thread-Safe Offloading** - Sync code in async context runs in thread pool
* **Pure Python** - No dependencies beyond standard library
* **Python 3.10+** - Uses modern pattern matching

Quick Example
-------------

.. code-block:: python

   from smartasync import smartasync
   import httpx

   @smartasync
   async def fetch_data(url: str):
       async with httpx.AsyncClient() as client:
           return await client.get(url).json()

   # Sync context - no await needed!
   data = fetch_data("https://api.example.com")

   # Async context - use await
   data = await fetch_data("https://api.example.com")

Installation
------------

.. code-block:: bash

   pip install smartasync

How It Works
------------

SmartAsync uses **pattern matching** to handle four execution scenarios:

========== ============ ========================================
Context    Method       Behavior
========== ============ ========================================
Sync → Async  ``async def``  Execute with ``asyncio.run()``
Sync → Sync   ``def``        Direct pass-through
Async → Async ``async def``  Return coroutine (awaitable)
Async → Sync  ``def``        Offload to thread with ``asyncio.to_thread()``
========== ============ ========================================

Part of Genro-Libs
------------------

SmartAsync is part of the `Genro-Libs toolkit <https://github.com/softwell/genro-libs>`_ - a collection of focused, well-tested Python developer tools.

License
-------

MIT License - see `LICENSE <https://github.com/genropy/smartasync/blob/main/LICENSE>`_ for details.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
