package View;

import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.GridLayout;
import java.awt.Image;
import java.awt.event.ActionListener;
import javax.swing.ImageIcon;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JPasswordField;
import javax.swing.JSplitPane;
import javax.swing.JTextField;

/**
 * GUI View Class for the Login Page
 */
public class LoginView {
  private JPanel loginPanel;
  private JTextField usernameText;
  private JPasswordField passwordField;
  private JButton loginButton;
  private JPanel mainPanel;
  private final JFrame mainFrame;
  private boolean isClosed;


  /**
   * Login View Constructor - initializes the mainFrame window
   *  - window sized smaller than the HomeFrame
   */
  // other design rules commented above specified method
  // Design Rule #13 - Seperatino of Responsibilities - this only covers LoginView
  // Design Rule #19 - elements of reusable components
  public LoginView(){
    // Create a new Panel which will go into the JFrame
    /*
     Login Prompt:
     Username:
     Password:
     Submit Button
     */
    mainFrame = new JFrame();
    mainFrame.setSize(600,200);
    mainFrame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
    isClosed = false;
  }

  // Login View Methods

  /**
   * shows the Login Screen on the MainFrame
   */
  public void showLoginPanel(){
    // Split into two sides
    JSplitPane jSplitPane = new JSplitPane(JSplitPane.HORIZONTAL_SPLIT);
    jSplitPane.setResizeWeight(.5);

    // Set Right and Left Components
    jSplitPane.setLeftComponent(createUserFormPanel());
    jSplitPane.setRightComponent(createBrandingImage());

    mainFrame.add(jSplitPane);
    mainFrame.repaint();
    mainFrame.revalidate();
    mainFrame.setVisible(true);
  }

  /**
   * Adds listener for the login button for the LoginController to act
   * @param actionListener - action listener specified at controller level
   */
  public void addLoginListener(ActionListener actionListener){
    loginButton.addActionListener(actionListener);
  }


  /**
   * Getter for the username text field
   * used for authentication
   * @return - username
   */
  public String getUsername(){
    return this.usernameText.getText();
  }

  /**
   * setter for the username login field
   * configured for future extension of autofill username +  used for testing
   * @param username - username parameter for the field to be set to
   */
  // Design Rule #17: Plan for future extension
  public void setUsernameText(String username){
    usernameText.setText(username);
  }

  /**
   * Getter for the password field
   * used for authentication
   * @return - password
   */
  public String getPassword(){
    return this.passwordField.getText();
  }


  /**
   * setter for the password field
   * configured for future autofill feature + used primarily for testing
   * @param pass - password parameter that the field needs to be set to
   */
  // Design Rule #17: Plan for future extension
  public void setPasswordField(String pass){
    passwordField.setText(pass);
  }

  /**
   * if authentication fails -> Controller will show invalid login message
   */
  public void showLoginError(){
    // if authenticate fails -> show error message
    loginButton.setText("Invalid Login!");
  }

  /**
   * getter for the Login Button - primarily for testing ease
   * @return - the login button JButton
   */
  public JButton getLoginButton(){
    return loginButton;
  }

  /**
   * closes the mainFrame for Login upon successful Authnetication
   */
  public void close(){
    isClosed = true;
    mainFrame.dispose();
  }

  /**
   * Used to document the state of the LoginView
   * once authentication is successful, LoginView state will be closed
   * @return false if still active - true is closed after successful authentication
   */
  public boolean isClosed(){
    return isClosed;
  }

  // Private Classes Internal
  // Design Rule 3 -> all fields are private and these internal methods are also private
  // Create the user input forms panel - added to the Main Frame
  private JPanel createUserFormPanel(){
    // Main Panel - Layout Border
    mainPanel = new JPanel(new BorderLayout());

    // Create Header
    JPanel headerPanel = new JPanel();
    JLabel headerLabel = new JLabel("Pulsy");
    headerLabel.setBackground(Color.DARK_GRAY);
    headerPanel.add(headerLabel, JPanel.CENTER_ALIGNMENT);
    mainPanel.add(headerPanel, BorderLayout.NORTH);


    // Create Form
    loginPanel = new JPanel(new GridLayout(2,2));
    usernameText = new JTextField();
    passwordField = new JPasswordField();
    loginPanel.add(new JLabel("Username: "));
    loginPanel.add(usernameText);
    loginPanel.add(new JLabel("Password: "));
    loginPanel.add(passwordField);

    mainPanel.add(loginPanel, BorderLayout.CENTER);

    // Create Login Button
    loginButton = new JButton("Login");
    mainPanel.add(loginButton, BorderLayout.SOUTH);

    return mainPanel;
  }
  // initializes panel with Pulsy picture as the right side
  private JPanel createBrandingImage(){
    JPanel brandPanel = new JPanel(new BorderLayout());

    ImageIcon pulseyIcon = new ImageIcon("src/assets/Pulsey_Icon.png");
    Image scaledIcon = pulseyIcon.getImage().getScaledInstance(125, 150, Image.SCALE_SMOOTH);
    ImageIcon scaled = new ImageIcon(scaledIcon);
    JLabel iconLabel = new JLabel(scaled);

    brandPanel.add(iconLabel);
    return brandPanel;
  }

}
