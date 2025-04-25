package ApiHandling;

import static org.junit.jupiter.api.Assertions.*;

import java.io.IOException;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class HttpRequestQueryTest {
  private HttpClient client;
  private HttpRequest request;
  private HttpRequestQuery query;
  private MockHttpRequestQuery mockQuery;

  @BeforeEach
  void setUp() {
    // set up http client and instance of the HTTPRequestQuery + Mock
    query = new HttpRequestQuery();
    mockQuery = new MockHttpRequestQuery();
  }

  @Test
  void sendGETRequest() throws IOException, InterruptedException {
    // Success Case -> ensure the REST API is running prior to testing
    // since the LLM response will vary even given the same prompt -> we can only test the type that is returned
    assertEquals(String.class, query.sendGETRequest("What can you do Pulsy", "Oura Ring Sleep Score: Hello").getClass());
//    assertDoesNotThrow(query.sendGETRequest("What can you do Pulsy", "Oura Ring Sleep Score: Hello"));

    // induce an IO Exception
    assertThrows(RuntimeException.class, () ->
        mockQuery.mockSendGETRequestIO("What can you do Pulsy", "Oura Ring Sleep Score: Hello"));

    // induce an Interrupt Exception
    assertThrows(RuntimeException.class, () ->
        mockQuery.mockSendGETRequestInterrupt("What can you do Pulsy", "Oura Ring Sleep Score: Hello"));
  }
}