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
