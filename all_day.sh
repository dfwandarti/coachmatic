# !/bin/bash

python3 70f803a5-408d-4c6d-88ea-a894e13a60c9.py  # jql:project in (SKO,SDHO) AND issuetype in (Bug, Spike, Story, Bug - Hotfix, GLPI - Causa Raiz) and status != Cancelado and  (status != Concluido or resolved > -90d)

python3 6475db40-942a-4c4f-999b-0d7ffd509642.py # jql:project = VIP and Impedido = Sim and created > startOfYear(-2) 

python3 b8a9afe7-2a2e-41e3-93e3-f9e3b86381a4.py # jql:project = EBANX and issuetype in (OS, Bug, Task) and status != Cancelado and (status != Done or resolved > -90d)


python3 effa6d6b-9874-4d3f-851f-24e4cc1fca0f.py # jql:project = VIP AND issuetype in ("Pedido de Suporte", "OS de Suporte", Bug) and status != Cancelado and (status not in (Done, Fechado) or resolved > -90d)

python3 13f23b9c-2376-41ec-ba41-e0b9584e19e8.py # jql:project = Vero AND issuetype in ("Pedido de Suporte") and status != Cancelado and (status not in (Done, Fechado) or resolved > -90d)

python3 fe45780f-fc50-4af8-afe5-59747b3f9847.py # jql:project = Vero AND issuetype in ("Pedido de Suporte", "OS de Suporte", Bug) and status != Cancelado and (status not in (Done, Fechado) or resolved > -90d)

python3 aa079632-ae27-4613-96fb-4b54d12e98cf.py # jql:project = Vero AND issuetype in (OS, Bug) and status != Cancelado and (status not in (Done, Fechado) or resolved > -90d)

python3 69b9505a-82e4-4ef0-8eca-71213a1be145.py # jql:project = VIP AND issuetype in (OS, Bug) and status != Cancelado and (status not in (Done, Fechado) or resolved > -90d)

