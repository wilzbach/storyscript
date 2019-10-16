if (random list length: 10 type: "string") == (random list length: (random integer low:1 high:10) type: "{random string length: ((random boolean) to int)}")
    x = 0
else if (random integer low: 10 high: ("20" to int)) == (random integer low: (random integer low: 10 high:20+10) high: ("{random string length: ((random boolean) to int)}" to int))
    x = 1
