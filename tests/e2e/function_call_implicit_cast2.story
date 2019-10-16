function foobar stuff : Map[string, any] returns int
  return stuff["a"] to int

foobar(stuff: {"a":1, "b": "a"} to any)
