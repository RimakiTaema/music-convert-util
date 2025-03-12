#!/usr/bin/env python3

import os
import argparse
import subprocess
import sys
from colorama import init, Fore, Style

# Initialize colorama for cross-platform color support
init()

# Program information
PROGRAM_NAME = "ConvF Music"
VERSION = "1.0.0"
DESCRIPTION = "Universal audio format conversion utility"

# Common audio formats that FFmpeg supports
COMMON_AUDIO_FORMATS = [
    # Lossy formats
    ".mp3", ".aac", ".ogg", ".opus", ".m4a", ".wma", ".vorbis",
    # Lossless formats
    ".flac", ".wav", ".aiff", ".alac", ".ape", ".wv",
    # Other formats
    ".ac3", ".amr", ".au", ".mid", ".mka", ".ra", ".shn"
]

def print_banner():
    """Print a stylized banner for the program"""
    banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════╗
║ {Fore.GREEN}ConvF Music {VERSION}{Fore.CYAN}                      ║
║ {Fore.WHITE}Universal Audio Format Converter{Fore.CYAN}          ║
╚══════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)

def print_info(message):
    print(f"{Fore.BLUE}[INFO]{Style.RESET_ALL} {message}")

def print_warn(message):
    print(f"{Fore.YELLOW}[WARN]{Style.RESET_ALL} {message}")

def print_error(message):
    print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {message}")

def print_success(message):
    print(f"{Fore.GREEN}[SUCCESS]{Style.RESET_ALL} {message}")

def get_ffmpeg_formats():
    """Get a list of audio formats supported by the installed FFmpeg"""
    try:
        result = subprocess.run(
            ["ffmpeg", "-formats"],
            capture_output=True,
            text=True
        )
        return result.stdout
    except Exception:
        return None

def get_output_codec(output_format):
    """Get the appropriate codec for the output format"""
    format_codec_map = {
        ".mp3": ["-c:a", "libmp3lame", "-q:a", "4"],
        ".ogg": ["-c:a", "libvorbis", "-q:a", "5"],
        ".opus": ["-c:a", "libopus", "-b:a", "128k"],
        ".m4a": ["-c:a", "aac", "-b:a", "192k"],
        ".flac": ["-c:a", "flac"],
        ".wav": ["-c:a", "pcm_s16le"],
        ".aac": ["-c:a", "aac", "-b:a", "192k"],
        ".wma": ["-c:a", "wmav2", "-b:a", "192k"],
        ".alac": ["-c:a", "alac"],
    }
    
    # Return codec settings if found in the map, otherwise use the default codec for that format
    return format_codec_map.get(output_format.lower(), ["-c:a", "copy"])

def convert_file(input_file, output_file=None, quality=5, format=None):
    """Convert a single audio file to the specified format"""
    if not os.path.isfile(input_file):
        print_error(f"The file '{input_file}' does not exist.")
        return False
    
    # Determine output format based on parameters
    if format:
        output_format = f".{format.lower()}"
    elif output_file:
        output_format = os.path.splitext(output_file)[1].lower()
        if not output_format:
            print_error("No output format specified in output filename.")
            return False
    else:
        # Default to OGG if no format is specified
        output_format = ".ogg"
    
    # Determine output file name if not specified
    if output_file is None:
        output_file = os.path.splitext(input_file)[0] + output_format
    
    print_info(f"Converting: {os.path.basename(input_file)} → {os.path.basename(output_file)}")
    
    # Get codec settings for the output format
    codec_settings = get_output_codec(output_format)
    
    # Add quality parameter if applicable
    if "-q:a" in codec_settings and quality is not None:
        q_index = codec_settings.index("-q:a")
        if q_index + 1 < len(codec_settings):
            codec_settings[q_index + 1] = str(quality)
    
    # Build the ffmpeg command
    ffmpeg_cmd = ["ffmpeg", "-i", input_file]
    ffmpeg_cmd.extend(codec_settings)
    ffmpeg_cmd.append(output_file)
    
    # Run ffmpeg with capture_output to handle its logs
    try:
        # Use a progress indicator
        print(f"{Fore.CYAN}[PROCESSING]{Style.RESET_ALL} ", end="", flush=True)
        
        result = subprocess.run(
            ffmpeg_cmd,
            capture_output=True,
            text=True
        )
        
        # Check for any errors
        if result.returncode != 0:
            print(f"\r{' ' * 50}\r", end="")  # Clear progress line
            print_error(f"FFmpeg conversion failed for '{input_file}'")
            print_warn("FFmpeg error details:")
            for line in result.stderr.splitlines()[-5:]:  # Show last few lines of error
                print(f"  {line}")
            return False
        
        print(f"\r{' ' * 50}\r", end="")  # Clear progress line
        print_success(f"Successfully converted to {os.path.basename(output_file)}")
        return True
    except Exception as e:
        print(f"\r{' ' * 50}\r", end="")  # Clear progress line
        print_error(f"An error occurred: {str(e)}")
        return False

def convert_folder(folder_path, quality=5, format="ogg"):
    """Convert all audio files in a folder to the specified format"""
    if not os.path.isdir(folder_path):
        print_error(f"The folder '{folder_path}' does not exist.")
        return False
    
    output_format = f".{format.lower()}"
    
    # Get all audio files in the folder
    all_files = os.listdir(folder_path)
    audio_files = []
    
    # Check if file is likely an audio file (we'll let FFmpeg decide if it can convert it)
    for filename in all_files:
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext and (file_ext in COMMON_AUDIO_FORMATS or file_ext not in [".txt", ".jpg", ".png", ".pdf", ".doc", ".docx", ".exe", ".zip"]):
            audio_files.append(filename)
    
    total_files = len(audio_files)
    
    if total_files == 0:
        print_warn(f"No potential audio files found in '{folder_path}'.")
        return False
    
    print_info(f"Found {total_files} potential audio files to convert.")
    
    success_count = 0
    skip_count = 0
    fail_count = 0
    
    for i, filename in enumerate(audio_files):
        input_file = os.path.join(folder_path, filename)
        
        # Skip files that are already in the target format
        if filename.lower().endswith(output_format):
            print_info(f"[{i+1}/{total_files}] Skipping: {filename} (already in target format)")
            skip_count += 1
            continue
            
        output_file = os.path.join(folder_path, os.path.splitext(filename)[0] + output_format)
        
        # Calculate percentage for progress display
        percent = int((i / total_files) * 100)
        print_info(f"[{i+1}/{total_files}] ({percent}%) Processing: {filename}")
        
        if convert_file(input_file, output_file, quality, format):
            success_count += 1
        else:
            fail_count += 1
    
    # Print summary
    print()
    print(f"{Fore.CYAN}╔══════════════════════════════════════════╗")
    print(f"║ {Fore.WHITE}Conversion Summary{Fore.CYAN}                      ║")
    print(f"╠══════════════════════════════════════════╣")
    print(f"║ {Fore.WHITE}Total files:    {Fore.GREEN}{total_files:<5}{Fore.CYAN}                   ║")
    print(f"║ {Fore.WHITE}Converted:      {Fore.GREEN}{success_count:<5}{Fore.CYAN}                   ║")
    print(f"║ {Fore.WHITE}Skipped:        {Fore.YELLOW}{skip_count:<5}{Fore.CYAN}                   ║")
    print(f"║ {Fore.WHITE}Failed:         {Fore.RED}{fail_count:<5}{Fore.CYAN}                   ║")
    print(f"║ {Fore.WHITE}Success rate:   {Fore.GREEN}{int((success_count/(total_files-skip_count))*100) if (total_files-skip_count) > 0 else 0}%{Fore.CYAN}                     ║")
    print(f"╚══════════════════════════════════════════╝{Style.RESET_ALL}")
    
    return success_count > 0

def list_supported_formats():
    """List common audio formats supported by FFmpeg"""
    print(f"\n{Fore.CYAN}Commonly Supported Audio Formats:{Style.RESET_ALL}")
    formats = []
    for fmt in COMMON_AUDIO_FORMATS:
        formats.append(fmt.lstrip('.'))
    
    # Print in columns
    col_width = 8
    num_cols = 5
    for i in range(0, len(formats), num_cols):
        row = formats[i:i+num_cols]
        print("  " + "".join(f"{fmt:<{col_width}}" for fmt in row))
    
    print(f"\n{Fore.YELLOW}Note:{Style.RESET_ALL} Actual support depends on your FFmpeg installation.")
    print(f"For a complete list, run: {Fore.GREEN}ffmpeg -formats{Style.RESET_ALL}\n")

def main():
    # Print program banner
    print_banner()
    
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description=f"{PROGRAM_NAME} - {DESCRIPTION}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  # Convert a single file to OGG format (default)
  %(prog)s -f music.mp3
  
  # Convert a single file to MP3 format
  %(prog)s -f music.wav --format mp3
  
  # Convert all audio files in a directory to FLAC
  %(prog)s -d /path/to/music --format flac
  
  # Convert with specified output name
  %(prog)s -f input.wav -o output.mp3
  
  # List supported audio formats
  %(prog)s --list-formats
        """
    )
    
    # Create a mutually exclusive group for input type
    input_group = parser.add_mutually_exclusive_group(required=False)
    input_group.add_argument("-f", "--file", metavar="FILE", help="Convert a single audio file")
    input_group.add_argument("-d", "--directory", metavar="DIR", help="Convert all audio files in a directory")
    input_group.add_argument("--list-formats", action="store_true", help="List commonly supported audio formats")
    
    parser.add_argument("-o", "--output", metavar="OUTPUT", help="Output file name (only used with --file)")
    parser.add_argument("--format", metavar="FORMAT", default="ogg", 
                      help="Output format (e.g., mp3, flac, ogg, wav) (default: ogg)")
    parser.add_argument("-q", "--quality", type=int, default=5, choices=range(0, 11), 
                      help="Quality setting (0-10, default: 5, where applicable)")
    parser.add_argument("-v", "--version", action="version", 
                      version=f"{PROGRAM_NAME} v{VERSION}")
    
    args = parser.parse_args()
    
    # If no arguments or only help requested, show help
    if len(sys.argv) == 1:
        parser.print_help()
        return 0
    
    # Check if ffmpeg is installed
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
    except FileNotFoundError:
        print_error("FFmpeg is not installed or not in the system PATH.")
        print_info("Please install FFmpeg to use this converter: https://ffmpeg.org/download.html")
        return 1
    
    # List formats if requested
    if args.list_formats:
        list_supported_formats()
        return 0
    
    # Ensure at least one input option is specified
    if not args.file and not args.directory:
        print_error("No input specified. Use -f/--file or -d/--directory to specify input.")
        return 1
    
    # Process based on input type
    if args.file:
        if args.output and not os.path.splitext(args.output)[1]:
            # Add format extension to output if not present
            args.output = f"{args.output}.{args.format}"
        
        success = convert_file(args.file, args.output, args.quality, args.format)
        print()
        if success:
            print_success("File conversion completed successfully!")
        else:
            print_error("File conversion failed.")
    elif args.directory:
        success = convert_folder(args.directory, args.quality, args.format)
    
    return 0 if success else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n")
        print_info("Operation cancelled by user.")
        sys.exit(1)
