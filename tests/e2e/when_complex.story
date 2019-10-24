twitter stream
    when tweet as t
        log info msg: "breaking"
    when tweet track: "storyscript"
        log info msg: "breaking"
    when tweet track: "storyscript" as t
        log info msg: "breaking"

twitter stream as s
    when s tweet
        log info msg: "breaking"
    when s tweet as t
        log info msg: "breaking"
    when s tweet track: "storyscript"
        log info msg: "breaking"
    when s tweet track: "storyscript" as t
        log info msg: "breaking"
