function foobar stuff : Map[string, any] returns int
  return stuff["a"] as int

foobar(stuff: {"a":1, "b": "a"} as any)
