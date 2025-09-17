import pytest
from django.core.exceptions import ObjectDoesNotExist
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from tasks_manager.models import Project, Position, Team


@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()


@pytest.mark.django_db
def test_delete_project_selenium(live_server, driver, django_user_model):
    team = Team.objects.create(name="team")
    user = django_user_model.objects.create_user(
        username="tester",
        password="password",
        team=team,
        position=Position.objects.create(name="Creator", team=team)
    )

    driver.get(f"{live_server.url}/login/")
    driver.find_element(By.NAME, "username").send_keys("tester")
    driver.find_element(By.NAME, "password").send_keys("password")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    project = Project.objects.create(name="Test Project", team=user.team)
    driver.get(f"{live_server.url}/projects/")

    delete_button = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, f"button.remove-task-btn[data-project-id='{project.pk}']"))
    )
    delete_button.click()

    WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.ID, "deleteModal"))
    )

    modal_title = driver.find_element(By.CSS_SELECTOR, "#deleteModal h2").text
    assert "Delete Project" in modal_title

    driver.find_element(By.ID, "confirmDeleteBtn").click()

    WebDriverWait(driver, 5).until(
        EC.invisibility_of_element_located((By.ID, "deleteModal"))
    )

    with pytest.raises(ObjectDoesNotExist):
        Project.objects.get(pk=project.pk)
