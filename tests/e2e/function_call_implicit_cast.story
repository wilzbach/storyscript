function boomrang k1: Map[string, float] k2: float returns float
  return k1["foo"]

boomrang(k1: {"foo": 2} k2: 1)
