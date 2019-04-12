function foo returns map[int,list[string]]
	return {20: ["foo", "bar"]}

a = 0
b = foo()
c = "any string"
c = b[20][0]
