import streamlit as st
import subprocess
import os

# Function to compress video
def compress_video(input_file_path, target_size_MB, output_file_path):
    # Duration of the video in seconds
    cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', input_file_path]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
    duration_seconds = float(result.stdout)

    # Calculate target total bitrate
    target_total_bitrate = (target_size_MB * 1024 * 1024 * 8 / duration_seconds) * 0.95

    # Audio bitrate
    audio_bitrate = 128000  # Consider a typical audio bitrate

    # Calculate target video bitrate
    video_bitrate = target_total_bitrate - audio_bitrate

    calculation_details = (
        f"Target Size (MB): {target_size_MB}\n"
        f"Video Duration (seconds): {duration_seconds:.2f}\n"
        f"Target Total Bitrate (with margin): {target_total_bitrate:.2f} bits/sec\n"
        f"Audio Bitrate: {audio_bitrate} bits/sec\n"
        f"Calculated Video Bitrate: {video_bitrate:.2f} bits/sec"
    )

    # Command to compress video
    cmd = [
        'ffmpeg',
        '-i', input_file_path,
        '-b:v', str(int(video_bitrate)),  # Set video bitrate
        '-b:a', str(audio_bitrate),  # Set audio bitrate
        '-y',  # Overwrite output file if it exists
        output_file_path
    ]

    subprocess.run(cmd, check=True)
    return calculation_details

# Streamlit UI
st.title('Video Compressor')

uploaded_file = st.file_uploader("Choose a video file", type=["mp4"])

if uploaded_file is not None:
    file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type}
    st.write(file_details)

    target_size_MB = st.number_input("Enter target size in MB", min_value=1, value=10)

    if st.button('Go'):
        # Save uploaded video to temporary file
        input_file_path = uploaded_file.name
        with open(input_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Ensure output directory exists
        output_dir = "Output"
        os.makedirs(output_dir, exist_ok=True)
        output_file_path = os.path.join(output_dir, f"compressed_{uploaded_file.name}")

        # Compress video
        calculation_details = compress_video(input_file_path, target_size_MB, output_file_path)
        
        # Show bitrate calculations and output file link
        st.text("Bitrate Calculations:")
        st.write(calculation_details)
        st.success(f"Compressed video saved as: {output_file_path}")
        st.download_button(label="Download Compressed Video", file_name=output_file_path, mime='video/mp4')
