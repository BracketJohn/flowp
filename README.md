# flowp

Afternoon project that approximates and plots flow pipes for linear hybrid automata. Very unoptimal in the sense that this is restricted to 2D space and doesn't use any optimized libraries for polytope representations.

Nice to play around and explore basic flowpipe construction.

# Usage

`flowp` can be used like:

```python
import numpy as np
from flowp import approx

initial_location = [np.array(v) for v in [[1, 1], [2, 1], [3, 2], [1, 2]]]
flow = np.array([[1, 4], [-1, 3]])
bloating = [np.array(v) for v in [[0, 1], [1, 0], [-1, 0], [0, -1]]]

polytopes = approx(initial_location, flow, bloating, plot=True)  # Opens plot in standard browser.
```

The above code will produce the following plot:

![Flowpipe plot](./example_flowp.png)

# Setup

If you have problems installing dependencies/setting this up to work, you can use `poetry` dependency management. Just run:

```
> poetry install
> cd src
> poetry run python3
```

This will use the provided lock file to install all dependencies and then run a virtual env python environment, in which you can execute the above code.
