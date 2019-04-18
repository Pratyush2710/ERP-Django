package App.java;

import javafx.application.Application;
import javafx.application.Platform;
import javafx.concurrent.Task;
import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.control.Alert;
import javafx.scene.control.ButtonType;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;
import javafx.stage.Stage;

import java.io.*;
import java.net.ServerSocket;
import java.net.Socket;
import java.nio.file.Paths;
import java.util.List;

public class Main extends Application {

    public static Stage stage;
    public static String name = "Abhay";
    public static String email = "jainsomya972@gmail.com";
    public static String profileImage;
    public static List<File> fileList;
    public static String sendType = "files";// can be files or folder
    public static DiscoveryClient discoveryClient;

    @Override
    public void start(Stage primaryStage) throws Exception{
        File userFile = new File(Paths.get("config.txt").toString());
        BufferedReader reader = null;
        Parent root;
        if(userFile.exists()) {
            reader = new BufferedReader(new FileReader(userFile));
            name = reader.readLine();
            email = reader.readLine();
            profileImage = reader.readLine();
            System.out.println(getClass().getResource("/App/fxml/main.fxml"));
            root = FXMLLoader.load(getClass().getResource("/App/fxml/main.fxml"));
        }
        else
            root = FXMLLoader.load(getClass().getResource("/App/fxml/new_user_dialog.fxml"));

        stage = primaryStage;
        primaryStage.setTitle("Hello World");
        primaryStage.setScene(new Scene(root, 600, 400));
        primaryStage.show();
        discoveryClient = new DiscoveryClient(6700,name);
        new Thread(discoveryClient).start();
    }

    public static void main(String[] args) {
        launch(args);
    }
}
