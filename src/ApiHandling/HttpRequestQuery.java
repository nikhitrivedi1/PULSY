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
 * HTTP Request Query Builder Class
 * creates the GET request for the application to interface with the REST API
 */
public class HttpRequestQuery {
  private final HttpClient client;
  private HttpRequest request;

  /**
   * Constructor - initializes the HTTP Client
   */
  public HttpRequestQuery(){
    // Create client
    client = HttpClient.newHttpClient();
  }

  /**
   * configures the GET request with query and metric details from the devices
   * @param query - query provided by the user - the question the LLM will attempt to answer - encoded into URL
   * @param metricDetails - the details of metrics offered by the device
   * @return - the response from the LLM
   * @throws IOException - if an error occurs when sending or receiving, or the client has shut down
   * @throws InterruptedException - thrown when there is a manual interruption of the connection
   * thrown errors will be handled at the Model level for user interface actions
   */
  // TODO: Look into ALL of the thrown exceptions for the client.send class - double check this
  public String sendGETRequest(String query, String metricDetails) throws IOException, InterruptedException{
    try{
      String encodedDescriptions = URLEncoder.encode(metricDetails, StandardCharsets.UTF_8);
      String encodedQuery = URLEncoder.encode(query, StandardCharsets.UTF_8);
      String stringUrl = "http://127.0.0.1:8000/query/?query=" + encodedQuery + "&descriptions=" + encodedDescriptions;
      request = HttpRequest.newBuilder()
          .uri(URI.create(stringUrl))
          .GET()
          .build();
      HttpResponse<String> response = client.send(request,HttpResponse.BodyHandlers.ofString());
      // Clean Up Response Formatting
      return formatResponse(response.body());
    } catch (InterruptedException | IOException e) {
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
