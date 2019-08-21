req = http fetch url: "foobar"
a = ["opened", "labeled"]
a.contains(item: req.body["action"])
