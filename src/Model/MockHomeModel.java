package Model;

/**
 * mock model for testing Controller - utilized for testing
 */
public class MockHomeModel implements Model{

  /**
   * mock model constructor - no initializations needed
   */
  public MockHomeModel(){
  }

  /**
   * mock method for sendQuerytoLLM to return query provided by the Controller
   * @param query - query from the controller passed as a string
   * @param metricDescriptions - descriptions of device metrics passed from controller
   * @return - returns formatted string to determine success of the test
   */
  public String sendQueryToLLM(String query, String metricDescriptions){
    // don't need to test the Exception errors - this will be handled by the model
    return "Query: " + query + System.lineSeparator() + " Metrics: " + metricDescriptions;
  }
}
