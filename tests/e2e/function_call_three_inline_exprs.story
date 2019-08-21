p1 = yaml parse data: "abc@xyz.com"
p2 = yaml parse data: "ss@storyscript.com"
p3 = yaml parse data: "Testing"
mailgun send to: (yaml format data: p1) from: (yaml format data: p2) subject: (yaml format data: p3)
