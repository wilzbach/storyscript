function random returns int
  return 28  # Assume some RNG here

function my_func k1: int k2: int returns int
  return 28  # Assume some RNG here

b = random integer low: my_func(k1: (random integer low: random() high: random()) k2: 2) high: 2
