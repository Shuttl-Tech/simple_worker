# simple-worker

`simple-worker` is a wrapper around SQS for applications that need to process
tasks asynchronously.

<!-- toc -->

- [Installation](#installation)
- [Configuration](#configuration)
- [Basic Usage](#basic-usage)
- [Developers Guide](#developers-guide)
  * [Changes to task handler signature](#changes-to-task-handler-signature)
  * [Task handler parameters](#task-handler-parameters)
  * [Task Execution Context](#task-execution-context)
  * [Testing Mode](#testing-mode)
- [Operations](#operations)
  * [Creating/Deleting queues](#creatingdeleting-queues)
  * [Retries, dead letter queues](#retries-dead-letter-queues)
  * [Running worker processes](#running-worker-processes)
  * [Terminating worker processes](#terminating-worker-processes)
  * [Stats, Reporting](#stats-reporting)
- [Design Notes](#design-notes)
  * [Explicit task names](#explicit-task-names)
  * [No positional arguments](#no-positional-arguments)

<!-- tocstop -->

## Installation

`pip install simple-worker`

## Configuration

You'll need to setup at least one SQS queue:

```bash
aws sqs create-queue --queue-name your-prefix-default
```

## Basic Usage

Initialize the app and task handlers:

```python
from simple_worker import App

app = App.init(queue_prefix='your-prefix-')

@app.register_task_handler('my_task')
def my_task_handler(a, b):
    # Do something worthwhile
    pass
```

Produce tasks:

```python
app.add_task('my_task', **{'a': 1, 'b': 2})
```

Consume tasks:

```python
app.worker().start()
```

## Developers Guide

### Changes to task handler signature

When altering the signature for task handlers, make sure to follow [parallel
change](https://martinfowler.com/bliki/ParallelChange.html) so that all old
jobs are not affected.

Here, altering a signature involves anything except re-ordering parameters.

There might be potentially 'safe' changes that this library could handle
intelligently, but for now it'll reject any signature mismatch.

### Task handler parameters

Task parameters are always passed as keyword arguments.  Hence, a task
handler's parameter names are important, their order is not.

```python
# The following two handlers are equivalent, because the param names remain
the same:

def task_handler(param1, param2):
    pass

def task_handler(param2, param1):
    pass

# But these two are not:

def task_handler(param1, param2):
    pass

def task_handler(param_1, param_2):
    # ^ Note, the param names changed from paramX -> param_X
    pass
```

Whenever you have to rename params, consider it a change in the task handler
signature and follow [parallel
change](https://martinfowler.com/bliki/ParallelChange.html) so that all old
jobs are not affected.

### Task Execution Context

By default, the `simple_worker.TaskExecutor` class is used to run tasks. This
class can be subclassed to wrap a task in an application-specific context.
For example, maybe you want a task to run in the context of your flask
application so that it can re-use all the app initialization logic.

```python
from simple_worker import TaskExecutor
from simple_worker import App

app = App()

class FlaskContextTaskExecutor(TaskExecutor):
    @contextmanager
    def context(self):
        with flask_app.app_context():
            yield

worker = app.worker(task_executor_cls=FlaskContextTaskExecutor)
worker.start()
```

### Testing Mode

For testing, an in-memory queue implementation is available. Init the app with
`testing_mode=True` to use it.

```
from simple_worker import App

app = App(testing_mode=True)
```

Using this mode can help catch errors (like task handler signature mismatches)
during development.

In the future, a 'testing worker' will be supported too so that one can
run queued jobs within tests.


## Operations

### Creating/Deleting queues

This library does not create or delete queues from SQS. It expects all the
queues it needs to be created beforehand.

### Retries, dead letter queues

This library doesn't handle retry logic, as SQS has decent-enough support
for this through visibility timeouts and dead letter queues. It is recommended
that we setup dead letter queues for all queues that applications use.

### Running worker processes

TODO

### Terminating worker processes

Worker processes are configured to attempt graceful shutdown when they receive
a `SIGTERM` signal. Any in-flight task will be completed before shutting down.

If a worker process doesn't terminate in a sensible amount of time after
receiving a `SIGTERM`, forcefully terminate.

### Stats, Reporting

Basic reporting on number of messages queued/in-flight can be done directly
through SQS. This library doesn't offer any reporting features at the moment.

## Design Notes

### Explicit task names

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

### No positional arguments

When tasks are queued, positional arguments are not allowed in the payload. All
arguments must be referred to by name. This prevents against mistakes like
altering the order of arguments. It also makes it easy to understand what a
task is by just viewing the payload in SQS.

