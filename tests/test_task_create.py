import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from datetime import datetime
from tasks_manager.models import Team, Position, Project, TaskType, Worker, Task

# --- Selenium helpers ---
def wait_until_visible(driver, by, value, timeout=10):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, value))
    )

def wait_until_clickable(driver, by, value, timeout=10):
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, value))
    )

# --- Fixtures ---
@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()

@pytest.fixture
def project_with_user(django_user_model):
    """Create a team, user, and project."""
    team, _ = Team.objects.get_or_create(name="team")
    position = Position.objects.create(name="Creator", team=team)
    user = django_user_model.objects.create_user(
        username="tester",
        password="password",
        team=team,
        position=position
    )
    project = Project.objects.create(name="Test Project", team=team)
    return user, team, project

@pytest.fixture
def login(driver, live_server, project_with_user):
    user, _, _ = project_with_user
    driver.get(f"{live_server.url}/login/")
    wait_until_visible(driver, By.NAME, "username").send_keys(user.username)
    driver.find_element(By.NAME, "password").send_keys("password")
    wait_until_clickable(driver, By.CSS_SELECTOR, "button[type='submit']").click()
    return driver


# --- Django DB test: create task ---
@pytest.mark.django_db
def test_create_task_in_db(project_with_user):
    user, team, project = project_with_user

    # Create a TaskType to use
    task_type = TaskType.objects.create(name="Bug", team=team)

    # Create the task
    task = Task.objects.create(
        name="Fix login bug",
        description="Login page throws 500 error",
        project=project,
        task_type=task_type,
        deadline=datetime.now()
    )
    task.assignees.add(user)
    task.save()

    # --- Assertions ---
    task_from_db = Task.objects.get(pk=task.pk)
    assert task_from_db.name == "Fix login bug"
    assert task_from_db.project == project
    assert task_from_db.task_type == task_type
    assert user in task_from_db.assignees.all()
