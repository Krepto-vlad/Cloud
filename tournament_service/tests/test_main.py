import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

ENV = {
    "DB_USERNAME": "u", "DB_PASSWORD": "p",
    "DB_SERVER": "s", "DB_DATABASE": "d",
}


def _make_client(mock_env):
    mock_env.return_value = ENV
    import sys
    sys.modules.pop("main", None)
    import main as m
    return TestClient(m.app), m


class TestTournamentServiceRoutes(unittest.TestCase):

    def test_root_returns_service_name(self):
        with patch("dotenv.dotenv_values") as me, patch("database.get_connection"):
            client, _ = _make_client(me)
            r = client.get("/")
            self.assertEqual(r.status_code, 200)
            self.assertEqual(r.json()["service"], "Tournament Service")

    def test_get_tournaments_returns_list(self):
        with patch("dotenv.dotenv_values") as me, \
             patch("database.get_connection") as mc:
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = [
                (1, "Spring Open", "2026-04-20", "NYC"),
                (2, "Summer League", "2026-06-15", "LA"),
            ]
            mc.return_value.cursor.return_value = mock_cursor
            client, _ = _make_client(me)
            r = client.get("/tournaments")
            self.assertEqual(r.status_code, 200)
            data = r.json()
            self.assertEqual(len(data), 2)
            self.assertEqual(data[0]["name"], "Spring Open")

    def test_get_tournament_by_id(self):
        with patch("dotenv.dotenv_values") as me, \
             patch("database.get_connection") as mc:
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = (1, "Spring Open", "2026-04-20", "NYC")
            mc.return_value.cursor.return_value = mock_cursor
            client, _ = _make_client(me)
            r = client.get("/tournaments/1")
            self.assertEqual(r.status_code, 200)
            self.assertEqual(r.json()["location"], "NYC")

    def test_get_tournament_not_found(self):
        with patch("dotenv.dotenv_values") as me, \
             patch("database.get_connection") as mc:
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = None
            mc.return_value.cursor.return_value = mock_cursor
            client, _ = _make_client(me)
            r = client.get("/tournaments/999")
            self.assertEqual(r.status_code, 404)

    def test_get_tournament_schedule_returns_list(self):
        with patch("dotenv.dotenv_values") as me, \
             patch("database.get_connection") as mc:
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = [
                (1, 1, "2026-04-21 09:00", "Quarter-finals"),
                (2, 2, "2026-04-23 09:00", "Semi-finals"),
            ]
            mc.return_value.cursor.return_value = mock_cursor
            client, _ = _make_client(me)
            r = client.get("/tournaments/1/schedule")
            self.assertEqual(r.status_code, 200)
            data = r.json()
            self.assertEqual(len(data), 2)
            self.assertEqual(data[0]["description"], "Quarter-finals")

    def test_get_tournament_schedule_empty(self):
        with patch("dotenv.dotenv_values") as me, \
             patch("database.get_connection") as mc:
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = []
            mc.return_value.cursor.return_value = mock_cursor
            client, _ = _make_client(me)
            r = client.get("/tournaments/99/schedule")
            self.assertEqual(r.status_code, 200)
            self.assertEqual(r.json(), [])

    def test_get_tournament_matches_returns_list(self):
        with patch("dotenv.dotenv_values") as me, \
             patch("database.get_connection") as mc:
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = [
                (1, "Alice", "Bob", "2026-04-21 10:00", "Alice"),
                (2, "Carol", "David", "2026-04-21 12:00", None),
            ]
            mc.return_value.cursor.return_value = mock_cursor
            client, _ = _make_client(me)
            r = client.get("/tournaments/1/matches")
            self.assertEqual(r.status_code, 200)
            data = r.json()
            self.assertEqual(data[0]["participant1"], "Alice")
            self.assertEqual(data[0]["result"], "Alice")
            self.assertIsNone(data[1]["result"])

    def test_get_tournament_matches_empty(self):
        with patch("dotenv.dotenv_values") as me, \
             patch("database.get_connection") as mc:
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = []
            mc.return_value.cursor.return_value = mock_cursor
            client, _ = _make_client(me)
            r = client.get("/tournaments/99/matches")
            self.assertEqual(r.status_code, 200)
            self.assertEqual(r.json(), [])

    def test_tournaments_response_has_correct_fields(self):
        with patch("dotenv.dotenv_values") as me, \
             patch("database.get_connection") as mc:
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = [
                (1, "Spring Open", "2026-04-20", "NYC"),
            ]
            mc.return_value.cursor.return_value = mock_cursor
            client, _ = _make_client(me)
            r = client.get("/tournaments")
            item = r.json()[0]
            self.assertIn("tornamentsID", item)
            self.assertIn("name", item)
            self.assertIn("Date", item)
            self.assertIn("location", item)


if __name__ == "__main__":
    unittest.main()


    def _get_client(self):
        with patch("dotenv.dotenv_values") as mock_env, \
             patch("database.get_connection"):
            mock_env.return_value = {
                "DB_USERNAME": "u", "DB_PASSWORD": "p",
                "DB_SERVER": "s", "DB_DATABASE": "d",
