http server as s
    when s listen path: "/" as r
        a = s.data["foobar"]
