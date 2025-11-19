from locust import HttpUser, TaskSet, task, between
import random

class ProductosTasks(TaskSet):
    filtros = [
        {"q": "SKU1", "categoria_id": 1, "page_size": 100, "page": 1},  # Chocolates
        {"q": "SKU2", "categoria_id": 2, "page_size": 200, "page": 2},  # Dulces
        {"q": "SKU3", "categoria_id": 1, "page_size": 300, "page": 3},
        {"q": "SKU4", "categoria_id": 2, "page_size": 100, "page": 2},
        {"q": "SKU5", "categoria_id": 1, "page_size": 200, "page": 1},
        {"q": "SKU6", "categoria_id": 2, "page_size": 300, "page": 1},
    ]

    @task(2)
    def buscar_productos(self):
        filtro = random.choice(self.filtros)
        self.client.get("/productos/buscar-ajax/", params=filtro)

class ProductosUser(HttpUser):
    tasks = [ProductosTasks]
    wait_time = between(1, 3)
    host = "http://localhost:8000"
