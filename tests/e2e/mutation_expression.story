req = http fetch url: "foobar"
a = ["opened", "labeled"]
b = a.contains(item: req.body["action"])
