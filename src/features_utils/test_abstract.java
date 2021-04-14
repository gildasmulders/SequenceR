public class Main {
    // Static method
    static void myStaticMethod() {
    }

    // Public method
    public void myPublicMethod() {
    }

    // Main method
    public static void main(String[] args) {
        Main.myStaticMethod();// Call the static method

        // myPublicMethod(); This would compile an error
        Main myObj = new Main();// Create an object of Main

        // ONLY FOR TOKENIZATION, BUGGY LINE BELOW
        myObje.myPublicMethod();// Call the public method on the object

    }
}
