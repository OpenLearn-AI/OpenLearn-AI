import uuid

import pytest
from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError

from app.db.base import Base
from app.models.user import User
from app.models.profile import Profile
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.material import Material


ISSUER = "http://localhost:8080/realms/openlearn"


async def _delete_user_by_subject(db, subject: str) -> None:
    """Defensively remove a user by Keycloak subject to keep tests repeatable."""
    result = await db.execute(
        select(User).where(User.keycloak_subject == subject)
    )
    for user in result.scalars():
        await db.delete(user)
    await db.commit()


async def _create_user(db, subject: str, email: str) -> User:
    await _delete_user_by_subject(db, subject)

    user = User(
        keycloak_issuer=ISSUER,
        keycloak_subject=subject,
        email=email,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


@pytest.mark.asyncio
async def test_create_and_read_user(db_session):
    user = User(
        keycloak_issuer="http://localhost:8080/realms/openlearn",
        keycloak_subject="db-test-subject",
        email="db-test@example.com",
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    assert isinstance(user.id, uuid.UUID)
    assert user.keycloak_issuer == "http://localhost:8080/realms/openlearn"
    assert user.keycloak_subject == "db-test-subject"
    assert user.email == "db-test@example.com"
    assert user.settings == {}

    result = await db_session.execute(
        select(User).where(User.email == "db-test@example.com")
    )
    saved_user = result.scalar_one()

    assert saved_user.id == user.id

    await db_session.delete(saved_user)
    await db_session.commit()


@pytest.mark.asyncio
async def test_email_must_be_unique(db_session):
    first_user = User(
        keycloak_issuer="http://localhost:8080/realms/openlearn",
        keycloak_subject="unique-test-subject-1",
        email="unique-test@example.com",
    )
    second_user = User(
        keycloak_issuer="http://localhost:8080/realms/openlearn",
        keycloak_subject="unique-test-subject-2",
        email="unique-test@example.com",
    )

    db_session.add(first_user)
    await db_session.commit()

    db_session.add(second_user)

    with pytest.raises(IntegrityError):
        await db_session.commit()

    await db_session.rollback()

    await db_session.delete(first_user)
    await db_session.commit()


@pytest.mark.asyncio
async def test_keycloak_identity_must_be_unique(db_session):
    first_user = User(
        keycloak_issuer="http://localhost:8080/realms/openlearn",
        keycloak_subject="same-subject",
        email="identity-test-1@example.com",
    )
    second_user = User(
        keycloak_issuer="http://localhost:8080/realms/openlearn",
        keycloak_subject="same-subject",
        email="identity-test-2@example.com",
    )

    db_session.add(first_user)
    await db_session.commit()

    db_session.add(second_user)

    with pytest.raises(IntegrityError):
        await db_session.commit()

    await db_session.rollback()

    await db_session.delete(first_user)
    await db_session.commit()


def test_users_table_no_longer_has_preferred_lang():
    assert "preferred_lang" not in Base.metadata.tables["users"].columns

    profile_columns = set(Base.metadata.tables["profiles"].columns.keys())
    assert "preferred_language" in profile_columns


def test_profiles_table_registered_in_metadata():
    table = Base.metadata.tables["profiles"]

    assert set(table.columns.keys()) == {
        "id",
        "user_id",
        "education_level",
        "major",
        "university",
        "preferred_language",
        "learning_style_vark",
        "daily_available_minutes",
    }

    user_id = table.columns["user_id"]
    assert len(user_id.foreign_keys) == 1
    foreign_key = list(user_id.foreign_keys)[0]
    assert foreign_key.target_fullname == "users.id"
    assert foreign_key.ondelete == "CASCADE"

    constraint_names = {constraint.name for constraint in table.constraints}
    assert "uq_profiles_user_id" in constraint_names
    assert "ck_profiles_preferred_language_supported" in constraint_names
    assert "ck_profiles_daily_available_minutes_range" in constraint_names


@pytest.mark.asyncio
async def test_create_and_read_profile(db_session):
    user = await _create_user(
        db_session,
        "profile-roundtrip-subject",
        "profile-roundtrip@example.com",
    )

    profile = Profile(
        user_id=user.id,
        education_level="university",
        major="Computer Science",
        university="Cairo University",
        preferred_language="ar",
        learning_style_vark="visual",
        daily_available_minutes=45,
    )

    db_session.add(profile)
    await db_session.commit()
    await db_session.refresh(profile)

    assert isinstance(profile.id, uuid.UUID)
    assert profile.user_id == user.id
    assert profile.education_level == "university"
    assert profile.major == "Computer Science"
    assert profile.university == "Cairo University"
    assert profile.preferred_language == "ar"
    assert profile.learning_style_vark == "visual"
    assert profile.daily_available_minutes == 45

    result = await db_session.execute(
        select(Profile).where(Profile.user_id == user.id)
    )
    saved_profile = result.scalar_one()

    assert saved_profile.id == profile.id

    await db_session.delete(user)
    await db_session.commit()


@pytest.mark.asyncio
async def test_profile_preferred_language_defaults_to_en(db_session):
    user = await _create_user(
        db_session,
        "profile-default-subject",
        "profile-default@example.com",
    )

    profile = Profile(user_id=user.id)

    db_session.add(profile)
    await db_session.commit()
    await db_session.refresh(profile)

    assert profile.preferred_language == "en"

    await db_session.delete(user)
    await db_session.commit()


@pytest.mark.asyncio
async def test_optional_profile_fields_accept_null(db_session):
    user = await _create_user(
        db_session,
        "profile-null-subject",
        "profile-null@example.com",
    )

    profile = Profile(user_id=user.id)

    db_session.add(profile)
    await db_session.commit()
    await db_session.refresh(profile)

    assert profile.education_level is None
    assert profile.major is None
    assert profile.university is None
    assert profile.learning_style_vark is None
    assert profile.daily_available_minutes is None

    await db_session.delete(user)
    await db_session.commit()


@pytest.mark.asyncio
async def test_user_can_have_only_one_profile(db_session):
    user = await _create_user(
        db_session,
        "profile-unique-subject",
        "profile-unique@example.com",
    )

    first_profile = Profile(user_id=user.id)
    db_session.add(first_profile)
    await db_session.commit()

    second_profile = Profile(user_id=user.id)
    db_session.add(second_profile)

    with pytest.raises(IntegrityError):
        await db_session.commit()

    await db_session.rollback()

    await db_session.delete(user)
    await db_session.commit()


@pytest.mark.asyncio
async def test_profile_requires_existing_user(db_session):
    profile = Profile(
        user_id=uuid.uuid4(),
        preferred_language="en",
    )

    db_session.add(profile)

    with pytest.raises(IntegrityError):
        await db_session.commit()

    await db_session.rollback()


@pytest.mark.asyncio
async def test_preferred_language_is_required(db_session):
    user = await _create_user(
        db_session,
        "profile-required-subject",
        "profile-required@example.com",
    )

    # Core insert so the NULL reaches the database; the ORM would replace an
    # unset preferred_language with the server default.
    with pytest.raises(IntegrityError):
        await db_session.execute(
            insert(Profile).values(user_id=user.id, preferred_language=None)
        )

    await db_session.rollback()

    await db_session.delete(user)
    await db_session.commit()


@pytest.mark.parametrize("language", ["en", "ar"])
@pytest.mark.asyncio
async def test_preferred_language_accepts_supported_values(db_session, language):
    user = await _create_user(
        db_session,
        f"profile-lang-ok-{language}-subject",
        f"profile-lang-ok-{language}@example.com",
    )

    profile = Profile(user_id=user.id, preferred_language=language)
    db_session.add(profile)
    await db_session.commit()
    await db_session.refresh(profile)

    assert profile.preferred_language == language

    await db_session.delete(user)
    await db_session.commit()


@pytest.mark.parametrize("language", ["fr", "de", "EN", ""])
@pytest.mark.asyncio
async def test_preferred_language_rejects_unsupported_values(db_session, language):
    user = await _create_user(
        db_session,
        "profile-lang-bad-subject",
        "profile-lang-bad@example.com",
    )

    profile = Profile(user_id=user.id, preferred_language=language)
    db_session.add(profile)

    with pytest.raises(IntegrityError):
        await db_session.commit()

    await db_session.rollback()

    await db_session.delete(user)
    await db_session.commit()


@pytest.mark.parametrize("invalid_minutes", [0, -30, 1441])
@pytest.mark.asyncio
async def test_daily_available_minutes_rejects_out_of_range(db_session, invalid_minutes):
    user = await _create_user(
        db_session,
        f"profile-minutes-invalid-{invalid_minutes}-subject",
        f"profile-minutes-invalid-{invalid_minutes}@example.com",
    )

    profile = Profile(
        user_id=user.id,
        daily_available_minutes=invalid_minutes,
    )
    db_session.add(profile)

    with pytest.raises(IntegrityError):
        await db_session.commit()

    await db_session.rollback()

    await db_session.delete(user)
    await db_session.commit()


@pytest.mark.parametrize("valid_minutes", [1, 1440])
@pytest.mark.asyncio
async def test_daily_available_minutes_accepts_boundaries(db_session, valid_minutes):
    user = await _create_user(
        db_session,
        f"profile-minutes-valid-{valid_minutes}-subject",
        f"profile-minutes-valid-{valid_minutes}@example.com",
    )

    profile = Profile(
        user_id=user.id,
        daily_available_minutes=valid_minutes,
    )
    db_session.add(profile)
    await db_session.commit()
    await db_session.refresh(profile)

    assert profile.daily_available_minutes == valid_minutes

    await db_session.delete(user)
    await db_session.commit()


@pytest.mark.asyncio
async def test_deleting_user_cascades_to_profile(db_session):
    user = await _create_user(
        db_session,
        "profile-cascade-subject",
        "profile-cascade@example.com",
    )

    profile = Profile(user_id=user.id)
    db_session.add(profile)
    await db_session.commit()

    await db_session.delete(user)
    await db_session.commit()

    result = await db_session.execute(
        select(Profile).where(Profile.user_id == user.id)
    )

    assert result.scalar_one_or_none() is None


async def _create_course(db, owner: User, title="Test Course", description="Learn things"):
    course = Course(
        owner_id=owner.id,
        title=title,
        description=description,
    )

    db.add(course)
    await db.commit()
    await db.refresh(course)

    return course


def test_courses_table_contract():
    table = Base.metadata.tables["courses"]

    assert set(table.columns.keys()) == {
        "id",
        "owner_id",
        "title",
        "description",
        "created_at",
    }

    owner_id = table.columns["owner_id"]
    foreign_key = list(owner_id.foreign_keys)[0]
    assert foreign_key.target_fullname == "users.id"
    assert foreign_key.ondelete == "CASCADE"
    assert owner_id.nullable is False

    assert table.columns["title"].nullable is False
    assert table.columns["description"].nullable is True
    assert table.columns["created_at"].nullable is False

    index_names = {index.name for index in table.indexes}
    assert "ix_courses_owner_id" in index_names


def test_enrollments_table_contract():
    table = Base.metadata.tables["enrollments"]

    assert set(table.columns.keys()) == {
        "id",
        "course_id",
        "user_id",
        "created_at",
    }

    course_fk = list(table.columns["course_id"].foreign_keys)[0]
    assert course_fk.target_fullname == "courses.id"
    assert course_fk.ondelete == "CASCADE"

    user_fk = list(table.columns["user_id"].foreign_keys)[0]
    assert user_fk.target_fullname == "users.id"
    assert user_fk.ondelete == "CASCADE"

    assert table.columns["course_id"].nullable is False
    assert table.columns["user_id"].nullable is False

    constraint_names = {constraint.name for constraint in table.constraints}
    assert "uq_enrollments_course_user" in constraint_names

    index_names = {index.name for index in table.indexes}
    assert "ix_enrollments_user_id" in index_names


@pytest.mark.asyncio
async def test_create_course_with_owner(db_session):
    user = await _create_user(
        db_session,
        "course-create-subject",
        "course-create@example.com",
    )

    course = await _create_course(
        db_session,
        user,
        title="Intro to AI",
        description="A first course in artificial intelligence.",
    )

    assert isinstance(course.id, uuid.UUID)
    assert course.owner_id == user.id
    assert course.title == "Intro to AI"
    assert course.description == "A first course in artificial intelligence."
    assert course.created_at is not None

    await db_session.delete(user)
    await db_session.commit()


@pytest.mark.asyncio
async def test_course_description_is_optional(db_session):
    user = await _create_user(
        db_session,
        "course-no-desc-subject",
        "course-no-desc@example.com",
    )

    course = await _create_course(
        db_session,
        user,
        title="No Description Course",
        description=None,
    )

    assert course.description is None

    await db_session.delete(user)
    await db_session.commit()


@pytest.mark.asyncio
async def test_course_requires_owner(db_session):
    user = await _create_user(
        db_session,
        "course-owner-required-subject",
        "course-owner-required@example.com",
    )

    course = Course(owner_id=None, title="Orphan Course")
    db_session.add(course)

    with pytest.raises(IntegrityError):
        await db_session.commit()

    await db_session.rollback()

    await db_session.delete(user)
    await db_session.commit()


@pytest.mark.asyncio
async def test_course_rejects_nonexistent_owner(db_session):
    user = await _create_user(
        db_session,
        "course-fk-subject",
        "course-fk@example.com",
    )

    course = Course(owner_id=uuid.uuid4(), title="Ghost Owner Course")
    db_session.add(course)

    with pytest.raises(IntegrityError):
        await db_session.commit()

    await db_session.rollback()

    await db_session.delete(user)
    await db_session.commit()


@pytest.mark.asyncio
async def test_course_title_is_required(db_session):
    user = await _create_user(
        db_session,
        "course-title-required-subject",
        "course-title-required@example.com",
    )

    course = Course(owner_id=user.id, title=None)
    db_session.add(course)

    with pytest.raises(IntegrityError):
        await db_session.commit()

    await db_session.rollback()

    await db_session.delete(user)
    await db_session.commit()


@pytest.mark.asyncio
async def test_deleting_owner_cascades_to_courses(db_session):
    user = await _create_user(
        db_session,
        "course-cascade-subject",
        "course-cascade@example.com",
    )

    await _create_course(db_session, user)

    await db_session.delete(user)
    await db_session.commit()

    result = await db_session.execute(
        select(Course).where(Course.owner_id == user.id)
    )

    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_create_enrollment(db_session):
    user = await _create_user(
        db_session,
        "enrollment-create-subject",
        "enrollment-create@example.com",
    )
    course = await _create_course(db_session, user)

    enrollment = Enrollment(course_id=course.id, user_id=user.id)
    db_session.add(enrollment)
    await db_session.commit()
    await db_session.refresh(enrollment)

    assert isinstance(enrollment.id, uuid.UUID)
    assert enrollment.course_id == course.id
    assert enrollment.user_id == user.id
    assert enrollment.created_at is not None

    await db_session.delete(user)
    await db_session.commit()


@pytest.mark.asyncio
async def test_enrollment_rejects_nonexistent_course(db_session):
    user = await _create_user(
        db_session,
        "enrollment-bad-course-subject",
        "enrollment-bad-course@example.com",
    )

    enrollment = Enrollment(course_id=uuid.uuid4(), user_id=user.id)
    db_session.add(enrollment)

    with pytest.raises(IntegrityError):
        await db_session.commit()

    await db_session.rollback()

    await db_session.delete(user)
    await db_session.commit()


@pytest.mark.asyncio
async def test_enrollment_rejects_nonexistent_user(db_session):
    user = await _create_user(
        db_session,
        "enrollment-bad-user-subject",
        "enrollment-bad-user@example.com",
    )
    course = await _create_course(db_session, user)

    enrollment = Enrollment(course_id=course.id, user_id=uuid.uuid4())
    db_session.add(enrollment)

    with pytest.raises(IntegrityError):
        await db_session.commit()

    await db_session.rollback()

    await db_session.delete(user)
    await db_session.commit()


@pytest.mark.asyncio
async def test_duplicate_enrollment_is_rejected(db_session):
    user = await _create_user(
        db_session,
        "enrollment-duplicate-subject",
        "enrollment-duplicate@example.com",
    )
    course = await _create_course(db_session, user)

    db_session.add(Enrollment(course_id=course.id, user_id=user.id))
    await db_session.commit()

    db_session.add(Enrollment(course_id=course.id, user_id=user.id))

    with pytest.raises(IntegrityError):
        await db_session.commit()

    await db_session.rollback()

    await db_session.delete(user)
    await db_session.commit()


@pytest.mark.asyncio
async def test_deleting_course_cascades_to_enrollments(db_session):
    owner = await _create_user(
        db_session,
        "enrollment-course-cascade-owner-subject",
        "enrollment-course-cascade-owner@example.com",
    )
    student = await _create_user(
        db_session,
        "enrollment-course-cascade-student-subject",
        "enrollment-course-cascade-student@example.com",
    )
    course = await _create_course(db_session, owner)

    db_session.add(Enrollment(course_id=course.id, user_id=student.id))
    await db_session.commit()

    await db_session.delete(course)
    await db_session.commit()

    result = await db_session.execute(
        select(Enrollment).where(Enrollment.course_id == course.id)
    )

    assert result.scalar_one_or_none() is None

    await db_session.delete(owner)
    await db_session.delete(student)
    await db_session.commit()


@pytest.mark.asyncio
async def test_deleting_user_cascades_to_enrollments(db_session):
    owner = await _create_user(
        db_session,
        "enrollment-user-cascade-owner-subject",
        "enrollment-user-cascade-owner@example.com",
    )
    student = await _create_user(
        db_session,
        "enrollment-user-cascade-student-subject",
        "enrollment-user-cascade-student@example.com",
    )
    course = await _create_course(db_session, owner)

    db_session.add(Enrollment(course_id=course.id, user_id=student.id))
    await db_session.commit()

    await db_session.delete(student)
    await db_session.commit()

    result = await db_session.execute(
        select(Enrollment).where(Enrollment.user_id == student.id)
    )

    assert result.scalar_one_or_none() is None

    await db_session.delete(owner)
    await db_session.commit()


async def _create_material(db, course: Course, uploaded_by: User) -> Material:
    material = Material(
        course_id=course.id,
        title="Lecture Slides",
        s3_key=f"courses/{course.id}/materials/{uuid.uuid4()}-slides.pdf",
        uploaded_by=uploaded_by.id,
    )
    db.add(material)
    await db.commit()
    await db.refresh(material)
    return material


def test_materials_table_contract():
    table = Base.metadata.tables["materials"]

    assert set(table.columns.keys()) == {
        "id",
        "course_id",
        "title",
        "s3_key",
        "status",
        "uploaded_by",
        "created_at",
    }

    course_fk = list(table.columns["course_id"].foreign_keys)[0]
    assert course_fk.target_fullname == "courses.id"
    assert course_fk.ondelete == "CASCADE"
    assert table.columns["course_id"].nullable is False

    uploader_fk = list(table.columns["uploaded_by"].foreign_keys)[0]
    assert uploader_fk.target_fullname == "users.id"
    assert uploader_fk.ondelete == "CASCADE"
    assert table.columns["uploaded_by"].nullable is False

    assert table.columns["title"].nullable is False
    assert table.columns["s3_key"].nullable is False
    assert table.columns["status"].nullable is False

    constraint_names = {constraint.name for constraint in table.constraints}
    assert "uq_materials_s3_key" in constraint_names

    index_names = {index.name for index in table.indexes}
    assert "ix_materials_course_id" in index_names
    assert "ix_materials_uploaded_by" in index_names


@pytest.mark.asyncio
async def test_material_defaults_to_pending(db_session):
    owner = await _create_user(
        db_session,
        "material-pending-subject",
        "material-pending@example.com",
    )
    course = await _create_course(db_session, owner)

    material = await _create_material(db_session, course, owner)

    assert material.status == "pending"

    await db_session.delete(owner)
    await db_session.commit()


@pytest.mark.asyncio
async def test_deleting_course_cascades_to_materials(db_session):
    owner = await _create_user(
        db_session,
        "material-course-cascade-subject",
        "material-course-cascade@example.com",
    )
    course = await _create_course(db_session, owner)
    material = await _create_material(db_session, course, owner)

    await db_session.delete(course)
    await db_session.commit()

    result = await db_session.execute(
        select(Material).where(Material.id == material.id)
    )
    assert result.scalar_one_or_none() is None

    await db_session.delete(owner)
    await db_session.commit()


@pytest.mark.asyncio
async def test_deleting_user_cascades_to_materials(db_session):
    owner = await _create_user(
        db_session,
        "material-user-cascade-subject",
        "material-user-cascade@example.com",
    )
    course = await _create_course(db_session, owner)
    material = await _create_material(db_session, course, owner)

    await db_session.delete(owner)
    await db_session.commit()

    result = await db_session.execute(
        select(Material).where(Material.id == material.id)
    )
    assert result.scalar_one_or_none() is None
