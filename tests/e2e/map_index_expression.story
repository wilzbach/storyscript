a = {"foo": {"bar": 1}, "bar": {"foo": 0}, "foobar": 2}
a[a["bar"].keys()[0] + a["foo"].keys()[0]]
# Equivalent statement
a["foo" + "bar"]
