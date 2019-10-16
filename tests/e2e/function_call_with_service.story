function random returns string
  return "abc@xyz.com"  # Assume some RNG here

function my_func k1: int k2: int returns string
  return k1 to string +k2 to string  # Assume some RNG here

a = random()
mailgun send to: [random()] subject: my_func(k1: 1 k2:2) from: random() text: "foobar"
