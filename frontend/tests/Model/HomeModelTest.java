package Model;

import static org.junit.jupiter.api.Assertions.*;

import Wearables.OuraRing;
import Wearables.Wearables;
import java.lang.reflect.Array;
import java.util.ArrayList;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class HomeModelTest {
  private HomeModel homeModel;
  private ArrayList<Wearables> testArr;
  private OuraRing o1, oFalse;

  @BeforeEach
  void setUp() {
    // Home Model
    homeModel = new HomeModel();
    testArr = new ArrayList<>();

    o1 = new OuraRing(
        "029847300",
        "Oura Ring is the first wearable designed to paint a truly holistic picture of your health. Born in Finland, our superior craftsmanship and human-centered philosophy give way to a wellness product loved by millions.",
        "*********************"
    );

    oFalse =  new OuraRing(
        "2817",
        "Oura Ring is the first wearable designed to paint a truly holistic picture of your health. Born in Finland, our superior craftsmanship and human-centered philosophy give way to a wellness product loved by millions.",
        "*********************"
    );
  }

  // TODO: This is a BIG TEST CASE -> WORK ON IT WITH A BETTER UNDERSTANDING
  // TODO: Not sure if it is necessary to test exact frameworks
  @Test
  void sendQueryToLLM() {
  }

  @Test
  void getDeviceList() {
    // add o1 to array list - for test purposes
    testArr.add(o1);

    // in this case we are assuming only one device per person
    assertEquals(testArr, homeModel.getDeviceList());

    // in this case we are assuming only one device per person
    assertNotEquals(oFalse, homeModel.getDeviceList());
  }

  @Test
  void setDeviceList(){
    // create new device and add it to the device list
    // for assertions test whether the device was added to the end of the array list
    // add to device list - constructor pre-loads one device onto the list

    // recreate arraylist using
    testArr.add(o1);
    testArr.add(oFalse);

    homeModel.setDeviceList(oFalse);
    assertEquals(testArr, homeModel.getDeviceList());

    // test for True Negative
    testArr.add(oFalse);
    homeModel.setDeviceList(o1);
    assertNotEquals(testArr, homeModel.getDeviceList());
  }

}