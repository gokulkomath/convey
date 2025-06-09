from typing import Any, Dict, List, Text
import os
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
import requests
import wikipediaapi
import subprocess


class ActionOpenApp(Action):
    def name(self) -> Text:
        return "action_open_app"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
      
        app = tracker.get_slot("app")

        if app:

            paths = os.environ.get("PATH", "").split(os.pathsep)
            found = False
            full_path=""
            for path in paths:
                full_path = os.path.join(path, app)
                print(full_path)
                if os.path.isfile(full_path):

                    found = True
                    break





            if (found):
                try:
                        pid = os.fork()
                        if pid == 0:
                             # Child process
                            os.execvp(full_path, [full_path])
                            return []
                        else:
                             dispatcher.utter_message(text=f"Opening {app}...")

              
                except Exception as e:
            
                        dispatcher.utter_message(text=f"⚠️ Exception: {str(e)}")

            else:
                dispatcher.utter_message(text=f"I don't think {app} is available in your system.")



        else:
            dispatcher.utter_message(text="I didn't catch the command to run.") 

        return []


class ActionTellJoke(Action):
    def name(self) -> Text:
        return "action_tell_joke"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:


        URL = "https://v2.jokeapi.dev/joke/Any"

        r = requests.get(url=URL)

        data = r.json()

        if(data["error"]):
	        dispatcher.utter_message(data["message"])


        if(data["type"]=="twopart"):
	        dispatcher.utter_message(data["setup"])
	        dispatcher.utter_message(data["delivery"])
            

        else:
	        dispatcher.utter_message(data["joke"])
        
        return []



class ActionWatchYoutube(Action):
    def name(self) -> Text:
        return "action_watch_youtube"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:


        try:
            pid = os.fork()
            if pid == 0:
             # Child process
                os.execvp("/usr/bin/brave", ["/usr/bin/brave","--new-window","https://www.youtube.com"])
               
                return []
            else:
                 dispatcher.utter_message(text=f"Opening Youtube...")
              
        except Exception as e:
            
            dispatcher.utter_message(text=f"⚠️ Exception: {str(e)}")



class ActionSearchTerm(Action):
    def name(self) -> Text:
        return "action_search_term"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:



        search_term = tracker.get_slot("search_term")

        if (search_term):
            try:

               
                wiki_wiki = wikipediaapi.Wikipedia('Convey (merlin@example.com)', 'en')
                page_py = wiki_wiki.page(search_term)

                dispatcher.utter_message(page_py.title)
                # Page - Title: Python (programming language)

                summary = page_py.summary[0:1000]

                first_dot = summary.find('.')
                if first_dot == -1:
                    dispatcher.utter_message(summary)
                    return []

                second_dot = summary.find('.', first_dot + 1)
                if second_dot == -1:
                    dispatcher.utter_message(summary[:first_dot + 1])  # Only one dot found
                    return []

                dispatcher.utter_message(summary[:second_dot + 1])  # Include second dot




            except Exception as e:
                dispatcher.utter_message(f"⚠️ Exception: {str(e)}")

        else:
            dispatcher.utter_message("Sorry, I didn't understand what you said")              


class ActionPlaySong(Action):
    def name(self) -> Text:
        return "action_play"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        song = tracker.get_slot("song")

        if not song:
            dispatcher.utter_message(text="I didn't catch the song to play.")
            return []

        try:
            # Get YouTube audio URL using yt-dlp
            yt_url = subprocess.check_output(
                ['yt-dlp', '-g', '-f', 'bestaudio', f'ytsearch1:{song}'],
                text=True
            ).strip()

            # Start VLC in a background process (non-blocking)
            process = subprocess.Popen(['cvlc', '--no-video', yt_url])

            # Get the child process PID
            child_pid = process.pid

            dispatcher.utter_message(text=f"🎵 Playing {song}... (PID: {child_pid})")

            # Set the child_pid slot
            return [SlotSet("child_pid", child_pid)]

        except Exception as e:
            dispatcher.utter_message(text=f"⚠️ Error: {str(e)}")
            return []


class ActionStopSong(Action):
    def name(self) -> Text:
        return "action_stop_song"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        pid = tracker.get_slot("child_pid")

        if pid:
            try:
                os.kill(int(pid), signal.SIGTERM)  # Graceful terminate
                dispatcher.utter_message(text=f"Stopped the song (PID: {pid}).")
                return [SlotSet("child_pid", None)]
            except ProcessLookupError:
                dispatcher.utter_message(text=f"No process found with PID {pid}.")
                return [SlotSet("child_pid", None)]
            except Exception as e:
                dispatcher.utter_message(text=f"Error stopping the song: {str(e)}")
        else:
            dispatcher.utter_message(text="No song is currently playing.")

        return []


