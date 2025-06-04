package ENUMS;

/**
 * representation of the available devices on the application
 * will be expanded once functionalities are added
 */
public enum DeviceName {
  /**
   * represnts the Apple Watch device - overrides to String to Apple Watch for the GUI
   */
  APPLEWATCH {
    @Override
    public String toString(){
      return "Apple Watch";
    }
  },
  /**
   * represents the Oura Ring device - overrides toString to Oura Ring for the GUI
   */
  OURARING {
    @Override
    public String toString(){
      return "Oura Ring";
    }
  }
}
