import io
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

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

    # ─────────────────────────────────────────────
    # Auth / Login
    # ─────────────────────────────────────────────

    def test_login_admin_returns_token_and_role(self):
        """POSITIVE: Admin secret returns access_token with role=admin"""
        response = self.client.post("/login", json={"secret_key": "test-admin-secret"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["role"], "admin")

    def test_login_user_returns_token_and_role(self):
        """POSITIVE: User secret returns access_token with role=user"""
        response = self.client.post("/login", json={"secret_key": "test-user-secret"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["role"], "user")

    def test_login_rejects_invalid_secret(self):
        """NEGATIVE: Wrong password returns 401"""
        response = self.client.post("/login", json={"secret_key": "wrong"})
        self.assertEqual(response.status_code, 401)

    def test_login_rejects_empty_secret(self):
        """NEGATIVE: Empty string password returns 401"""
        response = self.client.post("/login", json={"secret_key": ""})
        self.assertEqual(response.status_code, 401)

    def test_login_rejects_missing_body(self):
        """NEGATIVE: Malformed request body returns 422"""
        response = self.client.post("/login", json={})
        self.assertEqual(response.status_code, 422)

    # ─────────────────────────────────────────────
    # Health Check
    # ─────────────────────────────────────────────

    def test_health_endpoint(self):
        """POSITIVE: /health returns ok"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    # ─────────────────────────────────────────────
    # Search Face
    # ─────────────────────────────────────────────

    @patch("app.app.perform_face_search")
    @patch("app.app.save_upload_file")
    @patch("app.app.os.remove")
    @patch("app.app.os.path.exists")
    @patch("app.app.os.listdir")
    def test_search_face_returns_ranked_results(self, mock_listdir, mock_exists, mock_remove, mock_save, mock_search):
        """POSITIVE: Valid selfie returns matched event photos ranked by score"""
        token = self.get_token("test-user-secret")
        mock_save.return_value = os.path.join(ROOT_DIR, "uploads", "query-file.jpg")
        mock_exists.return_value = True  # ensures os.remove is called in the finally block
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

    @patch("app.app.perform_face_search")
    @patch("app.app.save_upload_file")
    @patch("app.app.os.remove")
    @patch("app.app.os.path.exists")
    @patch("app.app.os.listdir")
    def test_search_face_returns_404_when_no_matches_above_threshold(
        self, mock_listdir, mock_exists, mock_remove, mock_save, mock_search
    ):
        """NEGATIVE: All results below threshold returns 404"""
        token = self.get_token("test-user-secret")
        mock_save.return_value = os.path.join(ROOT_DIR, "uploads", "query-file.jpg")
        mock_exists.return_value = True
        mock_search.return_value = [
            {"face": "event-photo_face1.jpg", "distance": 0.10},
        ]
        mock_listdir.return_value = ["event-photo.jpg"]

        response = self.client.post(
            "/search-face",
            files={"file": ("person.jpg", io.BytesIO(b"fake"), "image/jpeg")},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 404)

    @patch("app.app.perform_face_search")
    @patch("app.app.save_upload_file")
    @patch("app.app.os.remove")
    @patch("app.app.os.path.exists")
    @patch("app.app.os.listdir")
    def test_search_face_deduplicates_same_source_image(
        self, mock_listdir, mock_exists, mock_remove, mock_save, mock_search
    ):
        """POSITIVE: Multiple faces from same source image deduplicated to one result"""
        token = self.get_token("test-user-secret")
        mock_save.return_value = os.path.join(ROOT_DIR, "uploads", "query-file.jpg")
        mock_exists.return_value = True
        mock_search.return_value = [
            {"face": "event-photo_face1.jpg", "distance": 0.95},
            {"face": "event-photo_face2.jpg", "distance": 0.88},
        ]
        mock_listdir.return_value = ["event-photo.jpg"]

        response = self.client.post(
            "/search-face",
            files={"file": ("person.jpg", io.BytesIO(b"fake"), "image/jpeg")},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        # Both faces come from 'event-photo.jpg', so result should be deduplicated to 1
        self.assertEqual(len(payload["results"]), 1)
        self.assertEqual(payload["results"][0]["filename"], "event-photo.jpg")

    def test_search_face_rejects_unauthenticated_request(self):
        """NEGATIVE: No auth token returns 401 (OAuth2PasswordBearer behavior)"""
        response = self.client.post(
            "/search-face",
            files={"file": ("person.jpg", io.BytesIO(b"fake"), "image/jpeg")},
        )
        self.assertEqual(response.status_code, 401)

    @patch("app.app.save_upload_file")  # prevent cv2 import via file processing before auth fires
    def test_search_face_rejects_admin_token(self, mock_save):
        """NEGATIVE: Admin token cannot access user /search-face endpoint"""
        token = self.get_token("test-admin-secret")
        response = self.client.post(
            "/search-face",
            files={"file": ("person.jpg", io.BytesIO(b"fake"), "image/jpeg")},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 403)

    @patch("app.app.save_upload_file")
    def test_search_face_rejects_invalid_file_type(self, mock_save):
        """NEGATIVE: Non-image file type raises 400"""
        mock_save.side_effect = ValueError("Invalid file type")
        token = self.get_token("test-user-secret")
        response = self.client.post(
            "/search-face",
            files={"file": ("doc.pdf", io.BytesIO(b"fake"), "application/pdf")},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 400)

    # ─────────────────────────────────────────────
    # Admin: Upload Event Images
    # ─────────────────────────────────────────────

    @patch("app.app.initialize_job")
    @patch("app.app.celery_app.send_task")
    @patch("app.app.save_upload_file")
    def test_admin_upload_queues_background_job(self, mock_save, mock_send_task, mock_initialize_job):
        """POSITIVE: Admin uploads 2 images -> 202 queued with correct count"""
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
        self.assertIn("job_id", payload)
        mock_initialize_job.assert_called_once()
        mock_send_task.assert_called_once()

    def test_admin_upload_rejects_user_token(self):
        """NEGATIVE: Regular user cannot access /admin/upload-images"""
        token = self.get_token("test-user-secret")
        response = self.client.post(
            "/admin/upload-images",
            files=[("files", ("event.jpg", io.BytesIO(b"a"), "image/jpeg"))],
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 403)

    def test_admin_upload_rejects_unauthenticated(self):
        """NEGATIVE: No token returns 401 (OAuth2PasswordBearer behavior)"""
        response = self.client.post(
            "/admin/upload-images",
            files=[("files", ("event.jpg", io.BytesIO(b"a"), "image/jpeg"))],
        )
        self.assertEqual(response.status_code, 401)

    def test_admin_upload_rejects_expired_token(self):
        """NEGATIVE: Fake/tampered JWT returns 401 (invalid token, not wrong role)"""
        response = self.client.post(
            "/admin/upload-images",
            files=[("files", ("event.jpg", io.BytesIO(b"a"), "image/jpeg"))],
            headers={"Authorization": "Bearer completely.fake.token"},
        )
        self.assertEqual(response.status_code, 401)

    # ─────────────────────────────────────────────
    # Admin: Drive Import
    # ─────────────────────────────────────────────

    @patch("app.app.initialize_job")
    @patch("app.app.celery_app.send_task")
    def test_drive_import_queues_background_job(self, mock_send_task, mock_initialize_job):
        """POSITIVE: Admin provides folder ID -> job queued"""
        token = self.get_token("test-admin-secret")

        response = self.client.post(
            "/admin/import-drive",
            json={"drive_folder_id": "folder123"},
            headers={"Authorization": f"Bearer {token}"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "queued")
        self.assertIn("job_id", response.json())
        mock_initialize_job.assert_called_once()
        mock_send_task.assert_called_once_with(
            "process_drive_folder", args=[unittest.mock.ANY, "folder123"]
        )

    def test_drive_import_rejects_user_token(self):
        """NEGATIVE: Regular user cannot trigger a drive import"""
        token = self.get_token("test-user-secret")
        response = self.client.post(
            "/admin/import-drive",
            json={"drive_folder_id": "folder123"},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 403)

    def test_drive_import_rejects_missing_folder_id(self):
        """NEGATIVE: Missing drive_folder_id body returns 422"""
        token = self.get_token("test-admin-secret")
        response = self.client.post(
            "/admin/import-drive",
            json={},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 422)

    # ─────────────────────────────────────────────
    # Admin: Job Status
    # ─────────────────────────────────────────────

    @patch("app.app.get_job_status")
    def test_job_status_returns_structured_progress(self, mock_get_job_status):
        """POSITIVE: Job status returns full structured payload"""
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
        payload = response.json()
        self.assertEqual(payload["faces_indexed"], 7)
        self.assertEqual(payload["status"], "processing")
        self.assertEqual(payload["job_id"], "job-1")

    @patch("app.app.get_job_status")
    def test_job_status_for_completed_job(self, mock_get_job_status):
        """POSITIVE: Completed job status returns completed state"""
        token = self.get_token("test-admin-secret")
        mock_get_job_status.return_value = {
            "job_id": "job-2",
            "job_type": "drive_import",
            "status": "completed",
            "images_received": 10,
            "images_downloaded": 10,
            "faces_indexed": 25,
            "error": None,
        }

        response = self.client.get(
            "/admin/job-status/job-2",
            headers={"Authorization": f"Bearer {token}"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "completed")
        self.assertEqual(response.json()["faces_indexed"], 25)

    def test_job_status_rejects_user_token(self):
        """NEGATIVE: Regular user cannot poll admin job status"""
        token = self.get_token("test-user-secret")
        response = self.client.get(
            "/admin/job-status/some-job",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 403)

    def test_job_status_rejects_unauthenticated(self):
        """NEGATIVE: No auth token returns 401 (OAuth2PasswordBearer behavior)"""
        response = self.client.get("/admin/job-status/some-job")
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
