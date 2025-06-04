package Controller;

import static org.junit.jupiter.api.Assertions.*;

import Model.HomeModel;
import Model.MockHomeModel;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

// TODO: Since the HomeModel test cases already test the functionality of the getDevice and setDevice methods
// TODO: I don't think test coverage here is necessary - because there are no passed arguments?
class HomeControllerTest {
  // mock home model will be used to test sendLLMQuery()
  // remaining methods can be covered in HomeModel() since they are getters
  private HomeController homeController;
  private MockHomeModel mockHomeModel;
  private HomeModel homeModel;

  @BeforeEach
  void setUp() {
    // initialize mockHome Model
    mockHomeModel = new MockHomeModel();
    homeModel = new HomeModel();
  }

  @Test
  void go() {
  }

  @Test
  void addMessageToChatHistory() {
  }

  @Test
  void createQuery() {
    // create sample query and metrics descriptions
    String sampleQuery1 = "Hi Pulsey - what are my sleep scores?";
    String sampleDescription1 = "Sleep Score: how well you slept on a scale from 0-100 - based on several factors";
    String expectedResponse = "Query: " + sampleQuery1 + System.lineSeparator() + " Metrics: " + sampleDescription1;
    assertEquals(expectedResponse, mockHomeModel.sendQueryToLLM(sampleQuery1, sampleDescription1));

    // Create a second sample Query
    String sampleQuery2 = "Is there a correlation between my heart rate and sleep scores?";
    String sampleDescription2 = "Heart Rate - measured in bpm, captured at time intervals throughout the day";
    String expectedResponse2 = "Query: " + sampleQuery2 + System.lineSeparator() + " Metrics: " + sampleDescription2;
    assertEquals(expectedResponse2, mockHomeModel.sendQueryToLLM(sampleQuery2, sampleDescription2));
  }

  @Test
  void getDeviceList() {
    // utilizing the normal HomeModel instance
  }

  @Test
  void showDevicePage() {
  }
}