import io
import os
import sys
import unittest
from unittest.mock import patch


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret")
os.environ.setdefault("ADMIN_SECRET_KEY", "test-admin-secret")
os.environ.setdefault("USER_SECRET_KEY", "test-user-secret")

from fastapi.testclient import TestClient

from app.app import app


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def get_token(self, secret):
        response = self.client.post("/login", json={"secret_key": secret})
        self.assertEqual(response.status_code, 200)
        return response.json()["access_token"]

    def test_login_rejects_invalid_secret(self):
        response = self.client.post("/login", json={"secret_key": "wrong"})
        self.assertEqual(response.status_code, 401)

    @patch("app.app.perform_face_search")
    @patch("app.app.save_upload_file")
    @patch("app.app.os.remove")
    @patch("app.app.os.listdir")
    def test_search_face_returns_ranked_results(self, mock_listdir, mock_remove, mock_save, mock_search):
        token = self.get_token("test-user-secret")
        mock_save.return_value = os.path.join(ROOT_DIR, "uploads", "query-file.jpg")
        mock_search.return_value = [
            {"face": "event-photo_face1.jpg", "distance": 0.91},
            {"face": "other-photo_face1.jpg", "distance": 0.22},
        ]
        mock_listdir.return_value = ["event-photo.jpg", "other-photo.jpg"]

        response = self.client.post(
            "/search-face",
            files={"file": ("person.jpg", io.BytesIO(b"fake"), "image/jpeg")},
            headers={"Authorization": f"Bearer {token}"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["matches"], ["event-photo.jpg"])
        self.assertEqual(payload["results"][0]["filename"], "event-photo.jpg")
        self.assertEqual(payload["results"][0]["score"], 0.91)
        mock_remove.assert_called_once()

    @patch("app.app.initialize_job")
    @patch("app.app.celery_app.send_task")
    @patch("app.app.save_upload_file")
    def test_admin_upload_queues_background_job(self, mock_save, mock_send_task, mock_initialize_job):
        token = self.get_token("test-admin-secret")
        mock_save.side_effect = [
            os.path.join(ROOT_DIR, "data", "raw_images", "event-a.jpg"),
            os.path.join(ROOT_DIR, "data", "raw_images", "event-b.jpg"),
        ]

        response = self.client.post(
            "/admin/upload-images",
            files=[
                ("files", ("event-a.jpg", io.BytesIO(b"a"), "image/jpeg")),
                ("files", ("event-b.png", io.BytesIO(b"b"), "image/png")),
            ],
            headers={"Authorization": f"Bearer {token}"},
        )

        self.assertEqual(response.status_code, 202)
        payload = response.json()
        self.assertEqual(payload["status"], "queued")
        self.assertEqual(payload["images_received"], 2)
        mock_initialize_job.assert_called_once()
        mock_send_task.assert_called_once()

    @patch("app.app.initialize_job")
    @patch("app.app.celery_app.send_task")
    def test_drive_import_queues_background_job(self, mock_send_task, mock_initialize_job):
        token = self.get_token("test-admin-secret")

        response = self.client.post(
            "/admin/import-drive",
            json={"drive_folder_id": "folder123"},
            headers={"Authorization": f"Bearer {token}"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "queued")
        mock_initialize_job.assert_called_once()
        mock_send_task.assert_called_once_with("process_drive_folder", args=[unittest.mock.ANY, "folder123"])

    @patch("app.app.get_job_status")
    def test_job_status_returns_structured_progress(self, mock_get_job_status):
        token = self.get_token("test-admin-secret")
        mock_get_job_status.return_value = {
            "job_id": "job-1",
            "job_type": "upload",
            "status": "processing",
            "images_received": 3,
            "images_downloaded": 0,
            "faces_indexed": 7,
            "error": None,
        }

        response = self.client.get(
            "/admin/job-status/job-1",
            headers={"Authorization": f"Bearer {token}"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["faces_indexed"], 7)


if __name__ == "__main__":
    unittest.main()
