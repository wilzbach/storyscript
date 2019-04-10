a = [1]
# access by number
a[0] = 0

b = {"a": "b"}
# access by string
b["a"] = "b"

c = 0
# access by name
a[c] = 1

# access by path
b.a = "b"


e = b.a + "foo"
