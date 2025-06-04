package View;

import static org.junit.jupiter.api.Assertions.*;

import Controller.AppController;
import Controller.LoginController;
import Model.LoginModel;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class LoginViewTest {
  private LoginController loginController;
  private LoginView loginView;

  @BeforeEach
  void setUp() {
    // initialize loginView and execute the go method for loginController
    loginView = new LoginView();
    loginController = new LoginController(new LoginModel(), loginView, new AppController());
    loginController.go();
  }

  @Test
  void testLoginButton(){
    // Test covers the following view methods
    // getUsername
    // getPassword
    // close
    // show LoginError

    // Test the Login Button - ensure that upon pressing login it returns the correct elements
    // should be blank since no user or no password
    // test the situation where login in invalid (blank)
    loginView.getLoginButton().doClick();
    assertEquals("Invalid Login!", loginView.getLoginButton().getText());

    // test the succesful case - in which case the window is closed
    loginView.setUsernameText("Nikhil");
    loginView.setPasswordField("1234");
    loginView.getLoginButton().doClick();
    assertTrue(loginView.isClosed());
  }

  @Test
  void getUsername() {
    // set the username field
    loginView.setUsernameText("Hello");
    assertEquals("Hello", loginView.getUsername());

    loginView.setUsernameText("103834792920");
    assertEquals("103834792920", loginView.getUsername());
  }

  @Test
  void getPassword() {
    //set the password field
    loginView.setPasswordField("You may not Pass!");
    assertEquals("You may not Pass!", loginView.getPassword());

    loginView.setPasswordField("1938377");
    assertEquals("1938377", loginView.getPassword());
  }

  @Test
  void close() {
    assertFalse(loginView.isClosed());

    loginView.close();
    assertTrue(loginView.isClosed());
  }
}