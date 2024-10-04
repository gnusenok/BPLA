# Исполнил Дашкин В.Р.
# БПЛА256_2-2
# Руководитель Максимов Е.В.
from flask import Flask, request, jsonify, send_from_directory
import random
import logging

app = Flask(__name__, static_folder='static')

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

logger = logging.getLogger()


# Класс данных дрона (Model)
class DroneControlSystem:
    """Класс для управления данными дрона."""

    def __init__(self):
        self.altitude = 0
        self.speed = 0
        self.position = (0, 0)
        self.battery = 100
        self.direction = 0  # направление движения дрона в градусах
        self.log = []  # история действий

    def update_position(self, x, y):
        self.position = (x, y)
        self.log_action(f"Position updated to {self.position}")

    def change_altitude(self, altitude):
        self.altitude = altitude
        self.log_action(f"Altitude changed to {self.altitude} meters")

    def update_speed(self, speed):
        self.speed = speed
        self.log_action(f"Speed updated to {self.speed} m/s")

    def change_direction(self, direction):
        self.direction = direction
        self.log_action(f"Direction changed to {self.direction} degrees")

    def consume_battery(self, consumption):
        self.battery -= consumption
        self.log_action(f"Battery consumed. Current level: {self.battery}%")

    def check_battery(self):
        return self.battery

    def log_action(self, action):
        """Логирование действия дрона."""
        logger.info(action)
        self.log.append(action)

    def get_log(self):
        """Получить историю действий."""
        return self.log


# Класс представления (View)
class DroneInterface:
    """Класс для отображения информации о дроне и взаимодействия с пользователем."""

    def show_status(self, drone_model):
        return {
            'altitude': drone_model.altitude,
            'speed': drone_model.speed,
            'position': drone_model.position,
            'battery': drone_model.battery,
            'direction': drone_model.direction
        }

    def display_alert(self, message):
        return {"alert": message}


# Контроллер для управления логикой
class DroneOperations:
    """Контроллер для управления поведением дрона."""

    def __init__(self, model, view):
        self.model = model
        self.view = view

    def adjust_position(self, x, y):
        self.model.update_position(x, y)
        return self.view.show_status(self.model)

    def adjust_altitude(self, altitude):
        self.model.change_altitude(altitude)
        return self.view.show_status(self.model)

    def adjust_speed(self, speed):
        self.model.update_speed(speed)
        return self.view.show_status(self.model)

    def adjust_direction(self, direction):
        self.model.change_direction(direction)
        return self.view.show_status(self.model)

    def monitor_battery(self):
        if self.model.check_battery() < 20:
            return self.view.display_alert("Battery low! Returning to base.")
        return self.view.show_status(self.model)

    def get_log(self):
        return {"log": self.model.get_log()}


# Симуляция сенсоров
class SensorSimulation:
    """Класс для симуляции сенсоров."""

    def simulate_obstacle(self):
        distance_to_obstacle = random.uniform(0, 50)  # Случайное расстояние до препятствия
        return distance_to_obstacle

    def simulate_weather_conditions(self):
        wind_speed = random.uniform(0, 20)  # Случайная скорость ветра
        weather_conditions = random.choice(["Clear", "Cloudy", "Stormy", "Rainy"])
        return {"wind_speed": wind_speed, "weather": weather_conditions}


# Инициализация дрона и контроллера
drone_model = DroneControlSystem()
drone_view = DroneInterface()
drone_controller = DroneOperations(drone_model, drone_view)
sensor_simulator = SensorSimulation()


@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')


# API для получения статуса дрона
@app.route('/status', methods=['GET'])
def get_status():
    return jsonify(drone_view.show_status(drone_model))


# API для обновления позиции дрона
@app.route('/position', methods=['POST'])
def update_position():
    data = request.get_json()
    x, y = data.get('x', 0), data.get('y', 0)
    return jsonify(drone_controller.adjust_position(x, y))


# API для обновления высоты дрона
@app.route('/altitude', methods=['POST'])
def update_altitude():
    data = request.get_json()
    altitude = data.get('altitude', 0)
    return jsonify(drone_controller.adjust_altitude(altitude))


# API для обновления скорости дрона
@app.route('/speed', methods=['POST'])
def update_speed():
    data = request.get_json()
    speed = data.get('speed', 0)
    return jsonify(drone_controller.adjust_speed(speed))


# API для проверки заряда батареи
@app.route('/battery', methods=['GET'])
def check_battery():
    return jsonify(drone_controller.monitor_battery())


# API для симуляции препятствий
@app.route('/simulate_obstacle', methods=['GET'])
def simulate_obstacle():
    obstacle_distance = sensor_simulator.simulate_obstacle()
    if obstacle_distance < 10:
        return jsonify(
            drone_view.display_alert(f"Obstacle detected {obstacle_distance} meters away! Adjusting course..."))
    return jsonify({"obstacle_distance": obstacle_distance})


# API для симуляции погодных условий
@app.route('/simulate_weather', methods=['GET'])
def simulate_weather():
    weather = sensor_simulator.simulate_weather_conditions()
    return jsonify(weather)


# API для получения истории действий дрона
@app.route('/log', methods=['GET'])
def get_log():
    return jsonify(drone_controller.get_log())


if __name__ == '__main__':
    app.run(debug=True)
