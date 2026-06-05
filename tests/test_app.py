import pytest


class TestRootRedirect:
    """Test GET / endpoint"""

    def test_redirect_to_static_index(self, client):
        # Arrange
        expected_redirect_url = "/static/index.html"

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == expected_redirect_url


class TestGetActivities:
    """Test GET /activities endpoint"""

    def test_get_all_activities_returns_nine(self, client):
        # Arrange - no setup needed

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == 9

    def test_get_activities_returns_correct_structure(self, client):
        # Arrange
        required_keys = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_details in activities.items():
            assert isinstance(activity_name, str)
            assert activity_details.keys() == required_keys
            assert isinstance(activity_details["description"], str)
            assert isinstance(activity_details["schedule"], str)
            assert isinstance(activity_details["max_participants"], int)
            assert isinstance(activity_details["participants"], list)

    def test_get_activities_participants_are_emails(self, client):
        # Arrange - no setup needed

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_details in activities.values():
            for participant in activity_details["participants"]:
                assert isinstance(participant, str)
                assert "@" in participant


class TestSignupForActivity:
    """Test POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self, client):
        # Arrange
        activity_name = "Chess Club"
        test_email = "new-student@mergington.edu"
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )

        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        
        # Verify participant was added
        updated_response = client.get("/activities")
        updated_count = len(updated_response.json()[activity_name]["participants"])
        assert updated_count == initial_count + 1
        assert test_email in updated_response.json()[activity_name]["participants"]

    def test_signup_already_registered_returns_400(self, client):
        # Arrange
        activity_name = "Chess Club"
        existing_participant = "michael@mergington.edu"  # Already in Chess Club

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_participant}
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()

    def test_signup_invalid_activity_returns_404(self, client):
        # Arrange
        invalid_activity = "Nonexistent Club"
        test_email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{invalid_activity}/signup",
            params={"email": test_email}
        )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_with_special_characters_in_email(self, client):
        # Arrange
        activity_name = "Programming Class"
        test_email = "test+tag@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )

        # Assert
        assert response.status_code == 200
        assert test_email in client.get("/activities").json()[activity_name]["participants"]


class TestRemoveParticipant:
    """Test DELETE /activities/{activity_name}/participants/{email} endpoint"""

    def test_remove_participant_success(self, client):
        # Arrange
        activity_name = "Chess Club"
        participant_to_remove = "michael@mergington.edu"
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{participant_to_remove}"
        )

        # Assert
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]

        # Verify participant was removed
        updated_response = client.get("/activities")
        updated_count = len(updated_response.json()[activity_name]["participants"])
        assert updated_count == initial_count - 1
        assert participant_to_remove not in updated_response.json()[activity_name]["participants"]

    def test_remove_nonexistent_participant_returns_404(self, client):
        # Arrange
        activity_name = "Chess Club"
        nonexistent_email = "nobody@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{nonexistent_email}"
        )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_remove_from_invalid_activity_returns_404(self, client):
        # Arrange
        invalid_activity = "Nonexistent Club"
        test_email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{invalid_activity}/participants/{test_email}"
        )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
