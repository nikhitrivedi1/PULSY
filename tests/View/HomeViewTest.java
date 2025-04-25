package View;

import static org.junit.jupiter.api.Assertions.*;

import Controller.HomeController;
import ENUMS.HomePageStates;
import ENUMS.SPEAKER;
import Model.HomeModel;
import javax.swing.JButton;
import javax.swing.JTextField;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class HomeViewTest {
  private HomeView homeView;
  private HomeController homeController;
  private JButton homeButton;
  private JButton deviceButton;
  private JTextField textField;

  /*
  Additional Test Coverage to be integrated after additional functionality is added
  Need to add data structure to keep track of conversation history - for both sending to the LLM + saving for future usages
  Need to add tests for device add page -> this is not yet developed -> will also add button tests for device detail page
  Need to additionally add provisions for submitting on a blank prompt -> for the user input field
   */

  @BeforeEach
  void setUp() {
    // Create View and Controller for the Home Page
    homeView = new HomeView();
    HomeModel homeModel= new HomeModel();
    homeController = new HomeController(homeView,homeModel);
    homeController.go();

    deviceButton = homeView.getDeviceButton();
    homeButton =  homeView.getHomeButton();
    textField = homeView.getTextField();
  }

  @Test
  void testDeviceButton(){
    // test is to ensure that by clicking the device button on the navigation panel - the state of the page changes
    deviceButton.doClick();
    assertEquals(HomePageStates.DEVICE_LIST, homeView.getState());

    // click the home button and try the device button one more time
    homeButton.doClick();

    deviceButton.doClick();
    assertEquals(HomePageStates.DEVICE_LIST, homeView.getState());
  }

  @Test
  void testHomeButton(){
    // navigate to the device list and get back to test
    deviceButton.doClick();
    homeButton.doClick();
    assertEquals(HomePageStates.CHAT, homeView.getState());

    // since other buttons are not yet active - we will be ok with one assertion here
    // until further dev work is completed
  }

  @Test
  void testChatInputButton(){
    // testing to be done by checking the number of messages - since each individual message is not accessible yet
    // future improvement would be to store these messages in a map or some other data structure and just have access to that
    // this will also help with future improvements to passing information to the RAG block

    textField = homeView.getTextField();
    textField.setText("You're a wizard Harry");
    // click the input button
    JButton inputButton = homeView.getInputButton();
    inputButton.doClick();

    // 3 because of the default intro message + LLM response as well
    assertEquals(3, homeView.getNumberMessages());

    // try one more
    textField.setText("A Wizard?");
    inputButton.doClick();
    assertEquals(5, homeView.getNumberMessages());
  }

  @Test
  void getUserText() {
    // Test to ensure that this getter is able to extract the correct user input
    textField.setText("Hello this is test #1");
    assertEquals("Hello this is test #1", homeView.getUserText());

    // second text
    textField.setText("Hello this is test #2");
    assertEquals("Hello this is test #2", homeView.getUserText());
  }

  @Test
  void addMessageToChat() {
    // again we will be using the message counter here -> however, in the future we want to have a structure in place
    // to get all of the conversation history

    // insert AI message
    homeView.addMessageToChat("This is Pulsy", SPEAKER.AI);
    assertEquals(2,homeView.getNumberMessages());

    homeView.addMessageToChat("This is a person", SPEAKER.USER);
    assertEquals(3, homeView.getNumberMessages());
  }
}