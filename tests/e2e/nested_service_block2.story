twitter stream
    when tweet track: "Storyscript" as ss
        x = 0
    http server
        when listen path:"/health" method:"get" as client
            x = 1
    when tweet track: "OMG" as omg
        x = 2
