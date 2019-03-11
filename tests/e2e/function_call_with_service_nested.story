function random returns int
  return 28  # Assume some RNG here

function my_func k1: int k2: int returns int
  return 28  # Assume some RNG here

b = my_service command p0: my_func(k1: (another_service command p1: random() k2: 2)) p2: 2
