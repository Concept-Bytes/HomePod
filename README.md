# Home Pod Voice Assistant

The Home Pod is an LLM voice assistant that runs on a raspberry pi. This applictaion has a display and user interface with apps for weather, sports, spotify, and more.

## Prerequisites

Before you begin, ensure you have the following:
- A Raspberry Pi set up with internet access.
- An OpenAI API key, Assistant ID, and Thread ID. You can obtain these from your OpenAI account on the [OpenAI Platform](https://platform.openai.com/assistants).

## Installation

1. **Clone the Repository**

   Open a terminal on your Raspberry Pi and run the following command to clone the repository:

   ```git clone https://github.com/Concept-Bytes/HomePod.git```

   Navigate into the project directory:

2. **Install Dependencies**

    Install the required Python packages:

3. **Configuration**

    Open `sample.env` in a text editor of your choice. Fill in your OpenAI API key, Assistant ID, and Thread ID in the designated spots. This information is critical for the AI functionality of the project and can be         obtained from your OpenAI account.

   Rename this to just .env
    
    ```python
    # Example placeholder in assist.py
    API_KEY = "your_openai_api_key_here"
   ASSISTANT_ID = "your_assistant_id_here"
   THREAD_ID = "your_thread_id_here"

    
## Running the Application

After completing the setup and configuration, run the application with:

```python homescreen.py```

This script will run the user interface in window mode to run this full screen run:

```python main_pod.py```


## Contributing
Contributions to the Home Pod are welcome! Please feel free to fork the repository, make your changes, and submit a pull request.

## License
This project is licensed under the MIT License - see the LICENSE file in the repository for details.
# HomePod
