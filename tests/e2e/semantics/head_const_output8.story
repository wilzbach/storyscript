http server as client
    when client listen method:"post" path:"/foo" as res
        v = res
        v.body = 2
