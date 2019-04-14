function foo returns Map[int,List[string]]
	return {20: ["foo", "bar"]}

a = 0
b = foo()
c = "any string"
c = b["foo"][0]
