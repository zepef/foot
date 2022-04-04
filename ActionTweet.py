# Standard imports
import os
import numpy as np
import matplotlib.pyplot as plt

# Streamlit UI/UX imports
import streamlit as st

# Audio/Vodeo imports
import moviepy.editor as mp
from pydub import AudioSegment
from pydub.utils import make_chunks
from pydub.effects import normalize
import soundfile as sf
import librosa
import librosa.display

# get the current working directory
cwd = os.getcwd()

# define the audio, video and text path
AUDIOPATH = f'{cwd}/audio/'
VIDEOPATH = f'{cwd}/video/'
TEXTPATH = f'{cwd}/text/'
TEMPPATH = f'{cwd}/temp/'

def file_selector(video_extension: str) -> str:
    """ This is a file selector function which returns a file name string
        based upon a provided base path and a file extension ('.mp4' for example)

    Args:
        extension (str): file extension of the file type to be selected

    Returns:
        str: file name of the selected file of correct extension type
    """
    # fill a list of all files in a given directory
    all_filenames = os.listdir(VIDEOPATH)
    
    # filter the files list with the provided extension
    filtered_filenames = [filenames for filenames in all_filenames if video_extension in filenames]
    
    # input zone in Streamlit side bar
    selected_filename = st.sidebar.selectbox('Select an MP4 Soccer Video', filtered_filenames)
    
    # return the selected file name from the VIDEOPATH
    return selected_filename

def slice_wav_file(file_name: str, chunk_size: int) -> None:
    
    # load the audio file    
    audio_file = AudioSegment.from_file(AUDIOPATH + file_name)
    chunk_filename = wav_filename.replace('.wav', '')
    
    # split the audio file into chunks
    chunk_length_ms = chunk_size * 1000
    chunks = make_chunks(audio_file, chunk_length_ms)

    # loop over the chunks and export them to an individual file
    for i, chunk in enumerate(chunks): 
        chunk_name = f'{TEMPPATH}{chunk_filename}' + '_{0}.wav'.format(i)
        chunk.export(chunk_name, format='wav')
        
def separate_vocals() -> None:
    
    margin_v = 10
    power = 2
    
    for i, file in enumerate(os.listdir(TEMPPATH)):
        
        processed_chunk_placeholder = st.empty()
    
        col1, col2, col3 = st.columns(3)

        processed_chunk_placeholder.text(f'Processing {file} out of {len(os.listdir(TEMPPATH))} chunks')
        current_file = os.path.join(TEMPPATH, file)

        with col1:
            
            col1_title_placeholder = st.empty()
            col1_graph_placeholder = st.empty()
            
            y, sr = librosa.load(current_file, sr=None, duration=300)
            S_full, phase = librosa.magphase(librosa.stft(y))
            S_filter = librosa.decompose.nn_filter(S_full, aggregate=np.median, metric='cosine', width=int(librosa.time_to_frames(2, sr=sr)))
            S_filter = np.minimum(S_full, S_filter)

            idx = slice(*librosa.time_to_frames([10, 15], sr=sr))
            fig, ax = plt.subplots()
            img = librosa.display.specshow(librosa.amplitude_to_db(S_full[:, idx], ref=np.max),
                                            y_axis='log', x_axis='time', sr=sr, ax=ax)
            fig.colorbar(img, ax=ax)
            col1_title_placeholder.text("Original chunk")
            col1_graph_placeholder.pyplot(fig)

        with col2:

            col2_title_placeholder = st.empty()
            col2_graph_placeholder = st.empty()

            mask_v = librosa.util.softmask(S_full - S_filter, margin_v * S_filter, power=power)
            S_foreground = mask_v * S_full
            y_foreground = librosa.istft(S_foreground * phase)
            
            idx = slice(*librosa.time_to_frames([10, 15], sr=sr))
            fig, ax = plt.subplots()
            img = librosa.display.specshow(librosa.amplitude_to_db(S_foreground[:, idx], ref=np.max),
                                    y_axis='log', x_axis='time', sr=sr, ax=ax)            
            fig.colorbar(img, ax=ax)
            col2_title_placeholder.text("Vocals only")
            col2_graph_placeholder.pyplot(fig)
            
        with col3:            
            
            col3_title_placeholder = st.empty()
            col3_graph_placeholder = st.empty()
            
            normalized_chunk = strip_silence(S_foreground)
            
            idx = slice(*librosa.time_to_frames([10, 15], sr=sr))
            fig, ax = plt.subplots()
            img = librosa.display.specshow(librosa.amplitude_to_db(normalized_chunk[:, idx], ref=np.max),
                                    y_axis='log', x_axis='time', sr=sr, ax=ax)            
            fig.colorbar(img, ax=ax)
            col3_title_placeholder.text("Vocals only")
            col3_graph_placeholder.pyplot(fig)
            
            col3_title_placeholder.text("Enhanced vocals")
            
        split_filename = file.split("_", 1)
        vocal_chunk_filename = f'{split_filename[0]}_voc{i}.wav'
        vocal_chunk_filename = os.path.join(TEMPPATH, vocal_chunk_filename)

        sf.write(vocal_chunk_filename, S_foreground, sr)

def recombine_audiofile(filename: str) -> None:
    pass

def suppress_long_silences(filename: str) -> None:
    pass
        
if __name__ == '__main__':
    
    # global configuration of the Streamlit app
    st.set_page_config(
        page_title="SA TweetBot",
        page_icon="🧊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.title('Welcome to the Soccer Actions Tweet Bot')
    st.write('an open source streamlit app by pef@knowledge-worker.ai ')

    # select the soccer video file
    mp4_filename = file_selector('.mp4')

    # starting the text extraction process
    if st.sidebar.button('Click to extract text from video'):
        
        # create a moviepy media container the selected video file
        clip = mp.VideoFileClip(VIDEOPATH + mp4_filename)

        # compute the video file size in MB
        mp4_file_size = os.path.getsize(VIDEOPATH + mp4_filename) // 1024 // 1024

        # extract audio from the video and save it to a wav file
        wav_filename = mp4_filename.replace('.mp4', '.wav')
        wav_msg_placeholder = st.empty()
        msg = f'Extracting audio from {mp4_file_size} MB video, please be patient...'
        wav_msg_placeholder.text(msg)
        #clip.audio.write_audiofile(AUDIOPATH + wav_filename)

        # slice large audio file into 5 minutes chunks for easier processing
        msg = 'Slicing audio file for better processing, please be patient...'
        wav_msg_placeholder.text(msg)
        #slice_wav_file(wav_filename, 5 * 60) # 5 minutes

        # extract vocals from audio file and save it to a wav file
        # display spectrogram of the audio file for pure fun
        msg = 'Extracting vocals from audio chunks, please be patient...'
        wav_msg_placeholder.text(msg)
        separate_vocals()
