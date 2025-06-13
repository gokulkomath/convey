from typing import Any, Dict, List, Text
import os
import subprocess
import requests
import wikipediaapi
import json
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from duckduckgo_search import DDGS
from urllib.parse import urlparse
import re

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
            full_path = ""
            for path in paths:
                full_path = os.path.join(path, app)
                if os.path.isfile(full_path):
                    found = True
                    break

            if found:
                try:
                    pid = os.fork()
                    if pid == 0:
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

        if data["error"]:
            dispatcher.utter_message(data["message"])
        elif data["type"] == "twopart":
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
                os.execvp("/usr/bin/brave", ["/usr/bin/brave", "--new-window", "https://www.youtube.com"])
                return []
            else:
                dispatcher.utter_message(text="Opening Youtube...")
        except Exception as e:
            dispatcher.utter_message(text=f"⚠️ Exception: {str(e)}")

        return []


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

        if search_term:
            try:
                wiki_wiki = wikipediaapi.Wikipedia('Convey (merlin@example.com)', 'en')
                page_py = wiki_wiki.page(search_term)

                dispatcher.utter_message(page_py.title)
                summary = page_py.summary[0:1000]

                first_dot = summary.find('.')
                if first_dot == -1:
                    dispatcher.utter_message(text=f"According to Wikipedia, {summary}")
                    return []

                second_dot = summary.find('.', first_dot + 1)
                if second_dot == -1:
                    dispatcher.utter_message(text=f"According to Wikipedia, {summary[:first_dot + 1]}")
                    return []

                third_dot = summary.find('.', second_dot + 1)
                if third_dot == -1:
                    dispatcher.utter_message(text=f"According to Wikipedia, {summary[:second_dot + 1]}")
                    return []

                dispatcher.utter_message(text=f"According to Wikipedia, {summary[:third_dot + 1]}")
                return []

            except Exception as e:
                dispatcher.utter_message(text=f"⚠️ Exception: {str(e)}")
        else:
            dispatcher.utter_message(text="Sorry, I didn't understand what you said.")

        return []


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
            yt_metadata_json = subprocess.check_output(
                ['yt-dlp', '--dump-json', '-f', 'bestaudio', f'ytsearch1:{song}'],
                text=True
            ).strip()

            video_info = json.loads(yt_metadata_json)
            duration = video_info['duration']
            yt_url = video_info['url']
            song_title = video_info['title']

            if duration > 350:
                dispatcher.utter_message(text="I don't think that is a song.")
                return []

            # Start VLC and announce song
            proc = subprocess.Popen([
                'vlc', '--qt-start-minimized', '--play-and-exit', '--no-video', yt_url
            ])
            dispatcher.utter_message(text=f"What you heard was {song_title}")
            proc.wait()

        except Exception as e:
            dispatcher.utter_message(text=f"⚠️ Error: {str(e)}")

        return []

class ActionInternetSearch(Action):
    def name(self) -> Text:
        return "action_internet_search"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        search_prompt = tracker.latest_message.get("text")
        results = DDGS().text(search_prompt, max_results=1)


        parsed = urlparse(results[0]['href'])
        domain = parsed.netloc

        if domain.startswith('www.'):
            domain = domain[4:]



        body = re.sub(r"\{.*?\}", "", results[0]['body'])
        dispatcher.utter_message(text=f"According to {domain}, {body}")