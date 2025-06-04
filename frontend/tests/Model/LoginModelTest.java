package Model;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class LoginModelTest {
  private LoginModel model;

  @org.junit.jupiter.api.BeforeEach
   void setUp(){
    // create instance of the Login Model
     model = new LoginModel();
  }

  @org.junit.jupiter.api.Test
  void authenticate() {
    // Test Case: Known Username and Password
    Assertions.assertTrue(model.authenticate("Nikhil", "1234"));

    // Test Case: Known "New" Username not in DB
    Assertions.assertFalse(model.authenticate("Helos", "hejsks"));
  }
}