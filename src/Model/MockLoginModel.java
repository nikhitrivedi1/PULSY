package Model;

/**
 * Mock class for the LoginModel to aid in the testing of the LoginController class
 */
public class MockLoginModel implements Model{
  private final StringBuilder log;

  /**
   * Constructor for the MockLoginModel()
   * initializes the log attribute for method usage
   */
  public MockLoginModel(){
    log = new StringBuilder();
  }

  /**
   * Mock class Method to test Login Controller is passing in correct values for the authenticate method
   * @param username - userName of the user passed in from the getUserName method
   * @param password - password of the user passed in from the getPassword method
   * @return - defaulted to true but will append to log for actual content assertion
   */
  public boolean authenticate(String username, String password){
    log.append("Passed Username: " + username + "Password: " + password);
    log.append(System.lineSeparator());

    // return a boolean
    return true;
  }

  /**
   * getter for the Log attribute
   * used for asserting the actual values of the passed username and password strings
   * @return returns the username and password as formatted strings
   */
  public String getLog(){
    return log.toString();
  }
}
