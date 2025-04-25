package ENUMS;

/**
 * States ENUM for the Home Page
 */
public enum HomePageStates {
  /**
   * CHAT state indicates that the Home Page is in its prinary chat state - ready for the user to input question into text field
   */
  CHAT,
  /**
   * state indicates the main page is showing the user's device list
   */
  DEVICE_LIST,
  /**
   * state indicates the main page is showing the user's profile
   */
  USER_PROFILE,
  /**
   * state indicates the main page is showing the device detail page for a single device
   */
  DEVICE_DETAILS
}
