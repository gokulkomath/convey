import subprocess
import json
import re

def get_video_duration_subprocess(url, format_string=False):
    """
    Fetches the duration of a video from a given URL using yt-dlp via subprocess.

    Args:
        url (str): The URL of the video.
        format_string (bool): If True, returns duration as HH:MM:SS string.
                              If False, returns duration as integer seconds.

    Returns:
        Union[int, str, None]: The duration, or None if not found/error.
                               Returns int if format_string is False,
                               str if format_string is True.
    """
    try:
        if format_string:
            # Use --print "%(duration_string)s" for formatted output
            cmd = ['yt-dlp', '--print', '%(duration_string)s', url]
            
            # Execute the command
            result = subprocess.check_output(cmd, text=True, stderr=subprocess.PIPE)
            duration = result.strip()
            
            # Basic validation for common format (e.g., 03:28, 1:05:10)
            if re.fullmatch(r'\d+:\d{2}(:\d{2})?', duration):
                return duration
            else:
                print(f"Warning: Unexpected duration string format for {url}: {duration}")
                return None

        else:
            # Use --print "%(duration)s" for duration in seconds
            cmd = ['yt-dlp', '--print', '%(duration)s', url]
            
            # Execute the command
            result = subprocess.check_output(cmd, text=True, stderr=subprocess.PIPE)
            duration_str = result.strip()
            
            # Convert to integer
            try:
                duration = int(duration_str)
                return duration
            except ValueError:
                print(f"Error: Could not convert duration '{duration_str}' to integer for {url}")
                return None

    except subprocess.CalledProcessError as e:
        print(f"Error fetching video info for {url}:")
        print(f"Command: {' '.join(e.cmd)}")
        print(f"Return Code: {e.returncode}")
        print(f"Stdout: {e.stdout.strip()}")
        print(f"Stderr: {e.stderr.strip()}")
        return None
    except FileNotFoundError:
        print("Error: 'yt-dlp' command not found. Make sure yt-dlp is installed and in your system's PATH.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def get_video_duration_json_subprocess(url):
    """
    Fetches video duration by parsing yt-dlp's --dump-json output.
    This method is more robust for getting various metadata.

    Args:
        url (str): The URL of the video.

    Returns:
        Union[int, None]: The duration in seconds, or None if not found/error.
    """
    try:
        cmd = ['yt-dlp', '--dump-json', url]
        
        # Execute the command and capture output
        result = subprocess.check_output(cmd, text=True, stderr=subprocess.PIPE)
        
        # Parse the JSON output
        info_dict = json.loads(result)
        
        duration = info_dict.get('duration')
        
        if duration is not None:
            return int(duration)
        else:
            print(f"Could not find 'duration' in JSON for {url}")
            return None

    except subprocess.CalledProcessError as e:
        print(f"Error fetching video info for {url}:")
        print(f"Command: {' '.join(e.cmd)}")
        print(f"Return Code: {e.returncode}")
        print(f"Stdout: {e.stdout.strip()}")
        print(f"Stderr: {e.stderr.strip()}")
        return None
    except FileNotFoundError:
        print("Error: 'yt-dlp' command not found. Make sure yt-dlp is installed and in your system's PATH.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not parse JSON output from yt-dlp for {url}")
        print(f"Raw output: {result}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

