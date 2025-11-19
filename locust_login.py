from locust import HttpUser, TaskSet, task, between
import random
import re

class LoginTasks(TaskSet):
    usuarios = [
        {"username": "fkeyla78@gmail.com", "password": "Ventana-123"},
      
        # Agrega más usuarios reales aquí
    ]

    def get_csrf_token(self):
        # Realiza un GET para obtener el token CSRF
        response = self.client.get("/login/")
        # Busca el token en el HTML
        match = re.search(r'name="csrfmiddlewaretoken" value="(.+?)"', response.text)
        if match:
            return match.group(1)
        return None

    @task(2)
    def login(self):
        user = random.choice(self.usuarios)
        csrf_token = self.get_csrf_token()
        if not csrf_token:
            print("No se pudo obtener el token CSRF")
            return
        data = {
            "username": user["username"],
            "password": user["password"],
            "csrfmiddlewaretoken": csrf_token
        }
        # Django espera el token CSRF en la cookie y en el POST
        headers = {"Referer": "http://localhost:8000/login/"}
        self.client.post("/login/", data=data, headers=headers)

class LoginUser(HttpUser):
    tasks = [LoginTasks]
    wait_time = between(1, 3)
    host = "http://localhost:8000"
