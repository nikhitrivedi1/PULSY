package Wearables;

import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class WearablesAbstractTest {
  private OuraRing o1, o2;

  @BeforeEach
  void setUp() {
    // Create Oura Ring Objects for testing
    o1 = new OuraRing("12345", "Use it for sleep and heart rate insights", "************");
    o2 = new OuraRing("54321", "Utilize it for detecting stress", "*******");
  }

  @Test
  void getDeviceID() {
    assertEquals("12345", o1.getDeviceID());
    assertEquals("54321", o2.getDeviceID());
  }

  @Test
  void setDeviceID() {
    // set a new device ID
    String newID = "abcd";
    o1.setDeviceID(newID);
    assertEquals("abcd", o1.getDeviceID());

    // set new ID for o2
    String newID2 = "dcba";
    o2.setDeviceID(newID2);
    assertEquals(newID2, o2.getDeviceID());
  }

  @Test
  void getDeviceDescription() {
    assertEquals("Use it for sleep and heart rate insights", o1.getDeviceDescription());
    assertEquals("Utilize it for detecting stress", o2.getDeviceDescription());
  }

  @Test
  void setDeviceDescription() {
    String newDesc1 = "I use it because it looks cool";
    o1.setDeviceDescription(newDesc1);
    assertEquals(newDesc1, o1.getDeviceDescription());

    String newDesc2 = "I use it because my friends use it";
    o2.setDeviceDescription(newDesc2);
    assertEquals(newDesc2, o2.getDeviceDescription());
  }

  @Test
  void getAPIKey() {
    assertEquals("************", o1.getAPIKey());
    assertEquals("*******", o2.getAPIKey());
  }

  @Test
  void setAPIKey() {
    String newKey = "thisismynewkey";
    o1.setAPIKey(newKey);
    assertEquals(newKey, o1.getAPIKey());

    String newKey2 = "mynameisJeff";
    o2.setAPIKey(newKey2);
    assertEquals(newKey2, o2.getAPIKey());
  }

  @Test
  void testToString() {
    assertEquals(
        "Name: Oura Ring\nDescription: Use it for sleep and heart rate insights\nID: 12345\n", o1.toString());
    assertEquals("Name: Oura Ring\nDescription: Utilize it for detecting stress\nID: 54321\n", o2.toString());
  }

  @Test
  void testEquals() {
    // positive case - same instance
    assertEquals(o1, o1);

    // positive case - same case different variable
    assertEquals(o1,
        new OuraRing("12345", "Use it for sleep and heart rate insights", "************"));

    // negative case - unequal
    assertNotEquals(o1, o2);
  }

  @Test
  void testHashCode() {
    assertEquals(o1.hashCode(), o1.hashCode());
    assertNotEquals(o1.hashCode(), o2.hashCode());
  }
}