if (random list length: 10 type: "string") == (random list length: (random integer low:1 high:10) type: "{random string length: ((random boolean) as int)}")
    x = 0
else if (random integer low: 10 high: ("20" as int)) == (random integer low: (random integer low: 10 high:20+10) high: ("{random string length: ((random boolean) as int)}" as int))
    x = 1
