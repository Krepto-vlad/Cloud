import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


class TestFeedbackServiceRoutes(unittest.TestCase):

    def _get_patched_client(self):
        with patch("dotenv.dotenv_values") as mock_env, \
             patch("database.get_connection"), \
             patch("threading.Thread"):
            mock_env.return_value = {
                "SB_LISTEN_CONN_STR": "fake_listen_conn",
                "SB_QUEUE_NAME": "fake_queue",
                "DB_USERNAME": "u", "DB_PASSWORD": "p",
                "DB_SERVER": "s", "DB_DATABASE": "d",
            }
            import sys
            sys.modules.pop("main", None)
            import main as app_module
            return TestClient(app_module.app), app_module

    def test_root_returns_service_name(self):
        with patch("dotenv.dotenv_values") as mock_env, \
             patch("database.get_connection"), \
             patch("threading.Thread"):
            mock_env.return_value = {
                "SB_LISTEN_CONN_STR": "x", "SB_QUEUE_NAME": "q",
                "DB_USERNAME": "u", "DB_PASSWORD": "p",
                "DB_SERVER": "s", "DB_DATABASE": "d",
            }
            import sys
            sys.modules.pop("main", None)
            import main as app_module
            client = TestClient(app_module.app)
            response = client.get("/")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["service"], "Feedback Service")

    def test_get_all_feedback_returns_list(self):
        with patch("dotenv.dotenv_values") as mock_env, \
             patch("database.get_connection") as mock_conn, \
             patch("threading.Thread"):
            mock_env.return_value = {
                "SB_LISTEN_CONN_STR": "x", "SB_QUEUE_NAME": "q",
                "DB_USERNAME": "u", "DB_PASSWORD": "p",
                "DB_SERVER": "s", "DB_DATABASE": "d",
            }
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = [
                (1, 1, 1, "Great event!"),
                (2, 2, 1, "Loved it."),
            ]
            mock_conn.return_value.cursor.return_value = mock_cursor

            import sys
            sys.modules.pop("main", None)
            import main as app_module
            client = TestClient(app_module.app)
            response = client.get("/feedback")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(len(data), 2)
            self.assertEqual(data[0]["comments"], "Great event!")

    def test_get_feedback_not_found(self):
        with patch("dotenv.dotenv_values") as mock_env, \
             patch("database.get_connection") as mock_conn, \
             patch("threading.Thread"):
            mock_env.return_value = {
                "SB_LISTEN_CONN_STR": "x", "SB_QUEUE_NAME": "q",
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
            response = client.get("/feedback/999")
            self.assertEqual(response.status_code, 404)

    def test_get_feedback_by_tournament(self):
        with patch("dotenv.dotenv_values") as mock_env, \
             patch("database.get_connection") as mock_conn, \
             patch("threading.Thread"):
            mock_env.return_value = {
                "SB_LISTEN_CONN_STR": "x", "SB_QUEUE_NAME": "q",
                "DB_USERNAME": "u", "DB_PASSWORD": "p",
                "DB_SERVER": "s", "DB_DATABASE": "d",
            }
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = [
                (1, 1, 2, "Nice schedule"),
            ]
            mock_conn.return_value.cursor.return_value = mock_cursor

            import sys
            sys.modules.pop("main", None)
            import main as app_module
            client = TestClient(app_module.app)
            response = client.get("/feedback/tournament/2")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data[0]["tornamentId"], 2)

    def test_get_my_feedback(self):
        with patch("dotenv.dotenv_values") as mock_env, \
             patch("database.get_connection") as mock_conn, \
             patch("threading.Thread"):
            mock_env.return_value = {
                "SB_LISTEN_CONN_STR": "x", "SB_QUEUE_NAME": "q",
                "DB_USERNAME": "u", "DB_PASSWORD": "p",
                "DB_SERVER": "s", "DB_DATABASE": "d",
            }
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = [
                (1, 3, 1, "Awesome!"),
            ]
            mock_conn.return_value.cursor.return_value = mock_cursor

            import sys
            sys.modules.pop("main", None)
            import main as app_module
            client = TestClient(app_module.app)
            response = client.get("/feedback/my?user_id=3")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data[0]["userID"], 3)


if __name__ == "__main__":
    unittest.main()
