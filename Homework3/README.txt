Integrantes:
Ignacio Quintana 201973610-8
Héctor Arteaga 201973564-0


Instrucciones de ejecución:

RED 1:
    archivos:
        l2_learning.py
        topology_R1.py

    controlador:
        python3 pox.py log.level --DEBUG misc.full_payload tarea3.l2_learning openflow.discovery openflow.spanning_tree --no-flood --hold-down

    mininet:
        mn --custom topology_R1.py --topo MyTopo --mac --controller remote --switch ovsk

RED 2:
    archivos:
        controller.py
        topology_R2.py

    controlador:
        python3 pox.py log.level --DEBUG misc.full_payload tarea3.controller tarea3.firewall --ports=80 openflow.discovery openflow.spanning_tree --no-flood --hold-down

    mininet:
        mn --custom topology_R2.py --topo MyTopo --mac --controller remote --switch ovsk

