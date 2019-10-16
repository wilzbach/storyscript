obj = {"abc@xyz.com": "Hello Mr. Abc"}
foreach obj.keys() as item
    mailgun send to: [item] from: "foo@bar.com" subject: "Spam" text: obj[item]
