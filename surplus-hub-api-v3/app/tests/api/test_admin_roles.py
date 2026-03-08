"""Tests for admin role management: /api/v1/admin/roles/*

RBAC scenarios:
  - Non-admin gets 403
  - MODERATOR blocked from ADMIN-only endpoints
  - ADMIN can list admin users
  - SUPER_ADMIN can update roles
  - Audit log created on role change
"""

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.security import create_access_token
from app.models.user import User

API_V1_STR = settings.API_V1_STR
ROLES_PREFIX = f"{API_V1_STR}/admin/roles"

_NO_AUTH_CODES = (401, 403)


# ---------------------------------------------------------------------------
# Session-scoped admin fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def roles_moderator_user(db):
    user = User(
        email="roles_moderator@example.com",
        hashed_password=None,
        name="Roles Moderator User",
        is_active=True,
        is_superuser=False,
        admin_role="MODERATOR",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="session")
def roles_admin_user(db):
    user = User(
        email="roles_admin@example.com",
        hashed_password=None,
        name="Roles Admin User",
        is_active=True,
        is_superuser=False,
        admin_role="ADMIN",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="session")
def super_roles_admin_user(db):
    user = User(
        email="roles_superadmin@example.com",
        hashed_password=None,
        name="Roles Super Admin User",
        is_active=True,
        is_superuser=True,
        admin_role="SUPER_ADMIN",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="session")
def roles_moderator_headers(roles_moderator_user):
    token = create_access_token(subject=roles_moderator_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="session")
def roles_admin_headers(roles_admin_user):
    token = create_access_token(subject=roles_admin_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="session")
def super_roles_admin_headers(super_roles_admin_user):
    token = create_access_token(subject=super_roles_admin_user.id)
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Tests: Auth guard
# ---------------------------------------------------------------------------

class TestAdminRolesAuthGuard:
    def test_no_token_rejected(self, client: TestClient):
        resp = client.get(f"{ROLES_PREFIX}")
        assert resp.status_code in _NO_AUTH_CODES

    def test_regular_user_gets_403(self, client: TestClient, auth_headers):
        """일반 사용자(admin_role=None)는 403."""
        resp = client.get(f"{ROLES_PREFIX}", headers=auth_headers)
        assert resp.status_code == 403

    def test_moderator_blocked_from_list(self, client: TestClient, roles_moderator_headers):
        """MODERATOR는 ADMIN-only 엔드포인트에 접근 불가."""
        resp = client.get(f"{ROLES_PREFIX}", headers=roles_moderator_headers)
        assert resp.status_code == 403

    def test_moderator_blocked_from_audit_logs(self, client: TestClient, roles_moderator_headers):
        """MODERATOR는 감사 로그에도 접근 불가."""
        resp = client.get(f"{ROLES_PREFIX}/audit-logs", headers=roles_moderator_headers)
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Tests: ADMIN can list admin users
# ---------------------------------------------------------------------------

class TestAdminCanListUsers:
    def test_admin_list_roles_admin_users(self, client: TestClient, roles_admin_headers):
        """ADMIN은 관리자 목록 조회 가능."""
        resp = client.get(f"{ROLES_PREFIX}", headers=roles_admin_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "success"
        data = body["data"]
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 1  # moderator, admin, super_admin 등 최소 1명

    def test_admin_list_returns_only_admin_roles(self, client: TestClient, roles_admin_headers):
        """반환된 유저는 모두 admin_role을 가져야 함."""
        resp = client.get(f"{ROLES_PREFIX}", headers=roles_admin_headers)
        assert resp.status_code == 200
        items = resp.json()["data"]["items"]
        for item in items:
            assert item.get("adminRole") is not None

    def test_admin_view_audit_logs(self, client: TestClient, roles_admin_headers):
        """ADMIN은 감사 로그 조회 가능."""
        resp = client.get(f"{ROLES_PREFIX}/audit-logs", headers=roles_admin_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "success"
        assert "items" in body["data"]


# ---------------------------------------------------------------------------
# Tests: SUPER_ADMIN can update roles
# ---------------------------------------------------------------------------

class TestSuperAdminRoleUpdate:
    def test_admin_cannot_update_role(
        self, client: TestClient, roles_admin_headers, roles_moderator_user
    ):
        """ADMIN은 역할 변경 불가 (SUPER_ADMIN 전용)."""
        resp = client.put(
            f"{ROLES_PREFIX}/{roles_moderator_user.id}/role",
            json={"adminRole": "ADMIN"},
            headers=roles_admin_headers,
        )
        assert resp.status_code == 403

    def test_super_admin_can_update_role(
        self, client: TestClient, super_roles_admin_headers, roles_moderator_user
    ):
        """SUPER_ADMIN은 역할 변경 가능."""
        resp = client.put(
            f"{ROLES_PREFIX}/{roles_moderator_user.id}/role",
            json={"adminRole": "ADMIN"},
            headers=super_roles_admin_headers,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "success"
        assert body["data"]["adminRole"] == "ADMIN"

        # 원상 복구 (다른 테스트 영향 방지)
        client.put(
            f"{ROLES_PREFIX}/{roles_moderator_user.id}/role",
            json={"adminRole": "MODERATOR"},
            headers=super_roles_admin_headers,
        )

    def test_super_admin_rejects_invalid_role(
        self, client: TestClient, super_roles_admin_headers, roles_moderator_user
    ):
        """유효하지 않은 역할은 400 반환."""
        resp = client.put(
            f"{ROLES_PREFIX}/{roles_moderator_user.id}/role",
            json={"adminRole": "GOD_MODE"},
            headers=super_roles_admin_headers,
        )
        assert resp.status_code == 400

    def test_super_admin_404_on_missing_user(
        self, client: TestClient, super_roles_admin_headers
    ):
        """존재하지 않는 유저 -> 404."""
        resp = client.put(
            f"{ROLES_PREFIX}/99999/role",
            json={"adminRole": "MODERATOR"},
            headers=super_roles_admin_headers,
        )
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Tests: Audit log created on role change
# ---------------------------------------------------------------------------

class TestAuditLogOnRoleChange:
    def test_audit_log_created_after_role_update(
        self, client: TestClient, super_roles_admin_headers, roles_admin_headers, roles_moderator_user
    ):
        """역할 변경 후 감사 로그가 생성되어야 함."""
        # 역할 변경 수행
        client.put(
            f"{ROLES_PREFIX}/{roles_moderator_user.id}/role",
            json={"adminRole": "MODERATOR"},
            headers=super_roles_admin_headers,
        )

        # 감사 로그 확인
        resp = client.get(f"{ROLES_PREFIX}/audit-logs", headers=roles_admin_headers)
        assert resp.status_code == 200
        logs = resp.json()["data"]["items"]
        assert len(logs) >= 1

        actions = [log["action"] for log in logs]
        assert "UPDATE_ADMIN_ROLE" in actions


# ---------------------------------------------------------------------------
# Tests: Audit log field validation
# ---------------------------------------------------------------------------

class TestAuditLogFields:
    def test_audit_log_contains_required_fields(
        self, client: TestClient, super_roles_admin_headers, roles_admin_headers, roles_moderator_user
    ):
        """감사 로그에 adminId, action, targetType, targetId 필드가 있어야 함."""
        client.put(
            f"{ROLES_PREFIX}/{roles_moderator_user.id}/role",
            json={"adminRole": "ADMIN"},
            headers=super_roles_admin_headers,
        )
        resp = client.get(f"{ROLES_PREFIX}/audit-logs", headers=roles_admin_headers)
        assert resp.status_code == 200
        logs = resp.json()["data"]["items"]
        assert len(logs) >= 1

        log = logs[0]
        assert "adminId" in log or "admin_id" in log
        assert "action" in log
        assert "targetType" in log or "target_type" in log
        assert "targetId" in log or "target_id" in log

    def test_audit_log_correct_action_value(
        self, client: TestClient, super_roles_admin_headers, roles_admin_headers, roles_moderator_user
    ):
        """감사 로그의 action 값이 UPDATE_ADMIN_ROLE이어야 함."""
        client.put(
            f"{ROLES_PREFIX}/{roles_moderator_user.id}/role",
            json={"adminRole": "MODERATOR"},
            headers=super_roles_admin_headers,
        )
        resp = client.get(f"{ROLES_PREFIX}/audit-logs", headers=roles_admin_headers)
        assert resp.status_code == 200
        logs = resp.json()["data"]["items"]
        role_change_logs = [l for l in logs if l["action"] == "UPDATE_ADMIN_ROLE"]
        assert len(role_change_logs) >= 1

    def test_audit_log_correct_target_type(
        self, client: TestClient, super_roles_admin_headers, roles_admin_headers, roles_moderator_user
    ):
        """감사 로그의 targetType이 'user'이어야 함."""
        client.put(
            f"{ROLES_PREFIX}/{roles_moderator_user.id}/role",
            json={"adminRole": "ADMIN"},
            headers=super_roles_admin_headers,
        )
        resp = client.get(f"{ROLES_PREFIX}/audit-logs", headers=roles_admin_headers)
        assert resp.status_code == 200
        logs = resp.json()["data"]["items"]
        role_change_logs = [l for l in logs if l["action"] == "UPDATE_ADMIN_ROLE"]
        assert len(role_change_logs) >= 1
        target_type = role_change_logs[0].get("targetType") or role_change_logs[0].get("target_type")
        assert target_type == "user"

    def test_audit_log_filter_by_admin_id(
        self, client: TestClient, super_roles_admin_headers, super_roles_admin_user, roles_admin_headers, roles_moderator_user
    ):
        """admin_id 필터링이 동작해야 함."""
        # SUPER_ADMIN이 역할 변경 수행
        client.put(
            f"{ROLES_PREFIX}/{roles_moderator_user.id}/role",
            json={"adminRole": "MODERATOR"},
            headers=super_roles_admin_headers,
        )

        # super_roles_admin_user.id로 필터링
        resp = client.get(
            f"{ROLES_PREFIX}/audit-logs?admin_id={super_roles_admin_user.id}",
            headers=roles_admin_headers,
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        logs = data["items"]
        # 반환된 모든 로그의 adminId가 super_roles_admin_user.id여야 함
        for log in logs:
            log_admin_id = log.get("adminId") or log.get("admin_id")
            assert log_admin_id == super_roles_admin_user.id

    def test_audit_log_pagination(
        self, client: TestClient, super_roles_admin_headers, roles_admin_headers, roles_moderator_user, roles_admin_user
    ):
        """감사 로그 페이지네이션이 동작해야 함 (limit/skip 파라미터)."""
        # 여러 번 역할 변경으로 로그 생성
        for role in ["ADMIN", "MODERATOR", "ADMIN"]:
            client.put(
                f"{ROLES_PREFIX}/{roles_moderator_user.id}/role",
                json={"adminRole": role},
                headers=super_roles_admin_headers,
            )

        resp_all = client.get(
            f"{ROLES_PREFIX}/audit-logs?skip=0&limit=100",
            headers=roles_admin_headers,
        )
        assert resp_all.status_code == 200
        total = resp_all.json()["data"]["total"]
        assert total >= 3

        # limit=1로 조회 시 1개만 반환
        resp_limit = client.get(
            f"{ROLES_PREFIX}/audit-logs?skip=0&limit=1",
            headers=roles_admin_headers,
        )
        assert resp_limit.status_code == 200
        assert len(resp_limit.json()["data"]["items"]) == 1

        # skip=1으로 조회 시 첫 번째 항목이 다를 수 있음
        resp_skip = client.get(
            f"{ROLES_PREFIX}/audit-logs?skip=1&limit=1",
            headers=roles_admin_headers,
        )
        assert resp_skip.status_code == 200
        items_skip = resp_skip.json()["data"]["items"]
        items_first = resp_all.json()["data"]["items"]
        if len(items_skip) > 0 and len(items_first) > 1:
            assert items_skip[0]["id"] != items_first[0]["id"]


# ---------------------------------------------------------------------------
# Tests: RBAC Hierarchy — detailed
# ---------------------------------------------------------------------------

class TestRBACHierarchy:
    def test_super_admin_can_access_list(
        self, client: TestClient, super_roles_admin_headers
    ):
        """SUPER_ADMIN은 관리자 목록 조회 가능 (ADMIN 이상 권한)."""
        resp = client.get(f"{ROLES_PREFIX}", headers=super_roles_admin_headers)
        assert resp.status_code == 200

    def test_super_admin_can_access_audit_logs(
        self, client: TestClient, super_roles_admin_headers
    ):
        """SUPER_ADMIN은 감사 로그 조회 가능."""
        resp = client.get(f"{ROLES_PREFIX}/audit-logs", headers=super_roles_admin_headers)
        assert resp.status_code == 200

    def test_admin_can_access_audit_logs(
        self, client: TestClient, roles_admin_headers
    ):
        """ADMIN은 감사 로그 조회 가능."""
        resp = client.get(f"{ROLES_PREFIX}/audit-logs", headers=roles_admin_headers)
        assert resp.status_code == 200

    def test_moderator_cannot_access_role_update(
        self, client: TestClient, roles_moderator_headers, roles_admin_user
    ):
        """MODERATOR는 역할 업데이트 엔드포인트에 접근 불가 (SUPER_ADMIN 전용)."""
        resp = client.put(
            f"{ROLES_PREFIX}/{roles_admin_user.id}/role",
            json={"adminRole": "MODERATOR"},
            headers=roles_moderator_headers,
        )
        assert resp.status_code == 403

    def test_admin_cannot_access_role_update(
        self, client: TestClient, roles_admin_headers, roles_moderator_user
    ):
        """ADMIN은 역할 업데이트 엔드포인트에 접근 불가 (SUPER_ADMIN 전용)."""
        resp = client.put(
            f"{ROLES_PREFIX}/{roles_moderator_user.id}/role",
            json={"adminRole": "ADMIN"},
            headers=roles_admin_headers,
        )
        assert resp.status_code == 403

    def test_super_admin_role_downgrade(
        self, client: TestClient, super_roles_admin_headers, roles_admin_headers, roles_admin_user
    ):
        """SUPER_ADMIN이 ADMIN을 MODERATOR로 강등할 수 있음."""
        # roles_admin_user를 ADMIN으로 복구 (사전 상태 보장)
        client.put(
            f"{ROLES_PREFIX}/{roles_admin_user.id}/role",
            json={"adminRole": "ADMIN"},
            headers=super_roles_admin_headers,
        )

        # ADMIN -> MODERATOR 강등
        resp = client.put(
            f"{ROLES_PREFIX}/{roles_admin_user.id}/role",
            json={"adminRole": "MODERATOR"},
            headers=super_roles_admin_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["adminRole"] == "MODERATOR"

        # 원상 복구 (다른 테스트 영향 방지)
        client.put(
            f"{ROLES_PREFIX}/{roles_admin_user.id}/role",
            json={"adminRole": "ADMIN"},
            headers=super_roles_admin_headers,
        )

    def test_super_admin_role_removal(
        self, client: TestClient, super_roles_admin_headers, db
    ):
        """SUPER_ADMIN이 역할을 null로 제거할 수 있음."""
        from app.core.security import get_password_hash

        # 제거 테스트용 임시 유저 생성
        temp_user = User(
            email="temp_remove_role@example.com",
            hashed_password=get_password_hash("tmp"),
            name="Temp Remove",
            is_active=True,
            admin_role="MODERATOR",
        )
        db.add(temp_user)
        db.commit()
        db.refresh(temp_user)

        resp = client.put(
            f"{ROLES_PREFIX}/{temp_user.id}/role",
            json={"adminRole": None},
            headers=super_roles_admin_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["adminRole"] is None


# ---------------------------------------------------------------------------
# Tests: Get admin user detail
# ---------------------------------------------------------------------------

class TestGetAdminUserDetail:
    def test_admin_can_get_user_detail(
        self, client: TestClient, roles_admin_headers, super_roles_admin_user
    ):
        """ADMIN은 특정 관리자 유저 상세 조회 가능."""
        resp = client.get(
            f"{ROLES_PREFIX}/{super_roles_admin_user.id}",
            headers=roles_admin_headers,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "success"
        assert body["data"]["id"] == super_roles_admin_user.id

    def test_get_nonexistent_roles_admin_user_404(
        self, client: TestClient, roles_admin_headers
    ):
        """존재하지 않는 관리자 유저 조회 -> 404."""
        resp = client.get(
            f"{ROLES_PREFIX}/99998",
            headers=roles_admin_headers,
        )
        assert resp.status_code == 404

    def test_get_regular_user_as_roles_admin_user_404(
        self, client: TestClient, roles_admin_headers, test_user
    ):
        """admin_role이 없는 일반 유저를 관리자 엔드포인트로 조회 -> 404."""
        resp = client.get(
            f"{ROLES_PREFIX}/{test_user.id}",
            headers=roles_admin_headers,
        )
        assert resp.status_code == 404

    def test_moderator_cannot_get_user_detail(
        self, client: TestClient, super_roles_admin_user, db
    ):
        """MODERATOR는 관리자 유저 상세 조회 불가 (ADMIN 이상 권한 필요)."""
        # 별도의 MODERATOR 유저를 사용 (다른 테스트에서 역할이 변경되지 않는 유저)
        fresh_mod = User(
            email="fresh_mod_detail@example.com",
            hashed_password=None,
            name="Fresh Moderator",
            is_active=True,
            admin_role="MODERATOR",
        )
        db.add(fresh_mod)
        db.commit()
        db.refresh(fresh_mod)
        token = create_access_token(subject=fresh_mod.id)
        fresh_mod_headers = {"Authorization": f"Bearer {token}"}
        resp = client.get(
            f"{ROLES_PREFIX}/{super_roles_admin_user.id}",
            headers=fresh_mod_headers,
        )
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Tests: Security edge cases
# ---------------------------------------------------------------------------

class TestSecurityEdgeCases:
    def test_no_auth_header_on_audit_logs(self, client: TestClient):
        """인증 헤더 없이 감사 로그 조회 -> 401/403."""
        resp = client.get(f"{ROLES_PREFIX}/audit-logs")
        assert resp.status_code in _NO_AUTH_CODES

    def test_no_auth_header_on_role_update(self, client: TestClient):
        """인증 헤더 없이 역할 변경 -> 401/403."""
        resp = client.put(
            f"{ROLES_PREFIX}/1/role",
            json={"adminRole": "MODERATOR"},
        )
        assert resp.status_code in _NO_AUTH_CODES

    def test_regular_user_cannot_list_admins(
        self, client: TestClient, auth_headers
    ):
        """일반 유저는 관리자 목록 조회 불가."""
        resp = client.get(f"{ROLES_PREFIX}", headers=auth_headers)
        assert resp.status_code == 403

    def test_regular_user_cannot_view_audit_logs(
        self, client: TestClient, auth_headers
    ):
        """일반 유저는 감사 로그 조회 불가."""
        resp = client.get(f"{ROLES_PREFIX}/audit-logs", headers=auth_headers)
        assert resp.status_code == 403

    def test_regular_user_cannot_update_role(
        self, client: TestClient, auth_headers, roles_moderator_user
    ):
        """일반 유저는 역할 변경 불가."""
        resp = client.put(
            f"{ROLES_PREFIX}/{roles_moderator_user.id}/role",
            json={"adminRole": "SUPER_ADMIN"},
            headers=auth_headers,
        )
        assert resp.status_code == 403

    def test_super_admin_update_own_role(
        self, client: TestClient, super_roles_admin_headers, super_roles_admin_user
    ):
        """SUPER_ADMIN이 자신의 역할을 변경하는 시도 (허용되어야 함)."""
        resp = client.put(
            f"{ROLES_PREFIX}/{super_roles_admin_user.id}/role",
            json={"adminRole": "SUPER_ADMIN"},
            headers=super_roles_admin_headers,
        )
        # 자기 자신 역할 변경 - API 설계상 허용 (역할 자체가 동일하면 그냥 200)
        assert resp.status_code == 200

    def test_invalid_role_value_returns_400(
        self, client: TestClient, super_roles_admin_headers, roles_moderator_user
    ):
        """유효하지 않은 역할 값 -> 400."""
        resp = client.put(
            f"{ROLES_PREFIX}/{roles_moderator_user.id}/role",
            json={"adminRole": "INVALID_ROLE"},
            headers=super_roles_admin_headers,
        )
        assert resp.status_code == 400

    def test_nonexistent_user_role_update_returns_404(
        self, client: TestClient, super_roles_admin_headers
    ):
        """존재하지 않는 유저 역할 변경 -> 404."""
        resp = client.put(
            f"{ROLES_PREFIX}/99999/role",
            json={"adminRole": "MODERATOR"},
            headers=super_roles_admin_headers,
        )
        assert resp.status_code == 404

    def test_moderator_blocked_from_role_update_super_admin_endpoint(
        self, client: TestClient, roles_moderator_headers, roles_admin_user
    ):
        """MODERATOR는 SUPER_ADMIN 전용 역할 업데이트 엔드포인트 접근 불가."""
        resp = client.put(
            f"{ROLES_PREFIX}/{roles_admin_user.id}/role",
            json={"adminRole": "SUPER_ADMIN"},
            headers=roles_moderator_headers,
        )
        assert resp.status_code == 403
