http server as client
    when client listen method:"get" path:"/" as request
        a = (gmaps geocode address: "Venice").lat + (random integer low: 1 high: 10)
