package Controller;

import Model.HomeModel;
import Model.LoginModel;
import View.HomeView;
import View.LoginView;

/**
 * Act as a Controller for the entire Application
 */
public class AppController implements Controller {

  /**
   * Controller constructor - directly calls go method upon initialization
   */
  public AppController(){
    go();
  }

  // this is the landing page whenever the app is run

  /**
   * Landing Page when application starts
   * @param args - any input arguments from the user upon start (not utilized at this time)
   */
  public static void main(String[] args){
    AppController start = new AppController();
  }

  /**
   * go method for App Controller -> deligates control to the loginController
   * creates login page upon start up
   */
  public void go(){
    showLoginPage();
  }

  /**
   * initializes instances of the Login Model, View, Controller and sends control to Login Controller
   */
  public void showLoginPage(){
    // Create instances of the login page
    LoginView loginView = new LoginView();
    LoginModel loginModel = new LoginModel();
    LoginController loginController = new LoginController(loginModel,loginView,this);
    loginController.go();
  }

  /**
   * called after successful Login
   * hands control over to Home Controller to create a Home Page
   */
  public void showMainPage(){
    // Create Instances of the Login Page
    HomeView homeView = new HomeView();
    HomeModel homeModel = new HomeModel();
    HomeController homeController = new HomeController(homeView, homeModel);
    homeController.go();
  }
}
