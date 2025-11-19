from locust import HttpUser, TaskSet, task, between
import random

class ProveedoresTasks(TaskSet):
    filtros = [
        {"q": "Proveedor1", "estado": "ACTIVO", "page_size": 100, "page": 1},
        {"q": "Proveedor2", "estado": "INACTIVO", "page_size": 200, "page": 2},
        {"q": "Proveedor3", "estado": "ACTIVO", "page_size": 300, "page": 3},
        {"q": "Proveedor4", "estado": "", "page_size": 100, "page": 2},
        {"q": "Proveedor5", "estado": "ACTIVO", "page_size": 200, "page": 1},
        {"q": "Proveedor6", "estado": "INACTIVO", "page_size": 300, "page": 1},
    ]

    @task(2)
    def buscar_proveedores(self):
        filtro = random.choice(self.filtros)
        self.client.get("/proveedores/buscar-ajax/", params=filtro)

class ProveedoresUser(HttpUser):
    tasks = [ProveedoresTasks]
    wait_time = between(1, 3)
    host = "http://localhost:8000"
