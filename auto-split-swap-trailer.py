import subprocess
import glob
import os

#Created by Son Tran
def split_and_swap_video():
    # Find the source video file in the current directory with .mp4 or .mov extension
    video_files = glob.glob('./*.mp4') + glob.glob('./*.mov')

    if len(video_files) == 0:
        print("No video file found in the current directory.")
        return

    input_path = video_files[0]
    print("Source video file:", input_path)

    # Determine the file format
    file_format = input_path.split('.')[-1].lower()

    # Use FFmpeg to get the duration of the source video
    duration_output = subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', input_path])
    duration = float(duration_output)

    # Calculate the number of segments needed
    segment_duration = 10.0  # Duration of each segment in seconds
    num_segments = int(duration / segment_duration)

    # Split the source video into segments
    for i in range(num_segments):
        start_time = segment_duration * i
        segment_name = f'temp_{i:03d}.{file_format}'
        subprocess.call(['ffmpeg', '-ss', str(start_time), '-i', input_path, '-t', str(segment_duration), '-c:v', 'libx264', '-crf', '18', '-c:a', 'aac', '-strict', '-2', segment_name])

    # Get the list of video segments
    segments = sorted(glob.glob('temp_*.' + file_format))

    # Swap the order of the video segments
    swapped_segments = segments[::-1]

    # Generate the output file name
    output_file_name = os.path.splitext(input_path)[0] + "_output." + file_format

    # Use FFmpeg to concatenate the swapped video segments into a single video
    filter_string = ''.join(f"[{i}:v][{i}:a]" for i in range(len(swapped_segments)))
    concat_command = ['ffmpeg']
    for segment in swapped_segments:
        concat_command.extend(['-i', segment])
    concat_command.extend(['-filter_complex', f"{filter_string}concat=n={len(swapped_segments)}:v=1:a=1[outv][outa]", '-map', '[outv]', '-map', '[outa]', '-c:v', 'libx264', '-crf', '18', '-c:a', 'aac', '-strict', '-2', '-movflags', '+faststart', output_file_name])
    subprocess.call(concat_command)

    # Clean up temporary files
    for segment in swapped_segments:
        os.remove(segment)

    print("Video processing completed.")

# Example usage
split_and_swap_video()
