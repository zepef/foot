# System imports
import os
import numpy as np

# Streamlit UI/UX imports
import streamlit as st

# Audio/Vodeo imports
import moviepy.editor as mp
from pydub import AudioSegment
from pydub.utils import make_chunks
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

    for file in os.listdir(TEMPPATH):

        current_file = os.path.join(TEMPPATH, file)
        y, sr = librosa.load(current_file, sr=None, duration=300)
        S_full, phase = librosa.magphase(librosa.stft(y))
        S_filter = librosa.decompose.nn_filter(S_full, aggregate=np.median, metric='cosine', width=int(librosa.time_to_frames(2, sr=sr)))
        S_filter = np.minimum(S_full, S_filter)

        mask_v = librosa.util.softmask(S_full - S_filter, margin_v * S_filter, power=power)
        S_foreground = mask_v * S_full
        y_foreground = librosa.istft(S_foreground * phase)

        vocal_chunk_filename = current_file.replace('.wav', '')
        vocal_chunk_filename = f'{vocal_chunk_filename}_voc.wav'
        sf.write(vocal_chunk_filename, y_foreground, sr)


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
        msg = f'Slicing audio file for better processing, please be patient...'
        wav_msg_placeholder.text(msg)
        slice_wav_file(wav_filename, 5 * 60) # 5 minutes
        
        # extract vocals from audio file and save it to a wav file
        # display spectrogram of the audio file for pure fun
        msg = 'Extracting vocals from audio chunks, please be patient...'
        wav_msg_placeholder.text(msg)
        separate_vocals()
