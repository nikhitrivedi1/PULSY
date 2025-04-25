package Wearables;

import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class OuraRingTest {
  private OuraRing o1, o2;

  @BeforeEach
  void setUp() {
    // create instance of Oura Ring
    // Create Oura Ring Objects for testing
    o1 = new OuraRing("12345", "Use it for sleep and heart rate insights", "************");
    o2 = new OuraRing("54321", "Utilize it for detecting stress", "*******");
  }

  @Test
  void getDeviceIcon() {
    assertEquals("src/assets/OuraIcon.png", o1.getDeviceIcon());
    assertEquals("src/assets/OuraIcon.png", o2.getDeviceIcon());
  }

  @Test
  void getDeviceName() {
    assertEquals("Oura Ring", o1.getDeviceName());
    assertEquals("Oura Ring", o2.getDeviceName());
  }

  @Test
  void getMetricDescriptions() {
    assertEquals(
        "{Deep Sleep=Deep sleep is the most restorative and rejuvenating sleep stage. It includes all your sleep, including naps, Sleep Score=Your Sleep Score reflects the quality and quantity of your sleep by analyzing key factors like sleep stages, restfulness, and timing. Learn what affects your score and how you can work toward better sleep, Restfulness=Restfulness tracks your wake-ups, excessive movement, and how often you get out of bed during sleep. It takes into account all your sleep, including naps., REM Sleep=REM (rapid eye movement) sleep is associated with dreaming, memory consolidation, and creativity. It plays an important role in re-energizing both your mind and body, and includes all your sleep, including naps., Sleep Efficiency=Sleep efficiency reflects the percentage of time spent asleep compared to the time spent awake while in bed. It takes into account all sleep, including naps., Timing=The Timing contributor takes into account all your sleep, including naps. Optimally, the midpoint of your sleep should fall between midnight and 3am, though this can vary depending on whether you're a morning or evening type. If you feel tired during the day, the best time to nap is usually in the early afternoon., Total Sleep=Total sleep reflects the amount of time spent in light, REM, and deep sleep. All your sleep is taken into account, including naps., Sleep Latency=Sleep latency measures how long it takes you to fall asleep at night. It’s only tracked for your longest sleep period.}", o1.getMetricDescriptions());
    assertEquals(
        "{Deep Sleep=Deep sleep is the most restorative and rejuvenating sleep stage. It includes all your sleep, including naps, Sleep Score=Your Sleep Score reflects the quality and quantity of your sleep by analyzing key factors like sleep stages, restfulness, and timing. Learn what affects your score and how you can work toward better sleep, Restfulness=Restfulness tracks your wake-ups, excessive movement, and how often you get out of bed during sleep. It takes into account all your sleep, including naps., REM Sleep=REM (rapid eye movement) sleep is associated with dreaming, memory consolidation, and creativity. It plays an important role in re-energizing both your mind and body, and includes all your sleep, including naps., Sleep Efficiency=Sleep efficiency reflects the percentage of time spent asleep compared to the time spent awake while in bed. It takes into account all sleep, including naps., Timing=The Timing contributor takes into account all your sleep, including naps. Optimally, the midpoint of your sleep should fall between midnight and 3am, though this can vary depending on whether you're a morning or evening type. If you feel tired during the day, the best time to nap is usually in the early afternoon., Total Sleep=Total sleep reflects the amount of time spent in light, REM, and deep sleep. All your sleep is taken into account, including naps., Sleep Latency=Sleep latency measures how long it takes you to fall asleep at night. It’s only tracked for your longest sleep period.}", o2.getMetricDescriptions());
  }
}