### Nekoposter
A script which sends \*cute\* nekos every hour.

### Example
See it in [test.py](./test.py)
```py
from neko_post import NekoPoster
from time import sleep

def main() -> None:
    nep = NekoPoster(
        instance="https://mastodon.online",
        token="53i2X8l9tei0zJfxXaTzv3Pp-k3jWAXFkfe5GGpjof4"
    )
    nep.create_img_dir()
    while True:
        nep.post_neko(wneko="random")
        nep.clean_cache()
        sleep(3600)

if __name__ == "__main__":
    main()
```

### Notes
1. It uses nekos life API, images may be copyrighted by their respective owners.
2. `random` endpoint includes NSFW images as well.
3. It's not always that instances use Mastodon at the backend. Frontend and backend for Mastodon are separated.
