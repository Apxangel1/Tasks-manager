import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from tasks_manager.models import Team, Position


User = get_user_model()

@pytest.mark.django_db
def test_register_page_loads(client):
    url = reverse("signup")
    response = client.get(url)
    assert response.status_code == 200
    assert b"Register" in response.content


@pytest.mark.django_db
def test_register_creates_user_and_team(client):
    url = reverse("signup")
    form_data = {
        "username": "newuser",
        "password1": "StrongPass123!",
        "password2": "StrongPass123!",
        "team_name": "My Test Team"
    }

    response = client.post(url, form_data, follow=True)

    assert response.redirect_chain[-1][0].endswith(reverse("index"))

    user = User.objects.get(username="newuser")
    assert user.team.name == "My Test Team"

    assert Team.objects.filter(name="My Test Team").exists()
    assert Position.objects.filter(name="Creator", team=user.team).exists()

    assert "_auth_user_id" in client.session


@pytest.fixture
def driver():
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(service=service, options=options)
    yield driver
    driver.quit()

@pytest.mark.django_db
def test_username_autofills_team_name(live_server, driver):
    driver.get(live_server.url + "/register/")

    username_input = driver.find_element(By.ID, "id_username")
    team_input = driver.find_element(By.ID, "id_team_name")

    username_input.send_keys("john")

    assert team_input.get_attribute("value") == "john's team"

    team_input.clear()
    team_input.send_keys("Custom Team")

    username_input.send_keys("ny")

    assert team_input.get_attribute("value") == "Custom Team"
