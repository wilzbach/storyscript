foreach (random list type: "string" length: 10) as item
    mailgun send to: item from: "foo@bar.com" subject:"Spam!!"
