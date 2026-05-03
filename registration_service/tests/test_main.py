import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


class TestRegistrationServiceRoutes(unittest.TestCase):

    def _make_client(self):
        # Patch DB and SB env so main.py can be imported without real connections
        with patch.dict("os.environ", {}):
            with patch("dotenv.dotenv_values") as mock_env:
                mock_env.return_value = {
                    "SB_SEND_CONN_STR": "fake_send_conn",
                    "SB_QUEUE_NAME": "fake_queue",
                    "DB_USERNAME": "u", "DB_PASSWORD": "p",
                    "DB_SERVER": "s", "DB_DATABASE": "d",
                }
                import importlib, sys
                # Ensure fresh import
                for mod in ["main", "database"]:
                    sys.modules.pop(f"registration_service.{mod}", None)
                    sys.modules.pop(mod, None)
                import main as app_module
                return TestClient(app_module.app), app_module

    def test_root_returns_service_name(self):
        with patch("dotenv.dotenv_values") as mock_env, \
             patch("database.get_connection"):
            mock_env.return_value = {
                "SB_SEND_CONN_STR": "x", "SB_QUEUE_NAME": "q",
                "DB_USERNAME": "u", "DB_PASSWORD": "p",
                "DB_SERVER": "s", "DB_DATABASE": "d",
            }
            import sys
            sys.modules.pop("main", None)
            import main as app_module
            client = TestClient(app_module.app)
            response = client.get("/")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["service"], "Registration Service")

    def test_get_users_returns_list(self):
        with patch("dotenv.dotenv_values") as mock_env, \
             patch("database.get_connection") as mock_conn:
            mock_env.return_value = {
                "SB_SEND_CONN_STR": "x", "SB_QUEUE_NAME": "q",
                "DB_USERNAME": "u", "DB_PASSWORD": "p",
                "DB_SERVER": "s", "DB_DATABASE": "d",
            }
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = [
                (1, "Alice", "alice@example.com"),
                (2, "Bob", "bob@example.com"),
            ]
            mock_conn.return_value.cursor.return_value = mock_cursor

            import sys
            sys.modules.pop("main", None)
            import main as app_module
            client = TestClient(app_module.app)
            response = client.get("/users")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIsInstance(data, list)
            self.assertEqual(len(data), 2)
            self.assertEqual(data[0]["name"], "Alice")

    def test_get_user_not_found(self):
        with patch("dotenv.dotenv_values") as mock_env, \
             patch("database.get_connection") as mock_conn:
            mock_env.return_value = {
                "SB_SEND_CONN_STR": "x", "SB_QUEUE_NAME": "q",
                "DB_USERNAME": "u", "DB_PASSWORD": "p",
                "DB_SERVER": "s", "DB_DATABASE": "d",
            }
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = None
            mock_conn.return_value.cursor.return_value = mock_cursor

            import sys
            sys.modules.pop("main", None)
            import main as app_module
            client = TestClient(app_module.app)
            response = client.get("/users/999")
            self.assertEqual(response.status_code, 404)

    def test_get_registrations_returns_list(self):
        with patch("dotenv.dotenv_values") as mock_env, \
             patch("database.get_connection") as mock_conn:
            mock_env.return_value = {
                "SB_SEND_CONN_STR": "x", "SB_QUEUE_NAME": "q",
                "DB_USERNAME": "u", "DB_PASSWORD": "p",
                "DB_SERVER": "s", "DB_DATABASE": "d",
            }
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = [
                (1, 1, 1, "confirmed"),
                (2, 2, 1, "pending"),
            ]
            mock_conn.return_value.cursor.return_value = mock_cursor

            import sys
            sys.modules.pop("main", None)
            import main as app_module
            client = TestClient(app_module.app)
            response = client.get("/registrations")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json()), 2)

    def test_registration_model_fields(self):
        from pydantic import ValidationError
        import sys
        sys.modules.pop("main", None)
        with patch("dotenv.dotenv_values") as mock_env, \
             patch("database.get_connection"):
            mock_env.return_value = {
                "SB_SEND_CONN_STR": "x", "SB_QUEUE_NAME": "q",
                "DB_USERNAME": "u", "DB_PASSWORD": "p",
                "DB_SERVER": "s", "DB_DATABASE": "d",
            }
            import main as app_module
            # Valid model
            reg = app_module.RegistrationCreate(userID=1, tornamentId=2)
            self.assertEqual(reg.userID, 1)
            self.assertEqual(reg.tornamentId, 2)
            # Invalid model
            with self.assertRaises(ValidationError):
                app_module.RegistrationCreate(userID="not_an_int", tornamentId=2)


if __name__ == "__main__":
    unittest.main()
