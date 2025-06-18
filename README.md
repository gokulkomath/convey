# Convey

Convey is an experimental voice-controlled desktop assistant, designed to streamline everyday interactions on your Linux system. While still under active development, it currently offers a workable set of features for controlling music, launching applications, and retrieving informatio
## 🚀 Features

Convey currently supports the following functionalities:

* **Music Playback:** Play music via voice commands (requires `yt-dlp` for fetching audio).
* **Application Launch:** Open various applications installed on your system.
* **Open YouTube:** Directly open YouTube in the browser.
* **Wikipedia Search:** Search and retrieve information directly from Wikipedia.
* **Internet Search & Q&A:** Answer questions and fetch information using web search capabilities.

## 💻 System Requirements & Compatibility

This project has been primarily **built for and tested on Arch Linux**.

Convey is configured to use **Brave Browser** for web-related tasks (like opening YouTube or performing internet searches). If you use a different default browser or Brave is not installed, you may need to modify the relevant code in the project for web-related functions to work as expected.
Make sure to set up a Rasa Developer API key, which can be obtained from the Rasa Pro website.

### Dependencies

To ensure all functionalities work, please install the following system-level dependencies:

* **`cava`**: For audio visualization (required for specific visual feedback related to music).
    ```bash
    # On Arch Linux:
    sudo pacman -S cava
    ```
* **`yt-dlp`**: For downloading and playing audio from various sources (e.g., YouTube).
    ```bash
    # On Arch Linux:
    sudo pacman -S yt-dlp
    # Or via pip:
    # pip install yt-dlp
    ```
 

## 🚧 Current Status & Future Work

Convey is a work in progress. While the core features mentioned above are functional and demonstrate the bot's capabilities, there's more work needed to refine its performance, expand its feature set, and improve robustness.


I welcome contributions and feedback to help make Convey a more powerful and versatile assistant!

## ⚙️ Setup and Usage



1.  **Clone the repository:**
    ```bash
    git clone https://github.com/gokulkomath/convey.git
    cd convey
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```
3.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt # Assuming you have a requirements.txt
    # Or, if not, list individual packages like:
    # pip install rasa wikipedia requests pydub playsound ... (add your actual dependencies)
    ```
4.  **Run the bot:**
    ```bash
     rasa run actions 
     rasa shell
    ```


## 🤝 Contributing

Contributions are welcome! If you'd like to contribute, please fork the repository and open a pull request with your changes. For major changes, please open an issue first to discuss what you would like to change.
