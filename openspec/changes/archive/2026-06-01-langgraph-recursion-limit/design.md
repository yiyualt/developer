## Design

```python
DEFAULT_RECURSION_LIMIT = 25

def invoke(self, input_state: dict, config: dict = None) -> dict:
    config = config or {}
    limit = config.get("recursion_limit", DEFAULT_RECURSION_LIMIT)
    
    for i in range(limit):
        ...
    raise RecursionError(f"Recursion limit of {limit} reached. Last state: {state}")
```
