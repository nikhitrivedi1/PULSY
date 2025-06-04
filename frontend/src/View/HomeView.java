package View;

import ENUMS.HomePageStates;
import Wearables.Wearables;
import ENUMS.SPEAKER;


import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Dimension;
import java.awt.FlowLayout;
import java.awt.Font;
import java.awt.GridLayout;
import java.awt.Image;
import java.awt.event.ActionListener;
import java.util.ArrayList;
import javax.swing.BorderFactory;
import javax.swing.BoxLayout;
import javax.swing.ImageIcon;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JSplitPane;
import javax.swing.JTextField;
import javax.swing.SwingConstants;

/**
 * View of the Main Home Page
 * called post successful authentication
 */
// Design Rule 13: Seperation of Classes -> this is used only for HomeView
  // Design Rule 19: Reusable components
public class HomeView {

  // Elements
  private JPanel totalPanel;
  private JSplitPane jSplitPane;

  private JPanel chatPanel;
  private JButton inputButton;
  private JTextField textField;
  private JButton homeButton;
  private JButton userProfileButton;
  private JButton deviceButton;
  private JButton deviceInfoButton;
  private final JFrame mainFrame;
  private HomePageStates currentState;
  private int numberMessages;


  // Navigation Elements
  /**
   * HomeView constructor
   * initializes the mainFrame display and configures size + parameters
   */
  public HomeView(){
    mainFrame = new JFrame();
    mainFrame.setSize(800,500);
    mainFrame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
    numberMessages = 0;
  }

  /**
   * adds the totalPanel will the ALL view elements required
   */
  public void createHomeView(){
    totalPanel = new JPanel(new BorderLayout());
    totalPanel.setPreferredSize(new Dimension(800,500));

    // Create Split Panel - Left and Right in 20-80 split
    jSplitPane = new JSplitPane(JSplitPane.HORIZONTAL_SPLIT);
    jSplitPane.setResizeWeight(.2);

    // Create Tool bar for Left Component
    JPanel headerPan = createToolBar();
    headerPan.setBorder(BorderFactory.createMatteBorder(0, 0, 0, 2, Color.GRAY));

    // Create Chat Interface for Right Component
    JPanel chatPan = createChatInterface();

    // Set the Split Panel Components
    jSplitPane.setLeftComponent(headerPan);
    jSplitPane.setRightComponent(chatPan);

    // Add to Outer Most Panel
    totalPanel.add(jSplitPane, BorderLayout.CENTER);

    // set state
    currentState = HomePageStates.CHAT;

    mainFrame.setContentPane(totalPanel);
    mainFrame.pack();
    mainFrame.setVisible(true);
  }

  /**
   * getter for the user text field - this is the query that will be passed to the LLM
   * @return user text input
   */
  public String getUserText(){
    String storedText = textField.getText();
    textField.setText("");
    return storedText;
  }

  // Public Methods for Implementation of Updating UI

  /**
   * adds a specific message to the main chat window using the SPEAKER type to determine the display location
   * @param message - message to be added to the display
   * @param speaker - who the message is coming from - AI or USER
   */
  public void addMessageToChat(String message, SPEAKER speaker){
    JPanel msg = createMessageHistoryPanel(message, speaker);
    msg.setMaximumSize(new Dimension(Integer.MAX_VALUE, msg.getPreferredSize().height));
    numberMessages++;
    chatPanel.add(msg);
    chatPanel.revalidate();
    chatPanel.repaint();
  }

  // Action Listeners for the Controller

  /**
   * action listener for the input button -> send message to LLM
   * @param actionListener - action listener of input button
   */
  public void addInputButtonListener(ActionListener actionListener){
    inputButton.addActionListener(actionListener);
  }

  /**
   * getter for the input button
   * utilized for future enhancements +  for testing purposes
   * Design Rule #18
   * @return - the inputbutton Jbutton
   */
  public JButton getInputButton(){
    return inputButton;
  }

  /**
   * getter for the user text field
   * utilized for future enhancements +  for testing purposes
   * Design Rule #18
   * @return the Text Field - query from the User to the LLM
   */
  public JTextField getTextField(){
    return textField;
  }

  /**
   * getter for the number of messages in the chat history panel
   * @return the number of messages from the user and AI in the chat history
   */
  public int getNumberMessages(){
    return numberMessages;
  }

  /**
   * action listener for the home button -> go back to the home page
   * @param actionListener - action listener of Home button
   */
  public void addHomeButtonListener(ActionListener actionListener){
    homeButton.addActionListener(actionListener);
  }

  /**
   * getter for the Home Button in the navigation panel
   * utilized for future enhancements +  for testing purposes
   * design Rule #18
   * @return the JButton for the Home Navigation Button
   */
  public JButton getHomeButton(){
    return homeButton;
  }

  /**
   * action listener for the device button -> goes to device list page
   * @param actionListener - action listener of device button
   */
  public void addDeviceButtonListener(ActionListener actionListener){
    deviceButton.addActionListener(actionListener);
  }

  /**
   * getter for the Device Navigation button
   * utilized for future enhancements +  for testing purposes
   * Design Rule #18
   * @return instance of the JButton for clicking the device button
   */
  public JButton getDeviceButton(){
    return deviceButton;
  }

  /**
   * getter for the device info button - not yet inmplemented
   * @return the button instance for the device info button
   */
  public JButton getDeviceInfoButton(){
    return deviceInfoButton;
  }


  /**
   *action listener for the user profile button -> user profile page
   * @param actionListener - action listener for the user profile button (IN PROCESS)
   */
  public void addUserProfileButton(ActionListener actionListener){
    userProfileButton.addActionListener(actionListener);
  }

  /**
   * getter for the userProfileButton -> primarily used for testing purposes (not yet implemented)
   * @return JButton instance of the userprofile button
   */
  public JButton getUserProfileButton(){
    return userProfileButton;
  }

  /**
   * getter for the state of the Home Page
   * utilized for implementing different variations of a similar UI on the same Frame
   * Design Rule #18, #17, #22, #6 (ENUMS)
   * @return the Home Page State depending on the sequence of user actions
   */
  public HomePageStates getState(){
    return currentState;
  }

  // Private Internal Methods
  // For the Left Portion of the Home Page - Navigation Tool Bar
  private JPanel createToolBar(){
    // create new panel with the header and list of buttons
    JPanel navPanel = new JPanel();
    navPanel.setLayout(new BorderLayout());

    // add the header element first
    navPanel.add(createHeader(), BorderLayout.NORTH);
    // Create a ToolBar
    JPanel buttonPanel = new JPanel();
    buttonPanel.setLayout(new GridLayout(0,1));

    // add icon here prior to the start of the buttons
    // add in Icon
    ImageIcon pulseyIcon = new ImageIcon("src/assets/Pulsey_Icon.png");
    Image scaledImage = pulseyIcon.getImage().getScaledInstance(100, 100, Image.SCALE_SMOOTH);
    ImageIcon resizedIcon = new ImageIcon(scaledImage);
    JLabel pulseyLabel = new JLabel(resizedIcon);

    buttonPanel.add(pulseyLabel);

    homeButton = new JButton("Home");
    buttonPanel.add(homeButton);

    userProfileButton = new JButton("User Profile");
    buttonPanel.add(userProfileButton);

    deviceButton = new JButton("Devices");
    buttonPanel.add(deviceButton);

    navPanel.add(buttonPanel, BorderLayout.CENTER);

    return navPanel;
  }
  private JPanel createHeader(){
    JPanel headerPanel = new JPanel();

    // create a new panel to group the label and icon
    JLabel headerLabel = new JLabel("Pulsy");
    headerLabel.setForeground(Color.WHITE);

    headerPanel.add(headerLabel);
    headerPanel.setBackground(Color.DARK_GRAY);
    return headerPanel;
  }

  // For the Right Portion of the Home Page - Chat Features
  private JPanel createChatInterface(){
    // Left Panel will be the chat interface
    JPanel chatContainer = new JPanel(new BorderLayout());

    // Text Field Input
    // within this panel -> top will be used for chat and botton for text
    JPanel textAreaPanel = new JPanel(new BorderLayout());
    textAreaPanel.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10)); // padding

    textField = new JTextField();
    textField.setPreferredSize(new Dimension(0, 30)); // reasonable height
    textField.setFont(new Font("SansSerif", Font.PLAIN, 14));

    inputButton = new JButton("➤"); // or use an icon later
    inputButton.setPreferredSize(new Dimension(60, 30));
    inputButton.setFocusPainted(false);

// Wrap button in a panel to right-align cleanly (optional)
    JPanel buttonWrapper = new JPanel(new BorderLayout());
    buttonWrapper.add(inputButton, BorderLayout.EAST);
    buttonWrapper.setOpaque(false); // preserve transparent background

// Add to main text input panel
    textAreaPanel.add(textField, BorderLayout.CENTER);
    textAreaPanel.add(buttonWrapper, BorderLayout.EAST);

// Add this input area to the bottom of your chat container
    chatContainer.add(textAreaPanel, BorderLayout.SOUTH);

//    // Chat Area - blank upon initialization
    chatPanel = new JPanel();
    chatPanel.setLayout(new BoxLayout(chatPanel, BoxLayout.PAGE_AXIS));
    JScrollPane scrollPane = new JScrollPane(chatPanel);
    scrollPane.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_ALWAYS);

    chatContainer.add(scrollPane);

    return chatContainer;
  }
  private JPanel createMessageHistoryPanel(String label, SPEAKER turn){
    // Outer panel holds the whole message row
    JPanel outerPanel = new JPanel();
    outerPanel.setLayout(new BorderLayout());
    outerPanel.setOpaque(false); // transparent background
    outerPanel.setSize(50,100);


    JPanel bubblePanel = new JPanel();
    bubblePanel.setLayout(new BorderLayout());
    bubblePanel.setBorder(BorderFactory.createEmptyBorder(8, 12, 8, 12)); // padding inside bubble

    // change the color according to turn variable
    if(turn == SPEAKER.AI){
      bubblePanel.setBackground(new Color(230, 230, 250));
    }else{
      bubblePanel.setBackground(new Color(200, 255, 200));
    }

    bubblePanel.setOpaque(true);

    // Label with the message
    String wrappedText = "<html><div style='width: " + 300 + "px;'>" + label + "</div></html>";
    JLabel messageLabel = new JLabel("<html>" + wrappedText + "</html>"); // allow wrapping
    messageLabel.setFont(new Font("SansSerif", Font.PLAIN, 14));

    bubblePanel.add(messageLabel, BorderLayout.CENTER);

    // Wrap the bubble in a wrapper panel for alignment
    JPanel alignWrapper = new JPanel(new FlowLayout(
        turn == SPEAKER.AI ? FlowLayout.LEFT : FlowLayout.RIGHT));
    alignWrapper.setOpaque(false);
    alignWrapper.add(bubblePanel);

    // Final add
    outerPanel.add(alignWrapper, BorderLayout.CENTER);

    return outerPanel;
  }


  // Device Page Specifics

  /**
   * creation of the device page panel when the user selects the device button
   * utilizes same main frame
   * @param devList - the list of devices unique to the user
   */
  public void createDevicePagePanel(ArrayList<Wearables> devList){
    JPanel devPanelContainer = new JPanel(new FlowLayout(FlowLayout.LEFT, 20,20));

    // for now just get the first one - Oura Ring
    JButton deviceBlock = createDeviceBlock(devList.getFirst());
    devPanelContainer.add(deviceBlock);

    // need to a second button to add a new wearable
    JButton addBlock = createAddDeviceBlock();
    devPanelContainer.add(addBlock);

    currentState = HomePageStates.DEVICE_LIST;

    jSplitPane.setRightComponent(devPanelContainer);
    jSplitPane.repaint();
    jSplitPane.revalidate();
  }

  // getter for the DeviceBlock created
  private JButton getDeviceBlock(){
    JButton deviceBlock = new JButton();
    deviceBlock.setLayout(new BorderLayout());
    deviceBlock.setPreferredSize(new Dimension(150, 200));
    deviceBlock.setOpaque(true);
    deviceBlock.setContentAreaFilled(true);
    deviceBlock.setFocusPainted(false);
    deviceBlock.setBorder(BorderFactory.createCompoundBorder(
        BorderFactory.createLineBorder(Color.BLACK, 1),
        BorderFactory.createEmptyBorder(10, 10, 10, 10)
    ));


    deviceBlock.addMouseListener(new java.awt.event.MouseAdapter() {
      @Override
      public void mouseEntered(java.awt.event.MouseEvent evt) {
        deviceBlock.setBackground(Color.WHITE);
      }

      @Override
      public void mouseExited(java.awt.event.MouseEvent evt) {
        deviceBlock.setBackground(Color.LIGHT_GRAY);
      }
    });

    return deviceBlock;
  }
  // creation of the device block
  private JButton createDeviceBlock(Wearables device){

    JButton deviceBlock = getDeviceBlock();

    JLabel deviceName = new JLabel(device.getDeviceName(), SwingConstants.CENTER);

    ImageIcon deviceIcon = new ImageIcon(device.getDeviceIcon());
    Image scaledImage = deviceIcon.getImage().getScaledInstance(100, 100, Image.SCALE_SMOOTH);
    ImageIcon resizedIcon = new ImageIcon(scaledImage);
    JLabel icon = new JLabel(resizedIcon);

    JLabel deviceID = new JLabel("Device ID:" + device.getDeviceID(), SwingConstants.CENTER);
//    JLabel deviceDescription = new JLabel("<html>" + device.getDeviceDescription() + "<html>", SwingConstants.CENTER);

    // Place each element into the block
    deviceBlock.add(deviceName, BorderLayout.NORTH);
    deviceBlock.add(icon, BorderLayout.CENTER);
    deviceBlock.add(deviceID, BorderLayout.SOUTH);

    return deviceBlock;
  }
  // creation of the (+) device block to allow users to add a device of their choosing
  private JButton createAddDeviceBlock(){
    JButton addBlock = getDeviceBlock();

    // Include artwork for a plus symbol
    ImageIcon deviceIcon = new ImageIcon("src/assets/plusSymbol.png");
    Image scaledImage = deviceIcon.getImage().getScaledInstance(100, 100, Image.SCALE_SMOOTH);
    ImageIcon resizedIcon = new ImageIcon(scaledImage);
    JLabel icon = new JLabel(resizedIcon);

    addBlock.add(icon);
    return addBlock;
  }
}
