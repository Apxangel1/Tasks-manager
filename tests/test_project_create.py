import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from tasks_manager.models import Project, Team, Position

User = get_user_model()


@pytest.mark.django_db
def test_project_create_success(client):
    team = Team.objects.create(name="Alpha Team")
    user = User.objects.create_user(
      username="bob",
      password="Pass123!",
      team=team,
      position=Position.objects.create(name="Creator",team=team))
    client.login(username="bob", password="Pass123!")

    url = reverse("project_create")
    form_data = {"name": "New Project", "description": "Test project"}
    response = client.post(url, form_data, follow=True)

    assert response.redirect_chain[-1][0].endswith(reverse("projects"))

    project = Project.objects.get(name="New Project")
    assert project.team == team


@pytest.mark.django_db
def test_project_create_duplicate_name_fails(client):
    team = Team.objects.create(name="Alpha Team")
    user = User.objects.create_user(
      username="bob",
      password="Pass123!",
      team=team,
      position=Position.objects.create(name="Creator",team=team))
    client.login(username="bob", password="Pass123!")

    Project.objects.create(name="Duplicate", description="x", team=team)

    url = reverse("project_create")
    form_data = {"name": "Duplicate", "description": "Another project"}
    response = client.post(url, form_data)

    assert response.status_code == 200
    assert b"A project with this name already exists" in response.content
    assert Project.objects.filter(name="Duplicate", team=team).count() == 1


@pytest.mark.django_db
def test_project_create_allows_same_name_in_different_teams(client):
    team1 = Team.objects.create(name="Alpha Team")
    team2 = Team.objects.create(name="Beta Team")

    user = User.objects.create_user(
      username="bob",
      password="Pass123!",
      team=team1,
      position=Position.objects.create(name="Creator",team=team1))

    user2 = User.objects.create_user(
      username="alice",
      password="Pass123!",
      team=team2,
      position=Position.objects.create(name="Creator",team=team2))

    Project.objects.create(name="Shared Name", description="x", team=team1)

    client.login(username="alice", password="Pass123!")

    url = reverse("project_create")
    form_data = {"name": "Shared Name", "description": "y"}
    response = client.post(url, form_data, follow=True)

    assert response.redirect_chain[-1][0].endswith(reverse("projects"))
    assert Project.objects.filter(name="Shared Name", team=team2).exists()

@pytest.mark.django_db
def test_project_create_shows_error_message(client):
    User = get_user_model()

    team = Team.objects.create(name="Test Team")
    user2 = User.objects.create_user(
      username="alice",
      password="Pass123!",
      team=team,
      position=Position.objects.create(name="Creator",team=team))
    client.login(username="alice", password="Pass123!")

    Project.objects.create(name="Existing", description="x", team=team)

    url = reverse("project_create")
    form_data = {"name": "Existing", "description": "Duplicate test"}
    response = client.post(url, form_data)

    assert response.status_code == 200
    assert b"A project with this name already exists" in response.content
