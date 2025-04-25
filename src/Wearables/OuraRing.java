package Wearables;


import ENUMS.DeviceName;
import java.util.HashMap;
import java.util.Map;

/**
 * Oura Ring Class extending the Wearables Abstract
 */
// Design Rule #3: fields are private + private methods are created for internal help functions
// Design Rule #4: no additional public methods aside from those speicifed in the interface
public class OuraRing extends WearablesAbstract {
  private final Map<String, String> metricDescriptions;
  private static final DeviceName name = DeviceName.OURARING;
  private static final String icon = "src/assets/OuraIcon.png";

  /**
   * Oura Ring Constructor
   * @param ID - the specific device ID provided by the user
   * @param description - the description of how the user utilizes this device
   * @param key - API Key for accessing device data
   */
  public OuraRing(String ID,String description, String key){
    super(ID, description, key);
    metricDescriptions = new HashMap<>();
    // Initialize the ArrayList of Metrics
    initializeMetricInfo();
  }

  /**
   * return the path of the Oura Ring Icon to the View Pages
   * @return - string path of the icon png
   */
  public String getDeviceIcon(){
    return icon;
  }

  /**
   * getter for the device name
   * @return the toString of the DeviceName ENUM
   */
  public String getDeviceName() {
    return name.toString();
  }

  /**
   * Provides the descriptions of all of the metrics provided by Oura
   * Sleep Score, Total Sleep, Sleep Efficiency, Restfulness, REM Sleep, Deep Sleep, Sleep Latency, Timing
   * @return - returns the toString of an Arraylist for easy passing to the LLM
   */
  public String getMetricDescriptions(){
    return this.metricDescriptions.toString();
  }

  /*
  Initialize the Metric Info Array List with specific descriptions of the OUra Ring -> perhaps better done by saving it to a file and converting it -> next iteration
   */
  private void initializeMetricInfo(){
    // Given Latest Information on Oura Ring -> capture and document definition of each metric
    // Look to store this information elsewhere

    // Sleep Score - source: https://support.ouraring.com/hc/en-us/articles/360025445574-Sleep-Score
    metricDescriptions.put("Sleep Score", "Your Sleep Score reflects the quality and quantity of your sleep by analyzing key factors like sleep stages, restfulness, and timing. Learn what affects your score and how you can work toward better sleep");

    //Contributors
    // Total Sleep
    metricDescriptions.put("Total Sleep", "Total sleep reflects the amount of time spent in light, REM, and deep sleep. All your sleep is taken into account, including naps.");
    // Sleep Efficiency
    metricDescriptions.put("Sleep Efficiency", "Sleep efficiency reflects the percentage of time spent asleep compared to the time spent awake while in bed. It takes into account all sleep, including naps.");
    // Restfulness
    metricDescriptions.put("Restfulness", "Restfulness tracks your wake-ups, excessive movement, and how often you get out of bed during sleep. It takes into account all your sleep, including naps.");
    // REM Sleep
    metricDescriptions.put("REM Sleep", "REM (rapid eye movement) sleep is associated with dreaming, memory consolidation, and creativity. It plays an important role in re-energizing both your mind and body, and includes all your sleep, including naps.");
    // Deep Sleep
    metricDescriptions.put("Deep Sleep", "Deep sleep is the most restorative and rejuvenating sleep stage. It includes all your sleep, including naps");
    // Sleep Latency
    metricDescriptions.put("Sleep Latency", "Sleep latency measures how long it takes you to fall asleep at night. It’s only tracked for your longest sleep period.");
    // Timing
    metricDescriptions.put("Timing", "The Timing contributor takes into account all your sleep, including naps. Optimally, the midpoint of your sleep should fall between midnight and 3am, though this can vary depending on whether you're a morning or evening type. If you feel tired during the day, the best time to nap is usually in the early afternoon.");

  }

}
