if (if_service1 command p1:(if_service11 call arg:1) p2: (if_service12 call arg:2)) == (if_service2 command p1:(if_service21 call arg:1) p2: (if_service22 call arg:2))
    x = 0
else if (else_service1 command p1:(else_service11 call arg:1) p2: (else_service12 call arg:2)) == (else_service2 command p1:(else_service21 call arg:1) p2: (else_service22 call arg:2))
    x = 1
else
    x = 2

x = 3
