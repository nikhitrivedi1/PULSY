package ApiHandling;

import java.io.IOException;
import java.net.ConnectException;
import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;

/**
 * mock class for the HttpRequestQuery
 */
public class MockHttpRequestQuery {
  private final HttpClient client;
  private HttpRequest request;

  /**
   * mock constructor - initialize client
   */
  public MockHttpRequestQuery(){
    // create client
    client = HttpClient.newHttpClient();
  }


  /**
   * mock sendGETRequest - intention is to see how application handles IO Exception
   * I don't think this is the correct way to test the HTTP REquest - likely need more guidance here
   * @param query - user query from the textfield
   * @param metricDetails - metricDetails from the devices class
   * @return - will not return anything by the exception
   * @throws IOException - thrown exception for testing purposes
   */
  public String mockSendGETRequestIO(String query, String metricDetails) throws IOException{
    try{
      throw new IOException();
    } catch (IOException e) {
      // Moving the Error to the Model to handle
      // this is an unrecoverable error here
      throw new RuntimeException(e);
    }
  }

  /**
   * mock sendGETRequest - intention is to see how application handles IO Exception
   * I don't think this is the correct way to test the HTTP REquest - likely need more guidance here
   * @param query - user query from the textfield
   * @param metricDetails - metricDetails from the devices class
   * @return - will not return anything by the exception
   * @throws InterruptedException - thrown exception for testing purposes
   */
  public String mockSendGETRequestInterrupt(String query, String metricDetails) throws InterruptedException{
    try{
      throw new InterruptedException();
    } catch (InterruptedException e) {
      // Moving the Error to the Model to handle
      // this is an unrecoverable error here
      throw new RuntimeException(e);
    }
  }

  /*
    Formats the LLM response - there appears to be a discrepancy between the response format and the accepted
    format by the Java Application
     */
  private String formatResponse(String unformattedString){
    unformattedString = unformattedString.replace("\"","");
    String[] lines = unformattedString.split("\n");
    // concatinate all of these lines
    String formattedResponse = "";
    for (String line:lines){
      formattedResponse+= (line + "\n");
    }
    return formattedResponse;
  }
}
