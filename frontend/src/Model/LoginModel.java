package Model;

import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;


/**
 * Login Model for handling primarily authentication
 */
public class LoginModel {


  /**
   * Login Model Constructor
   * Handles all model related calls from the Login Controller
   */
  public LoginModel(){
  }

  // Short term store user information, etc in a JSON file locally - check against this

  /**
   * Authenticates the provided username and password using UserDB.json
   * @param username - provided username of the user
   * @param password - provided password of the user from the password field
   * @return - returns false if failed to authenticate - returns true if authenticated
   */
  public boolean authenticate(String username, String password){
    try{
      return searchForUser(username, password);
    } catch (RuntimeException e) {
      throw new RuntimeException(e);
    }
  }

  // TODO: Correctly Address the FileNotFound Exception Here - need to understand better
  // TODO: Add methods for adding username and password
  // TODO: Javadocs not necessary for private function but include notes here for devs
  /*
   * Performs the actual authentication given the passed in username and password
   * utilizes json-simple library to parse the JSON formatted file UserDB.json
   * @param username - provided username of the user - utilized as the key
   * @param password - provided password of the user - utilized as the value
   * @return - NullPointerException will return false since username is not available in DB
   * @throws RuntimeException - handles any Parsing errors with use of JSONparser and IO errors from FileReader
   */
  private boolean searchForUser(String username, String password) throws RuntimeException{
    final String DBPATH = "src/Model/UserDB.json";
    // JSON-Simple Library
    JSONParser parser = new JSONParser();
    try{
      JSONArray a = (JSONArray) parser.parse(new FileReader(DBPATH));
      for(Object o : a){
        JSONObject usernamePasswordPair = (JSONObject) o;
        if(usernamePasswordPair.get(username).equals(password)){
          return true;
        }
      }
    } catch (NullPointerException e) {
      // returns false because username is not in the JSON array
      return false;
    } catch (ParseException | IOException e) {
      throw new RuntimeException(e);
    }
    return false;
  }
}
