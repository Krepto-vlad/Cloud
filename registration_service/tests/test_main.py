import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

ENV = {
    "SB_SEND_CONN_STR": "fake",
    "SB_QUEUE_NAME": "q",
    "DB_USERNAME": "u", "DB_PASSWORD": "p",
    "DB_SERVER": "s", "DB_DATABASE": "d",
}


def _make_client(mock_env):
    mock_env.return_value = ENV
    import sys
    sys.modules.pop("main", None)
    import main as m
    return TestClient(m.app), m


class TestRegistrationServiceRoutes(unittest.TestCase):

    def test_root_returns_service_name(self):
        with patch("dotenv.dotenv_values") as me, patch("database.get_connection"):
            client, _ = _make_client(me)
            r = client.get("/")
            self.assertEqual(r.status_code, 200)
            self.assertEqual(r.json()["service"], "Registration Service")

    def test_get_users_returns_list(self):
        with patch("dotenv.dotenv_values") as me, \
             patch("database.get_connection") as mc:
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = [
                (1, "Alice", "alice@example.com"),
                (2, "Bob", "bob@example.com"),
            ]
            mc.return_value.cursor.return_value = mock_cursor
            client, _ = _make_client(me)
            r = client.get("/users")
            self.assertEqual(r.status_code, 200)
            self.assertEqual(len(r.json()), 2)
            self.assertEqual(r.json()[0]["name"], "Alice")

    def test_get_user_by_id_returns_correct_user(self):
        with patch("dotenv.dotenv_values") as me, \
             patch("database.get_connection") as mc:
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = (1, "Alice", "alice@example.com")
            mc.return_value.cursor.return_value = mock_cursor
            client, _ = _make_client(me)
            r = client.get("/users/1")
            self.assertEqual(r.status_code, 200)
            self.assertEqual(r.json()["email"], "alice@example.com")

    def test_get_user_not_found(self):
        with patch("dotenv.dotenv_values") as me, \
             patch("database.get_connection") as mc:
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = None
            mc.return_value.cursor.return_value = mock_cursor
            client, _ = _make_client(me)
            r = client.get("/users/999")
            self.assertEqual(r.status_code, 404)

    def test_get_registrations_returns_list(self):
        with patch("dotenv.dotenv_values") as me, \
             patch("database.get_connection") as mc:
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = [
                (1, 1, 1, "confirmed"),
                (2, 2, 1, "pending"),
            ]
            mc.return_value.cursor.return_value = mock_cursor
            client, _ = _make_client(me)
            r = client.get("/registrations")
            self.assertEqual(r.status_code, 200)
            self.assertEqual(len(r.json()), 2)

    def test_get_registration_by_id(self):
        with patch("dotenv.dotenv_values") as me, \
             patch("database.get_connection") as mc:
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = (1, 1, 1, "confirmed")
            mc.return_value.cursor.return_value = mock_cursor
            client, _ = _make_client(me)
            r = client.get("/registrations/1")
            self.assertEqual(r.status_code, 200)
            self.assertEqual(r.json()["status"], "confirmed")

    def test_get_registration_not_found(self):
        with patch("dotenv.dotenv_values") as me, \
             patch("database.get_connection") as mc:
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = None
            mc.return_value.cursor.return_value = mock_cursor
            client, _ = _make_client(me)
            r = client.get("/registrations/999")
            self.assertEqual(r.status_code, 404)

    def test_get_my_registrations_filters_by_user(self):
        with patch("dotenv.dotenv_values") as me, \
             patch("database.get_connection") as mc:
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = [(1, 5, 2, "pending")]
            mc.return_value.cursor.return_value = mock_cursor
            client, _ = _make_client(me)
            r = client.get("/me/registrations?user_id=5")
            self.assertEqual(r.status_code, 200)
            self.assertEqual(r.json()[0]["userID"], 5)

    def test_post_registration_status_is_pending(self):
        with patch("dotenv.dotenv_values") as me, \
             patch("database.get_connection") as mc, \
             patch("main.ServiceBusClient") as msb:
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = (42,)
            mc.return_value.__enter__ = lambda s: mc.return_value
            mc.return_value.__exit__ = MagicMock(return_value=False)
            mc.return_value.cursor.return_value = mock_cursor
            sb_inner = MagicMock()
            msb.from_connection_string.return_value.__enter__ = MagicMock(
                return_value=sb_inner
            )
            msb.from_connection_string.return_value.__exit__ = MagicMock(
                return_value=False
            )
            client, _ = _make_client(me)
            r = client.post("/registrations", json={"userID": 1, "tornamentId": 1})
            self.assertEqual(r.status_code, 201)
            self.assertEqual(r.json()["status"], "pending")
            self.assertEqual(r.json()["registerID"], 42)

    def test_post_registration_sb_failure_returns_503(self):
        with patch("dotenv.dotenv_values") as me, \
             patch("database.get_connection") as mc, \
             patch("main.ServiceBusClient") as msb:
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = (1,)
            mc.return_value.__enter__ = lambda s: mc.return_value
            mc.return_value.__exit__ = MagicMock(return_value=False)
            mc.return_value.cursor.return_value = mock_cursor
            msb.from_connection_string.side_effect = Exception("SB down")
            client, _ = _make_client(me)
            r = client.post("/registrations", json={"userID": 1, "tornamentId": 1})
            self.assertEqual(r.status_code, 503)

    def test_registration_model_requires_tournament_id(self):
        with patch("dotenv.dotenv_values") as me, patch("database.get_connection"):
            client, _ = _make_client(me)
            r = client.post("/registrations", json={"userID": 1})
            self.assertEqual(r.status_code, 422)

    def test_registration_model_fields(self):
        from pydantic import ValidationError
        import sys
        sys.modules.pop("main", None)
        with patch("dotenv.dotenv_values") as mock_env, \
             patch("database.get_connection"):
            mock_env.return_value = ENV
            import main as app_module
            reg = app_module.RegistrationCreate(userID=1, tornamentId=2)
            self.assertEqual(reg.userID, 1)
            self.assertEqual(reg.tornamentId, 2)
            with self.assertRaises(ValidationError):
                app_module.RegistrationCreate(userID="not_an_int", tornamentId=2)


if __name__ == "__main__":
    unittest.main()
