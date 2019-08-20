a = 0
http server as s
    b = 1
    when s listen path: "/" as req
        c = 2
        geo = (gmaps geocode address: req.query_params["city"])
        loc = "{geo.lat} {geo.lon}"
        req write content: loc
        d = 3
    e = 4
d = 5
