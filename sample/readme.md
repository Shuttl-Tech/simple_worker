> How to use example

- Make sure you have your aws creds in ~/.aws
`https://docs.aws.amazon.com/cli/latest/userguide/cli-config-files.html`

- aws sqs create-queue --queue-name foo

- `pipenv install --dev`

- change the queuname in `producer.py` and `consumer.py` to `foo`

- start producer and consumer in different shells:
  - terminal 1
    - `pipenv shell`
    - `python sample/producer.py`
  - terminal 2
    - `pipenv shell`
    - `python sample/consumer.py`

- create new tasks in producer by pressing any key. consumer process should start processing these tasks. yay!
