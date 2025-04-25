package Controller;

import Model.HomeModel;
import View.HomeView;
import Wearables.Wearables;
import ENUMS.SPEAKER;
import java.util.ArrayList;


/**
 * Home Controller Class for the Main Application Page
 */
public class HomeController implements Controller{
  private final HomeView homeView;
  private final HomeModel homeModel;

  /**
   * Home Controller Constructor
   * @param homeView - HomeView instance for method calls to the main page GUI
   * @param homeModel - HomeModel instance for method calls for REST API and LLMs
   */
  public HomeController(HomeView homeView, HomeModel homeModel){
    this.homeView = homeView;
    this.homeModel = homeModel;
  }

  /**
   * go()
   * Initialize and show the home page of the application
   * Welcome Message to be presented by Pulsey
   * method call to set up all action event listeners from the HomeView
   */
  public void go(){
    this.homeView.createHomeView();
    // Default Home View with Welcome Message
    String welcomeMessage = "Hi my name is Pulsy and I am your AI designed to help you extract value and understanding from your wearables data - how can I help you today?";
    // Default Message to welcome the user to Pulsey
    this.homeView.addMessageToChat(welcomeMessage, SPEAKER.AI);
    // set up action Listeners
    setUpActionListeners();
  }

  // Methods for Home Functionality

  /**
   * addMessageToChatHistory()
   * will update the chat area with either input questions from the user or responses from the LLM
   * method call directly to the view to update this area
   * @param msg - message to be added to the HomeView
   * @param speaker - SPEAKER field to define who is sending this message
   */
  public void addMessageToChatHistory(String msg, SPEAKER speaker){
    this.homeView.addMessageToChat(msg,speaker);
  }

  /**
   * Gathers user input message from the HomeView and device information from the HomeModel for query formulation
   * message from the user will be pushed to the Chat History Element in HomeView
   * Message from the user and device details from deviceList will be sent to HomeModel for REST API Call
   * The response from the RESTAPI (sendQueryToLLM) will be added to the ChatHistory
   * @param msg - message from the user input field in the HomeView
   */
  public void createQuery(String msg){
    // add message to chat history
    addMessageToChatHistory(msg, SPEAKER.USER);

    // get the relevant Metric
    // TODO: hard coded for only one device right now -> will build out
    String deviceMetricDetails = this.homeModel.getDeviceList().getFirst().getMetricDescriptions();

    // also send the query to the LLM for a response
    String response = homeModel.sendQueryToLLM(msg, deviceMetricDetails);

    addMessageToChatHistory(response, SPEAKER.AI);
  }

  /**
   * Getter for the Wearable Device List from the Model
   * @return - Device list comprising of all sub-class instances of the Wearable interface
   */
  public ArrayList<Wearables> getDeviceList(){
    return this.homeModel.getDeviceList();
  }

  /**
   * will update the homeView to show the device page if the user selects the devices button in the navigation panel
   */
  public void showDevicePage(){
    this.homeView.createDevicePagePanel(getDeviceList());
  }

  // Private Scoped Functions
  private void setUpActionListeners(){
    // Add Action Listener for all the buttons
    homeView.addInputButtonListener(e ->
        createQuery(homeView.getUserText())
    );

    // modify the homeView to show the device page instead of the home page
    homeView.addDeviceButtonListener(e ->
        showDevicePage()
    );

    homeView.addHomeButtonListener(e ->
        go()
    );
  }
}
