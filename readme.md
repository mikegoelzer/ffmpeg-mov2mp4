# `ffmpeg` Screen Capture Compressor

Simple script to compress huge macOS `.mov` screen capture videos made with `Cmd`+`Shift`+`5` into smaller `.mp4` files. Useful when video quality is not that important, but size is.

Typically compresses ~200 MB `.mov` videos down to <1 MB with text still easily readable.

## Usage

To run the script, use the following command:

```sh
python3 ffmpeg-mov2mp4.py -i <input_file> -o <output_file> -s <seconds> -t <seconds>
```

Common options:

- `-i` or `--input`: input video file
- `-o` or `--output`: output video file (default is input with `mp4` extension)
- `-s` and `-t`: clips out seconds from the beginning and/or end of the input video
- `c`: bitrate compression; for fast scrolling screen grabs, may make text unreadable (default: none)

For full list of options:

```sh
python3 ffmpeg-mov2mp4.py --help
```

Example:

```sh
python3 ffmpeg-mov2mp4.py -i input.mov -c high -s 2 -t 5
```