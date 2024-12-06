from typing import Generator

import numpy as np


def get_steps(start: float, step: float, stop: float) -> Generator[float, None, None]:
    modulo = abs(stop - start) % abs(step)
    if stop > start:
        vstop = stop - modulo
    else:
        vstop = stop + modulo
    for i in np.linspace(start, vstop, int(abs(vstop - start) / abs(step)) + 1):
        if ((i >= start) and (i <= stop)) or (
            (i >= stop) and (i <= start)
        ):  # Check inserted here to ensure scan remains within defined range
            yield i
