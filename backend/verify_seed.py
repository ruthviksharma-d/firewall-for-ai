import sys, os, tempfile
sys.path.insert(0, os.getcwd())

# Point DB at a throwaway sqlite file before importing anything that touches engine
import database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

tmp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False).name
test_engine = create_engine(f"sqlite:///{tmp_db}", connect_args={"check_same_thread": False})
TestSession = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)
database.engine = test_engine
database.SessionLocal = TestSession

import seed
seed.SessionLocal = TestSession
seed.engine = test_engine

seed.seed()

from models.user import User, UserRole
from models.audit_log import AuditLog
from models.policy import Policy
from models.company_keyword import CompanyKeyword
from sqlalchemy import select, func

db = TestSession()
n_users = db.scalar(select(func.count()).select_from(User))
n_employees = db.scalar(select(func.count()).select_from(User).where(User.role != UserRole.ADMIN))
n_logs = db.scalar(select(func.count()).select_from(AuditLog))
n_policies = db.scalar(select(func.count()).select_from(Policy))
n_keywords = db.scalar(select(func.count()).select_from(CompanyKeyword))
depts = db.scalars(select(User.department).distinct()).all()
actions = dict(db.execute(select(AuditLog.action, func.count()).group_by(AuditLog.action)).all())
websites = dict(db.execute(select(AuditLog.website, func.count()).group_by(AuditLog.website)).all())
oldest = db.scalar(select(func.min(AuditLog.created_at)))
newest = db.scalar(select(func.max(AuditLog.created_at)))

print(f"users={n_users} employees={n_employees} logs={n_logs} policies={n_policies} keywords={n_keywords}")
print(f"departments({len(depts)})={sorted(depts)}")
print(f"actions={actions}")
print(f"websites={websites}")
print(f"date range: {oldest} -> {newest}")

# sanity assertions
assert n_employees == len(seed.DEFAULT_EMPLOYEES), f"expected {len(seed.DEFAULT_EMPLOYEES)} employees"
assert 200 <= n_logs <= 300, f"expected 200-300 logs, got {n_logs}"
assert n_policies == len(seed.DEFAULT_POLICIES)
assert n_keywords == len(seed.DEFAULT_KEYWORDS)
assert set(actions.keys()) == {"ALLOW", "WARN", "REDACT", "BLOCK"}, f"missing action types: {actions.keys()}"
assert set(websites.keys()) == set(seed.WEBSITES)
assert (newest - oldest).days <= 31, "spread should be within ~30 days"
assert len(depts) >= 8, f"expected >=8 departments, got {len(depts)}"

# idempotency check - run seed again, counts should not change
seed.seed()
db2 = TestSession()
n_logs2 = db2.scalar(select(func.count()).select_from(AuditLog))
n_users2 = db2.scalar(select(func.count()).select_from(User))
assert n_logs2 == n_logs, "seed() should be idempotent for audit logs"
assert n_users2 == n_users, "seed() should be idempotent for users"

print("ALL CHECKS PASSED")
