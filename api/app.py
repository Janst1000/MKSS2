from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from datetime import datetime

app = Flask(__name__)
api = Api(app)

# Datenstrukturen für Roboter und Items
robots = {
    1: {
        "id": 1,
        "position": {"x": 0, "y": 0},
        "energy": 100,
        "inventory": {},
        "actions": []
    },
    2: {
        "id": 2,
        "position": {"x": 1, "y": 1},
        "energy": 100,
        "inventory": {},
        "actions": []
    }
}

items = {
    1: {
        "id": 1,
        "position": {"x": 0, "y": 0},
    },
}

# Roboter-Status abrufen
class RobotStatus(Resource):
    def get(self, robot_id):
        robot = robots.get(robot_id)
        if robot:
            robot["actions"].append({"action": "status", "timestamp": datetime.now().isoformat()})
            robots[robot_id] = robot
            return jsonify(robot)
        return {"message": "Robot not found"}, 404

# Roboter bewegen
class RobotMove(Resource):
    def post(self, robot_id):
        data = request.get_json()
        direction = data.get("direction")
        robot = robots.get(robot_id)
        
        if not robot:
            return {"message": "Robot not found"}, 404

        # Bewegung des Roboters basierend auf der Richtung
        if direction == "up":
            robot["position"]["y"] += 1
        elif direction == "down":
            robot["position"]["y"] -= 1
        elif direction == "left":
            robot["position"]["x"] -= 1
        elif direction == "right":
            robot["position"]["x"] += 1
        else:
            return {"message": "Invalid direction"}, 400

        robots[robot_id] = robot
        robot["actions"].append({"action": "move", "direction": direction, "timestamp": datetime.now().isoformat()})
        return jsonify(robot)

# Roboter-Zustand aktualisieren
class RobotState(Resource):
    def patch(self, robot_id):
        data = request.get_json()
        robot = robots.get(robot_id)
        
        if not robot:
            return {"message": "Robot not found"}, 404

        # Aktualisieren des Energielevels und/oder Position
        if "energy" in data:
            robot["energy"] = data["energy"]
        if "position" in data:
            robot["position"] = data["position"]

        robots[robot_id] = robot
        robot["actions"].append({"action": "update_state", "data": data, "timestamp": datetime.now().isoformat()})
        return jsonify(robot)
    
# Roboter-Item aufheben
class RobotPickup(Resource):
    def post(self, robot_id, item_id):
        item = items.get(item_id)
        robot = robots.get(robot_id)
        
        if not robot:
            return {"message": "Robot not found"}, 404
        if not item:
            return {"message": "Item not found"}, 404

        robot_pos = robot["position"]
        item_pos = item["position"]
        if abs(robot_pos["x"] - item_pos["x"]) == 0 and abs(robot_pos["y"] - item_pos["y"]) == 0:
            robot["inventory"][item_id] = item
            items.pop(item_id)
            robot["actions"].append({"action": "pickup", "item": item, "timestamp": datetime.now().isoformat()})
            robots[robot_id] = robot
            return jsonify(robot)    
        else:    
            return {"message": "Item not in range"}, 400
    
class RobotPutDown(Resource):
    def post(self, robot_id, item_id):
        robot = robots.get(robot_id)
        item = robot['inventory'].get(item_id)        
        if not robot:
            return {"message": "Robot not found"}, 404
        if not item:
            return {"message": "Item not found"}, 404

        if item_id in robot["inventory"]:
            robot["inventory"].pop(item_id)
            item['position'] = robot['position'].copy()
            items[item_id] = item
            robot["actions"].append({"action": "drop", "item": item, "timestamp": datetime.now().isoformat()})
            robots[robot_id] = robot
            return jsonify(robot)        
        return {"message": "Item not in range"}, 400
    
class RobotGetActions(Resource):
    def get(self, robot_id):
        robot = robots.get(robot_id)
        if robot:
            return jsonify(robot["actions"])
        return {"message": "Robot not found"}, 404
    
class RobotAttack(Resource):
    def post(self, robot_id, target_id):
        robot = robots.get(robot_id)
        target = robots.get(target_id)
        if not robot:
            return {"message": "Robot not found"}, 404
        if not target:
            return {"message": "Target not found"}, 404
        if robot["energy"] < 5:
            return {"message": "Not enough energy"}, 400
        elif abs(robot["position"]["x"] - target["position"]["x"]) <= 1 and abs(robot["position"]["y"] - target["position"]["y"]) <= 1:
            robot["energy"] -= 5
            robot["actions"].append({"action": "attack", "target": target_id, "timestamp": datetime.now().isoformat()})
            robots[robot_id] = robot
            return jsonify(robot)

# Endpunkte registrieren
api.add_resource(RobotStatus, '/robots/<int:robot_id>/status')
api.add_resource(RobotMove, '/robots/<int:robot_id>/move')
api.add_resource(RobotState, '/robots/<int:robot_id>/state')
api.add_resource(RobotPickup, '/robots/<int:robot_id>/pickup/<int:item_id>')
api.add_resource(RobotPutDown, '/robots/<int:robot_id>/putdown/<int:item_id>')
api.add_resource(RobotGetActions, '/robots/<int:robot_id>/actions')
api.add_resource(RobotAttack, '/robots/<int:robot_id>/attack/<int:target_id>')

if __name__ == '__main__':
    app.run(debug=True)
