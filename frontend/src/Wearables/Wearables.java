package Wearables;

/**
 * Interface for all Wearable Devices
 */
// Design RUle #2: Use of interfaces
public interface Wearables {
  // Interface for defining wearable sub-classes
  // sub-classes will include: Apple Watch, Oura Ring, Fitbit, etc.

  /**
   * getter for the DeviceName - either OURARING, AppleWatch (class not yet supported)
   * @return toString of the DeviceName ENUM
   */
  String getDeviceName();


  /**
   * getter for the device ID - this is a unique ID provided to the device upon purchase
   * crucial for measuring equality between devices
   * @return device ID
   */
  String getDeviceID();

  /**
   * setter for the device ID
   * will be called in the "New Device" form - not yet build
   * @param ID - the passed in ID from the user
   */
  void setDeviceID(String ID);

  /**
   * getter for the Device Description
   * should be specified as a constant for developers
   * will contain a 1-2 sentence description of the device and how the user primarily uses it
   * @return the description of the device
   */
  String getDeviceDescription();

  /**
   * Setter for the Device description as noted above
   * this setter will be used primarily for editing an existing instance
   * @param description parameter for describing how the user utilizes this device
   */
  void setDeviceDescription(String description);

  /**
   * Getter for the device ICON to show in the device list page and related pages
   * This should be specified and defined as a constant for the developer in the sub-class level
   * Must be GIF, JPEG, or PNG per <a href="https://docs.oracle.com/javase/8/docs/api/javax/swing/ImageIcon.html">...</a>
   * @return the png file path
   */
  String getDeviceIcon();


  /**
   * getter for the API_KEY
   * In order for LLM to get access to the Wearable device data via the company's API
   * a unique API key needs to be allocated to the user and device
   * this should be passed by the user
   * @return the API Key for a specific device instance
   */
  String getAPIKey();

  /**
   * setter for the APIKEY
   * will be useful for the "Edit Wearable Device Information" once available
   * @param key - the new API Key that will replace the older one
   */
  void setAPIKey(String key);

  /**
   * A description of all the metrics from the device
   * this is critical because each device/company has a unique list of sensor data that is offered
   * by passing in the metric descriptions - the LLM will have better context on hwo to respond to certain questions
   * @return - description of metrics in the developer defined formatting
   */
  String getMetricDescriptions();

}
