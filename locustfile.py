from locust import HttpUser, TaskSet, task, between
import random

class InventarioTasks(TaskSet):
    filtros = [
        {'q': 'SKU1', 'tipo': 'ingreso', 'desde': '2025-01-01', 'hasta': '2025-12-31', 'page_size': 100, 'page': 1},
        {'q': 'SKU2', 'tipo': 'salida', 'desde': '2025-01-01', 'hasta': '2025-12-31', 'page_size': 200, 'page': 2},
        {'q': 'SKU3', 'tipo': 'ajuste', 'desde': '2025-01-01', 'hasta': '2025-12-31', 'page_size': 300, 'page': 3},
        {'q': 'SKU4', 'tipo': 'devolucion', 'desde': '2025-01-01', 'hasta': '2025-12-31', 'page_size': 100, 'page': 2},
        {'q': 'SKU5', 'tipo': 'transferencia', 'desde': '2025-01-01', 'hasta': '2025-12-31', 'page_size': 200, 'page': 1},
        {'q': 'SKU6', 'tipo': '', 'desde': '2025-01-01', 'hasta': '2025-12-31', 'page_size': 300, 'page': 1},
    ]

    @task(2)
    def buscar_movimientos(self):
        filtro = random.choice(self.filtros)
        self.client.get("/movimientos/buscar-ajax/", params=filtro)

class InventarioUser(HttpUser):
    tasks = [InventarioTasks]
    wait_time = between(1, 3)
    host = "http://localhost:8000"  # Cambia el puerto si tu servidor usa otro
