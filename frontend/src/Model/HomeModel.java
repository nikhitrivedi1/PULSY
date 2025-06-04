package Model;

import Wearables.Wearables;
import Wearables.OuraRing;
import ApiHandling.HttpRequestQuery;
import java.io.IOException;
import java.util.ArrayList;

/**
 * Home Model Class - Model Class for the main Home Page
 */
// Design Rules:
public class HomeModel {
  private final ArrayList<Wearables> deviceList;

  /**
   * Home Model Constructor
   * initializes the ArrayList of Wearables
   * calls the loadDeviceList() method to add the default OuraRing Object to the list
   */
  public HomeModel(){
    // Initialize the ArrayList for now with only Oura Ring
    this.deviceList = new ArrayList<>();
    loadDeviceList();
  }

  /**
   * sends the query and wearables mtrics descriptions to the LLM for processing
   * utilizes the HTTPRequestQuery() class to execute the GET Request
   * @param query - the question prompted by the user
   * @param metricDescriptions - descriptions of the wearable health metrics based on user device list
   * @return - returns the response from the LLM
   */
  public String sendQueryToLLM(String query, String metricDescriptions){
    try{
      long start = System.currentTimeMillis();
      // create HTTP Request Object
      HttpRequestQuery q1 = new HttpRequestQuery();
      String response = q1.sendGETRequest(query, metricDescriptions);
      long end = System.currentTimeMillis();
      System.out.println("TIME to get response: ");
      System.out.println(end-start);
      return response;
    } catch (IOException | InterruptedException | RuntimeException e) {
      // return the error to the user indicating to them that there is a connection issue
      // most likely indicates that there is a connection issue between the REST API and the Java Application
      return "Hmmm......There appears to be an issue with connecting to my central brain - try double checking your internet connection";
    }
  }

  /**
   * Getter for the Device List
   * @return - returns the full arraylist
   */
  public ArrayList<Wearables> getDeviceList() {
    return deviceList;
  }

  /**
   * adds a device of instance Wearable to the ArrayList(Wearables)
   * new device is added to the end of the Arraylist
   * @param device - the device that will be added to the Arraylist
   */
  public void setDeviceList(Wearables device){
    deviceList.add(device);
  }

  /*
   * called during initialization
   * preloads the device list with the default o1 Oura Ring Instance
   * Purely for demo purposes - will update with DB once full working interface is available
   */
  private void loadDeviceList(){
    // Create new instance of the Oura Ring - this will eventually be stored in a DB and loaded
    OuraRing o1 = new OuraRing(
        "029847300",
        "Oura Ring is the first wearable designed to paint a truly holistic picture of your health. Born in Finland, our superior craftsmanship and human-centered philosophy give way to a wellness product loved by millions.",
        "*********************"
    );
    this.setDeviceList(o1);
  }

}
