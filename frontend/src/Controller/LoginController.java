package Controller;

import Model.LoginModel;
import View.LoginView;

/**
 * Login Controller Class
 * utilizes method calls to handle activities on the Login Page of the application
 * relies on the AppController Class for navigating to home page after successful login
 */
public class LoginController implements Controller {
  private final LoginModel model;
  private final LoginView view;
  private final AppController app;

  /**
   * Login Controller Constructor
   * @param model - passes in instance of Login Model for handling backend processes of Login Page
   * @param view - passes in instance of Login View for handling front end rendering processes of Login Page
   * @param appController - passes in parent instance of appController for directing between application pages
   */
  public LoginController(LoginModel model, LoginView view, AppController appController){
    this.model = model;
    this.view = view;
    this.app = appController;
  }

  /**
   * go()
   * Initializes and builds the Login Panel View for the GUI
   * Initializes Action Event Listeners on the Login Submit Button
   */
  public void go(){
    this.view.showLoginPanel();
    // Create Listener for the Login Button
    this.view.addLoginListener(e -> modelAuthenticate());
  }

  /**
   * modelAuthenticate()
   * Authenticates the username and password fields after the login submit button is pressed
   * username and password fields are extracted using getters in the LoginView
   * Login model then uses these fields and authenticates through model unique methods
   * Will show error if login fails
   * Will navigate to Main Page if Login Passes
   */
  public void modelAuthenticate() {
    if (this.model.authenticate(this.view.getUsername(), this.view.getPassword())) {
      this.app.showMainPage();
      this.view.close();
    } else {
      this.view.showLoginError();
    }
  }
}
