# simple-worker

`simple-worker` is a wrapper around SQS for applications that need to process
tasks asynchronously.

### Installation

`pip install simple-worker`

### Configuration

You'll need to setup at least one SQS queue:

```bash
aws sqs create-queue --queue-name your-prefix-default
```

### Basic Usage

Initialize the app and task handlers:

```python
from simple_worker import App

app = App.init(broker_url='sqs://yo@yo:', queue_prefix='your-prefix-')

@app.register_task_handler('my_task')
def my_task_handler(a, b):
    # Do something worthwhile
    pass
```

Produce tasks:

```python
app.add_task('my_task', {'a': 1, 'b': 2})
```

To consume tasks:

```python
app.worker().start()
```

### Design Notes

**Explicit task names**

Libraries like Celery automatically generate task names based on a module +
function name. An example:

```python
# file: module1/tasks.py

# The below function will have a task name of `module1.tasks.my_function`
@celery.task
def my_function(a, b):
    pass
```

In this case, producers aren't aware of the task name either, since they import
and use the handler function directly.

While this offers a nicer API, it masks a lot of details. What happens when a
task handler function is moved from one module to another? The task name would
have changed under-the-hood, and all old tasks would start failing once the new
code is deployed.

`simple_worker` avoids these situations by making task names explicit. The
producer and consumer are aware of the `task_name` being used to refer to
a task handler.

**No positional arguments**

When tasks are queued, positional arguments are not allowed in the payload. All
arguments must be referred to by name. This prevents against mistakes like
altering the order of arguments. It also makes it easy to understand what a
task is by just viewing the payload in SQS.

### Developers

**Testing**

For testing, an in-memory queue implementation is available. Init the app with
the following `broker_url` to activate it: "memory://localhost". When used, any
tasks created on the same app will be available for consumption by workers.

**Catching errors during development**

**TODO**

### Operations

**Stats**

Basic reporting on number of messages queued/inflight can be done directly
through SQS. This library doesn't offer any such features.

**Dead letter queues and retries**

This library doesn't handle retry logic, as SQS has decent-enough support
for this through visibility timeouts and dead letter queues.
