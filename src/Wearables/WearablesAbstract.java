package Wearables;

import java.util.Objects;

/**
 * Abstract class of Parent Class Wearables
 * contains methods that are shared across the Wearable Sub-classes
 */
// Design Rule 15 - abstract class was created to avoid code duplication
  // Design RUle 21 - override equals and hashCode() methods
public abstract class WearablesAbstract implements Wearables {
  private String ID, description, key;

  /**
   * Wearables Abstract Constructor
   * @param ID - DeviceID passed in by the user
   * @param description - description of how the user utilizes this device
   * @param key - the API key needed for getting device data
   */
  // TODO: Include Error if the API Key is empty -> indicates that we will not be able to access API
  public WearablesAbstract(String ID, String description, String key){
    this.ID = ID;
    this.key = key;
    this.description = description;
  }

  /**
   * getter for the Device ID for GUI elements
   * @return the ID of the Device
   */
  @Override
  public String getDeviceID() {
    return ID;
  }

  /**
   * setter for the device ID - in the case where the user needs to edit an instance
   * @param ID - the passed in ID from the user
   */
  @Override
  public void setDeviceID(String ID) {
    this.ID = ID;
  }

  /**
   * getter for the device description -
   * @return a string on how the user utilizes this device
   */
  @Override
  public String getDeviceDescription(){
    return this.description;
  }

  /**
   * setter for the device description
   * @param description parameter for describing how the user utilizes this device
   */
  @Override
  public void setDeviceDescription(String description) {
    this.description = description;
  }

  /**
   * getter for the API Key - for interfacing with company API
   * @return the API key
   */
  @Override
  public String getAPIKey(){
    return this.key;
  }

  /**
   * Setter for the API Key
   * @param key - the new API Key that will replace the older one
   */
  @Override
  public void setAPIKey(String key) {
    this.key = key;
  }

  /**
   * Unique TOString for the Wearable Class
   * @return summary of the wearable name, description and ID
   */
  @Override
  public String toString(){
    // Format String
    return "Name: " + getDeviceName() + "\n" + "Description: " + getDeviceDescription() + "\n" + "ID: " + getDeviceID() + "\n";
  }

  /**
   * Override of the equals method to compare different wearables
   * @param other - the Object that will be compared to the Wearables instance
   * Comparison done on the deviceID - since this is unique
   * @return true if equals and false if not
   */
  @Override
  public boolean equals(Object other){
    if(this == other){
      return true;
    }

    // check instance
    if(! (other instanceof WearablesAbstract otherDev)){
      return false;
    }

    // cast and check for ID
    return otherDev.getDeviceID().equals(this.getDeviceID());
  }

  /**
   * Override hashCode for the wearables subclasses
   * @return hash index given ID and device name
   */
  @Override
  public int hashCode(){
    return Objects.hash(this.ID, getDeviceName());
  }
}
