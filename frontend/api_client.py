import requests

BASE_URL = "http://127.0.0.1:8000"

class APIClient:
    
    @staticmethod
    def get_clients():
        try:
            response = requests.get(f"{BASE_URL}/clients/")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка получения клиентов: {e}")
            return []

    # ДОБАВЛЯЕМ НОВЫЙ МЕТОД
    @staticmethod
    def create_client(client_data):
        try:
            # Отправляем POST запрос с данными клиента (JSON)
            response = requests.post(f"{BASE_URL}/clients/", json=client_data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при создании клиента: {e}")
            return None
    
    @staticmethod
    def delete_client(client_id):
        try:
            # Отправляем DELETE запрос
            response = requests.delete(f"{BASE_URL}/clients/{client_id}")
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при удалении клиента: {e}")
            return False
    
    @staticmethod
    def get_pets_by_client(client_id):
        """Скачивает питомцев конкретного клиента"""
        try:
            response = requests.get(f"{BASE_URL}/pets/client/{client_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка получения питомцев: {e}")
            return []

    @staticmethod
    def create_pet(pet_data):
        """Отправляет данные нового питомца на сервер"""
        try:
            response = requests.post(f"{BASE_URL}/pets/", json=pet_data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при создании питомца: {e}")
            return None
    
    @staticmethod
    def delete_pet(pet_id):
        try:
            response = requests.delete(f"{BASE_URL}/pets/{pet_id}")
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при удалении питомца: {e}")
            return False
    @staticmethod
    def get_doctors():
        try:
            response = requests.get(f"{BASE_URL}/doctors/")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка получения списка врачей: {e}")
            return []

    @staticmethod
    def create_doctor(doctor_data):
        try:
            response = requests.post(f"{BASE_URL}/doctors/", json=doctor_data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при добавлении врача: {e}")
            return None

    @staticmethod
    def delete_doctor(doctor_id):
        try:
            response = requests.delete(f"{BASE_URL}/doctors/{doctor_id}")
            response.raise_for_status()
            return True, "Врач успешно удален" # Возвращаем статус и сообщение успеха
        except requests.exceptions.HTTPError as e:
            # Если сервер вернул ошибку (например, наши 400 Bad Request)
            if e.response is not None and e.response.status_code == 400:
                try:
                    # Вытаскиваем сообщение "detail", которое мы написали в роутере на бэкенде
                    error_msg = e.response.json().get("detail", "Не удалось удалить врача.")
                    return False, error_msg
                except Exception:
                    pass
            return False, f"Ошибка сервера: {e}"
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при удалении врача: {e}")
            return False, "Ошибка подключения к серверу"
    
    @staticmethod
    def get_pets():
        """Получает список всех питомцев (нужно для выпадающего списка при записи)"""
        try:
            response = requests.get(f"{BASE_URL}/pets/")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка получения списка питомцев: {e}")
            return []

    @staticmethod
    def get_appointments_by_date(target_date):
        """Получает расписание записей на конкретную дату (строка 'YYYY-MM-DD')"""
        try:
            response = requests.get(f"{BASE_URL}/appointments/date/{target_date}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка получения расписания: {e}")
            return []

    @staticmethod
    def create_appointment(appointment_data):
        """Отправляет новую запись на прием на сервер"""
        try:
            response = requests.post(f"{BASE_URL}/appointments/", json=appointment_data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при создании записи: {e}")
            return None
    
    @staticmethod
    def delete_appointment(appointment_id):
        """Отправляет запрос на удаление записи"""
        try:
            response = requests.delete(f"{BASE_URL}/appointments/{appointment_id}")
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при отмене записи: {e}")
            return False
        
    @staticmethod
    def get_appointment(appointment_id):
        """Скачивает данные конкретной карточки приема"""
        try:
            response = requests.get(f"{BASE_URL}/appointments/{appointment_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка получения записи: {e}")
            return None

    @staticmethod
    def update_appointment(appointment_id, data):
        """Отправляет медицинские данные для обновления карты"""
        try:
            response = requests.put(f"{BASE_URL}/appointments/{appointment_id}", json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при сохранении медкарты: {e}")
            return None