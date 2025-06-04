package Controller;

import static org.junit.jupiter.api.Assertions.*;

import Model.HomeModel;
import Model.MockLoginModel;
import Wearables.Wearables;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class LoginControllerTest {
  MockLoginModel mockLoginModel;

  @BeforeEach
  void setUp() {
    // Utilize the Mock Login Model
    mockLoginModel = new MockLoginModel();
  }

  @Test
  void go() {
  }


  @Test
  void modelAuthenticate() {
    // Test Passed variables to the login model
    String userName1 = "Nikhil";
    String password1 = "1234";

    // two asssertions - one for confirming pass variables and second for confirming boolean as true
    assertTrue(mockLoginModel.authenticate(userName1, password1));
    String expectedString = "Passed Username: " + userName1 + "Password: " + password1;
    assertEquals(expectedString + System.lineSeparator() , mockLoginModel.getLog());

    // same here - except we are expecting a longer expected string from log since it is appended
    String userName2 = "JoeMontana";
    String password2 = "16";
    assertTrue(mockLoginModel.authenticate(userName2, password2));
    String expectedString2 = "Passed Username: " + userName2 + "Password: " + password2;
    assertEquals(expectedString + System.lineSeparator() + expectedString2 + System.lineSeparator(), mockLoginModel.getLog());
  }
}