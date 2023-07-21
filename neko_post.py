from typing import Self
from os import listdir, fsdecode, mkdir, remove
from requests import post, get, Response

class NekoPoster:
    """
    When the main class is being initialize __init__(...) start the index from 0
    Returns: None
    """
    def __init__(
            self: Self, instance: str,
            token: str, log_task: bool = True,
            image_dir: str = "images"
    ) -> None:
        self.index = 0
        self.instance = instance
        self.statues_route = "api/v1/statuses"
        self.media_route = "api/v1/media"
        self.token = {
            "Authorization": f"Bearer {token}"
        }
        self.image_dir = image_dir
        self.log_task = log_task
        self.status_message = ""
        self.nekos_best = "https://nekos.best/api/v2"
        self.neko_random = "https://api.nekosapi.com/v2/images/random"
        self.endpoints = [
            "highfive", "happy", "sleep", "handhold", "laugh", "bite",
            "poke", "tickle", "kiss", "wave", "thumbsup", "state", "cuddle",
            "baka", "blush", "nom", "think", "pout", "faceplam", "wink", "shoot",
            "smug", "nope", "cry", "pat", "nod", "punch", "dance", "feed", "shrug",
            "bored", "kick", "hug", "yeet", "slap", "neko", "husbando", "kitsune",
            "waifu", "random"
        ]

    """Function: __log_task__(...)
    Print log messages whereever needed
    Returns: Nones
    """
    def __log_task__(self: Self, msg: str) -> None:
        if self.log_task:
            print(msg)

    """Function: __endpoint__(...)
    Choose an endpoint
    Returns: str
    """
    def __endpoint__(self: Self, endpoint: str) -> str:
        if endpoint == "random":
            return self.neko_random

        return f"{self.nekos_best}/{endpoint}"
    
    """Function: __create_img_dir__(...)
    Create the images directory, if it doesn't exist
    Returns: None
    """
    def create_img_dir(self: Self) -> None:
        try:
            mkdir("images")
        except Exception:
            pass

    """Function: __read_file__(...)
    Read a file contents and return the buffer to the caller
    Returns: bytes
    """
    def __read_file__(self: Self, file: str) -> bytes:
        try:
            with open(file, "rb") as r:
                if r.readable():
                    return r.read()
        except BlockingIOError as e:
            self.__log_task__(
                f"File write error, I/O blocking has been detected\nDebug: {e}"
            )

    """Function: __write_file__(...)
    Write all passed contents to a specific file
    Returns: None
    """
    def __write_file__(self: Self, file: str, data: bytes) -> str:
        try:
            with open(file, "wb") as w:
                if w.writable():
                    w.write(data)
        except BlockingIOError as e:
            self.__log_task__(
                f"File write error, I/O blocking has been detected\nDebug: {e}"
            )

        return file

    """Function: __req_post__(...)
    Create a post request to the API with appropriate header and body
    Returns: Response 
    """
    def __req_post__(
            self: Self, url: str, data: any,
            files: any, headers: dict[str, any]
    ) -> Response:
        req = post(url=url,
                   data=data,
                   files=files,
                   headers=headers
            )
        if req.status_code != 200:
            self.__log_task__(f"Request error, status code: {req.status_code}")

        return req

    """Function: __req_get__(...)
    Create a get request to the API with appropriate header and body
    Returns: Response
    """
    def __req_get__(
            self: Self, url: str,
    ) -> Response:
        headers = { "Accept": "application/vnd.api+json" }
        req = get(url=url, headers=headers)
        if req.status_code != 200:
            self.__log_task__(f"Request error, status code: {req.status_code}")

        return req

    """Function: __make_neko_call__(...)
    Create get requests and sort out the image
    Returns: str
    """
    def __make_neko_call__(self: Self, ntype: str) -> str:
        self.__log_task__("Downloading image...")
        if ntype not in self.endpoints:
            raise BaseException(f"Unknown endpoint: {ntype}")

        if ntype == "random":
            try:
                req = self.__req_get__(self.__endpoint__("random"))
                name = req.json()["data"]["id"]
                url = req.json()["data"]["attributes"]["file"]
                req = self.__req_get__(url)
                return self.__write_file__(f"{self.image_dir}/{name}.webp", req.content)
            except Exception as e:
                self.__log_task__(f"An exception occurred.\nDebug: {e}")
                pass

        try:
            req = self.__req_get__(self.__endpoint__(ntype))
            url = req.json()["results"][0]["url"]
            name = url.rpartition(f"{ntype}/")[2]
            req = self.__req_get__(url)

            self.__log_task__(f"Download was successfull, status code: {req.status_code}")
            return self.__write_file__(f"{self.image_dir}/{name}", req.content)
        except Exception as e:
            self.__log_task__(f"An exception occurred.\nDebug: {e}")
            pass

    """Function: post_neko(...)
    Post the neko on the instance with public visibility
    Returns: None
    """
    def post_neko(self: Self, wneko: str, visibility: str = "public") -> None:
        try:
            neko = self.__make_neko_call__(wneko)
            bin = self.__read_file__(neko)
            neko_name = neko.split("/")[1]
            self.__log_task__(f"Posting image...")
            files = { "file": (neko_name, bin, "application/octet-stream") }
            data = { 'description': neko_name }
            req = self.__req_post__(
                url=f"{self.instance}/{self.media_route}",
                data=data, files=files,
                headers=self.token
            )
            data = { 
                "status": self.status_message,
                "visibility": visibility,
                "media_ids[]": req.json()["id"]
            }
            req = self.__req_post__(
                url=f"{self.instance}/{self.statues_route}",
                data=data, files=None, headers=self.token
            )
            self.__log_task__(f"Post was successful, status code: {req.status_code}")
        except Exception as e:
            self.__log_task__(f"An exception occurred.\nDebug: {e}")
            pass

    """Function: clean_cache(...)
    Remove all images if images folder has more than 10 images.
    Returns: None
    """
    def clean_cache(self: Self) -> None:
        self.__log_task__(f"Cache index: {self.index}")
        if self.index > 10:
            self.index = 0
            for f in listdir(self.image_dir):
                name = fsdecode(f)
                fmt = f"{self.image_dir}/{name}"
                try:
                    remove(fmt)
                    self.__log_task__(f"Removed image {name}")
                except IOError as e:
                    self.__log_task__(
                        f"Error: Failed to delete file {fmt}\nDebug: {e}"
                    )
        else:
            self.index += 1

