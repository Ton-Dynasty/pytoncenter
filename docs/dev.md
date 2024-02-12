# Development Guide


## Setup Development Environment

### 1. Install dependencies

```bash
poetry install
```

### 2. Export the TONCENTER_API_KEY

To use the TON Center API, you need to obtain an API key from the [TON Center](https://toncenter.com/). After obtaining the API key from [@tonapibot](https://t.me/tonapibot), export it as an environment variable:

```bash
export TONCENTER_API_KEY=your_api_key
```

### 3. Open virtual environment

```bash
poetry shell
```

### 4. Install pre-commit hooks

```bash
poetry run pre-commit install
```

### 5. Run tests

```bash
make test
```

### 6. Run examples

```bash
poetry run python examples/v3/decode_jetton_data.py
```
