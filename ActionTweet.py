import os
import moviepy.editor as mp
import streamlit as st

def file_selector(folder_path='.'):
    all_filenames = os.listdir(folder_path)
    mp4_filenames = [filenames for filenames in all_filenames if '.mp4' in filenames]
    selected_filename = st.sidebar.selectbox('Select a Soccer Video', mp4_filenames)
    return os.path.join(folder_path, selected_filename)

mp4_filename = file_selector()
if st.sidebar.button('Click to Convert MP4 to WAV'):
    clip = mp.VideoFileClip(mp4_filename)

    mp4_file_size = os.path.getsize(mp4_filename)
    mp4_file_size = mp4_file_size // 1024 // 1024

    wav_filename = mp4_filename.replace('.mp4', '.wav')
    wav_msg_placeholder = st.sidebar.empty()
    msg = f'Extracting audio from {mp4_file_size} MB video,\nplease be patient...'
    wav_msg_placeholder.text(msg)

    clip.audio.write_audiofile(wav_filename)

    msg = f'Audio Wave extracted to:\n{wav_filename}'
    wav_msg_placeholder.text(msg)