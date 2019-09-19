slack bot
    when hears channel: "foobar" as msg
        a = "foo {(random string length:10) as string + msg as string}"
