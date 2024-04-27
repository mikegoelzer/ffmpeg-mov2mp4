#!/usr/bin/env python3

import argparse
import shutil
import subprocess
import sys

COLOR_GREEN = "\033[92m"
COLOR_NORMAL = "\033[0m"

def get_video_duration(input_file):
    """Returns the duration of a video in seconds."""
    try:
        # Construct the command to get the video duration using ffprobe
        command = [
            'ffprobe',
            '-v', 'error',  # hide all warnings and errors
            '-show_entries', 'format=duration',  # show only the duration entry from the format section
            '-of', 'default=noprint_wrappers=1:nokey=1',  # output formatting options
            input_file  # the video file to probe
        ]
        
        # Execute the command and capture the output
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Convert the output to a float representing the duration in seconds
        duration = float(result.stdout.strip())
        return duration
    
    except Exception as e:
        print(f"Error getting video duration: {e}")
        return None

def compress_video(input_file, output_file, bitrate_compression_level, trim_start=0, trim_end=0):
    """Compresses a video file into a smaller video file"""

    command = [
        'ffmpeg', 
        '-y',                      # overwrite output file without asking
        '-i', input_file,          # input file
        '-c:a', 'aac',             # audio codec
        '-c:v', 'libx264',         # x264 video codec
        '-pix_fmt', 'yuv420p',     # pixel format
        '-vf', 'scale=-1:720',     # scale video to 720p, retaining aspect ratio
        # '-b:a', '128k'           # adjust audio bitrate (errors if audio is not present)
        '-movflags', '+faststart'  # move metadata to beginning of file
    ]
    
    # Extra arg to adjust bitrate based on compression level requested
    bitrate = {
        1: '1000k',
        2: '500k',
        3: '250k'
    }.get(bitrate_compression_level, None)
    if bitrate:
        command.extend(['-b:v', bitrate])

    # Trimming video based on trim_start and trim_end
    if trim_start > 0 or trim_end > 0:
        video_duration = get_video_duration(input_file)
        if video_duration is None:
            print("warning: cannot get video duration; trimming skipped")
        else:
            trim_filter = f"trim=start={trim_start}:"
            if trim_end > 0:
                trim_filter += f"end={int(video_duration-trim_end)}"
            # Append trim filter to existing '-vf' argument
            vf_index = command.index('-vf') + 1
            command[vf_index] = trim_filter + ',setpts=PTS-STARTPTS,' + command[vf_index]
            
            # squelches an error when seconds are trimmed from end by defaulting to 25fps
            if trim_end > 0:
                command.extend(['-r', '25'])

    # append output file
    command.append(output_file)

    # print the command in bright green and execute it
    print("Command: " + COLOR_GREEN + " ".join(command) + COLOR_NORMAL)  
    subprocess.run(command)

def main():
    # cli args
    parser = argparse.ArgumentParser(description="utility to compress large .mov screen captures into small .mp4 files",
                                     epilog="simplest example:\n    ffmpeg-mov2mp4.py -i screencap.mov",
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-i', '--input', required=True, help="input file path")
    parser.add_argument('-o', '--output', help="output file path (default: <input file>.mp4)")
    def bitrate_compression_level_type(arg):
        arg = arg.lower()
        levels = {'none': 0, 'low': 1, 'med': 2, 'high': 3}
        for key, value in levels.items():
            if key.startswith(arg):
                return value
        raise argparse.ArgumentTypeError(f"invalid compression level: {arg}")
    parser.add_argument('-c', '--bitrate-compression-level', type=bitrate_compression_level_type, default=0,
                        help="bitrate compression level: 'none' (default), 'low', 'med', 'high'")
    parser.add_argument('-s', '--skip', type=int, default=0, help="seconds to skip at start (default: 0)")
    parser.add_argument('-t', '--truncate', type=int, default=0, help="seconds to remove from end (default: 0)")
    args = parser.parse_args()

    # output file path defaults to input file path but with an .mp4 extension
    if args.output is None:
        if args.input.endswith('.mp4'):
            args.output = args.input[:-4] + '_1.mp4'
        else:
            args.output = args.input.rsplit('.', 1)[0] + '.mp4'
    
    # Check if ffmpeg and ffprobe are in the system path
    if shutil.which('ffmpeg') is None or shutil.which('ffprobe') is None:
        print("error: ffmpeg and ffprobe not found in path")
        sys.exit(1)

    # do the compression
    compress_video(args.input, args.output, args.bitrate_compression_level, trim_start=args.skip, trim_end=args.truncate)

if __name__ == "__main__":
    main()

