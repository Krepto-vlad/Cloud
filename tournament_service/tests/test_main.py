import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


class TestTournamentServiceRoutes(unittest.TestCase):

    def _get_client(self):
        with patch("dotenv.dotenv_values") as mock_env, \
             patch("database.get_connection"):
            mock_env.return_value = {
                "DB_USERNAME": "u", "DB_PASSWORD": "p",
                "DB_SERVER": "s", "DB_DATABASE": "d",
            }
            import sys
            sys.modules.pop("main", None)
            import main as app_module
            return TestClient(app_module.app), app_module

    def test_root_returns_service_name(self):
        with patch("dotenv.dotenv_values") as mock_env, \
             patch("database.get_connection"):
            mock_env.return_value = {
                "DB_USERNAME": "u", "DB_PASSWORD": "p",
                "DB_SERVER": "s", "DB_DATABASE": "d",
            }
            import sys
            sys.modules.pop("main", None)
            import main as app_module
            client = TestClient(app_module.app)
            response = client.get("/")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["service"], "Tournament Service")

    def test_get_tournaments_returns_list(self):
        with patch("dotenv.dotenv_values") as mock_env, \
             patch("database.get_connection") as mock_conn:
            mock_env.return_value = {
                "DB_USERNAME": "u", "DB_PASSWORD": "p",
                "DB_SERVER": "s", "DB_DATABASE": "d",
            }
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = [
                (1, "Spring Open", "2026-04-20", "NYC"),
                (2, "Summer League", "2026-06-15", "LA"),
            ]
            mock_conn.return_value.cursor.return_value = mock_cursor

            import sys
            sys.modules.pop("main", None)
            import main as app_module
            client = TestClient(app_module.app)
            response = client.get("/tournaments")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(len(data), 2)
            self.assertEqual(data[0]["name"], "Spring Open")

    def test_get_tournament_not_found(self):
        with patch("dotenv.dotenv_values") as mock_env, \
             patch("database.get_connection") as mock_conn:
            mock_env.return_value = {
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
            response = client.get("/tournaments/999")
            self.assertEqual(response.status_code, 404)

    def test_get_tournament_schedule_returns_list(self):
        with patch("dotenv.dotenv_values") as mock_env, \
             patch("database.get_connection") as mock_conn:
            mock_env.return_value = {
                "DB_USERNAME": "u", "DB_PASSWORD": "p",
                "DB_SERVER": "s", "DB_DATABASE": "d",
            }
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = [
                (1, 1, "2026-04-21 09:00", "Quarter-finals"),
            ]
            mock_conn.return_value.cursor.return_value = mock_cursor

            import sys
            sys.modules.pop("main", None)
            import main as app_module
            client = TestClient(app_module.app)
            response = client.get("/tournaments/1/schedule")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data[0]["description"], "Quarter-finals")

    def test_get_tournament_matches_returns_list(self):
        with patch("dotenv.dotenv_values") as mock_env, \
             patch("database.get_connection") as mock_conn:
            mock_env.return_value = {
                "DB_USERNAME": "u", "DB_PASSWORD": "p",
                "DB_SERVER": "s", "DB_DATABASE": "d",
            }
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = [
                (1, "Alice", "Bob", "2026-04-21 10:00", "Alice"),
            ]
            mock_conn.return_value.cursor.return_value = mock_cursor

            import sys
            sys.modules.pop("main", None)
            import main as app_module
            client = TestClient(app_module.app)
            response = client.get("/tournaments/1/matches")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data[0]["participant1"], "Alice")


if __name__ == "__main__":
    unittest.main()
