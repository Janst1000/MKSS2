import unittest
import json
from app import create_app, get_initial_state

class RobotApiTestCase(unittest.TestCase):
    def setUp(self):
        # Create a new instance of the app and test client for each test
        self.app = create_app().test_client()
        self.app.testing = True

    def test_get_robot_status(self):
        response = self.app.get('/robots/1/status')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertIn("id", data)
        self.assertIn("position", data)
        self.assertIn("energy", data)
        self.assertIn("inventory", data)
        self.assertIn("links", data)

    def test_post_robot_move(self):
        # Move the robot up
        response = self.app.post('/robots/1/move', json={"direction": "up"})
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertIn("position", data)
        self.assertEqual(data["position"]["y"], 1)  # Since robot initially starts at y=0

    def test_post_robot_pickup(self):
        # Ensure the item and robot are in the same position
        response = self.app.post('/robots/1/pickup/1')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertIn("inventory", data)
        self.assertIn("1", data["inventory"])  # Check that item 1 is now in inventory

    def test_post_robot_putdown(self):
        # First, pick up the item so we can put it down
        self.app.post('/robots/1/pickup/1')
        
        # Then put down the item
        response = self.app.post('/robots/1/putdown/1')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertNotIn("1", data["inventory"])  # Check that item 1 is no longer in inventory

    def test_post_robot_attack(self):
        # Move robot 2 to be near robot 1 for attack
        self.app.post('/robots/2/move', json={"direction": "left"})
        
        # Attack robot 2 from robot 1
        response = self.app.post('/robots/1/attack/2')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertIn("energy", data)
        self.assertEqual(data["energy"], 95)  # Attack cost 5 energy

    def test_get_robot_actions(self):
        # Get the first page of actions
        response = self.app.get('/robots/1/actions?page=1&size=5')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertIn("actions", data)
        self.assertIn("page", data)
        self.assertIn("links", data)
        
        # Check pagination fields
        self.assertEqual(data["page"]["number"], 1)
        self.assertEqual(data["page"]["size"], 5)

    def test_get_single_action(self):
        # Add an action
        self.app.post('/robots/1/move', json={"direction": "up"})
        
        # Retrieve that specific action
        response = self.app.get('/robots/1/actions/0')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertIn("action", data)
        self.assertEqual(data["action"]["action"], "move")
        self.assertEqual(data["action"]["direction"], "up")

if __name__ == '__main__':
    unittest.main()